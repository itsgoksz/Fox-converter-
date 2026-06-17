import os
import pandas as pd
from dbfread import DBF
from collections import defaultdict

# =====================================================
# LOAD ALL DBF FILES
# =====================================================

tables = {}

print("Loading DBF files...\n")

for file in os.listdir("."):
    if file.lower().endswith(".dbf"):
        try:
            table_name = os.path.splitext(file)[0].upper()

            df = pd.DataFrame(iter(DBF(file, load=True, ignore_missing_memofile=True)))

            df.columns = [c.upper() for c in df.columns]

            tables[table_name] = df

            print(
                f"Loaded {table_name:<30} Rows={len(df):>8,} Cols={len(df.columns):>3}"
            )

        except Exception as e:
            print(f"Failed to load {file}: {e}")

print(f"\nLoaded {len(tables)} tables")

# =====================================================
# STEP 1 - FIND CANDIDATE KEYS
# =====================================================

print("\nFinding candidate keys...")

candidate_keys = {}

for table_name, df in tables.items():
    keys = []

    for col in df.columns:
        try:
            unique_count = df[col].nunique(dropna=True)

            if unique_count == len(df) and unique_count > 0:
                keys.append(col)

        except:
            pass

    candidate_keys[table_name] = keys

# =====================================================
# STEP 2 - FIND SHARED COLUMN NAMES
# =====================================================

print("Finding shared columns...")

column_usage = defaultdict(list)

for table_name, df in tables.items():
    for col in df.columns:
        column_usage[col].append(table_name)

shared_columns = {col: tbls for col, tbls in column_usage.items() if len(tbls) > 1}

# =====================================================
# STEP 3 - VERIFY RELATIONSHIPS
# =====================================================

print("Testing value overlap...")

relationships = []

for column_name, table_list in shared_columns.items():
    if len(table_list) < 2:
        continue

    for i in range(len(table_list)):
        for j in range(i + 1, len(table_list)):
            table_a = table_list[i]
            table_b = table_list[j]

            try:
                values_a = set(tables[table_a][column_name].dropna().astype(str))

                values_b = set(tables[table_b][column_name].dropna().astype(str))

                if not values_a or not values_b:
                    continue

                overlap = values_a.intersection(values_b)

                overlap_count = len(overlap)

                if overlap_count > 0:
                    pct_a = (overlap_count / len(values_a)) * 100

                    pct_b = (overlap_count / len(values_b)) * 100

                    relationships.append(
                        {
                            "COLUMN": column_name,
                            "TABLE_A": table_a,
                            "TABLE_B": table_b,
                            "OVERLAP_COUNT": overlap_count,
                            "A_MATCH_PCT": round(pct_a, 2),
                            "B_MATCH_PCT": round(pct_b, 2),
                        }
                    )

            except:
                pass

# =====================================================
# STEP 4 - CREATE CSV REPORTS
# =====================================================

print("Saving reports...")

# Table Catalog
catalog_rows = []

for table_name, df in tables.items():
    catalog_rows.append(
        {
            "TABLE": table_name,
            "ROWS": len(df),
            "COLUMNS": len(df.columns),
            "COLUMN_NAMES": ", ".join(df.columns),
        }
    )

catalog_df = pd.DataFrame(catalog_rows)

catalog_df.sort_values(by="ROWS", ascending=False).to_csv(
    "database_catalog.csv", index=False
)

# Candidate Keys
key_rows = []

for table_name, keys in candidate_keys.items():
    for key in keys:
        key_rows.append({"TABLE": table_name, "POSSIBLE_KEY": key})

pd.DataFrame(key_rows).to_csv("candidate_keys.csv", index=False)

# Relationships
relationship_df = pd.DataFrame(relationships)

if not relationship_df.empty:
    relationship_df.sort_values(by="OVERLAP_COUNT", ascending=False).to_csv(
        "relationship_report.csv", index=False
    )

# =====================================================
# STEP 5 - HUMAN READABLE REPORT
# =====================================================

report = []

report.append("FOXPRO DATABASE DISCOVERY REPORT")
report.append("=" * 80)

report.append("")
report.append(f"Tables Loaded : {len(tables)}")
report.append(f"Total Rows    : {sum(len(df) for df in tables.values()):,}")

report.append("")
report.append("LARGEST TABLES")
report.append("-" * 80)

largest = sorted(tables.items(), key=lambda x: len(x[1]), reverse=True)[:20]

for table_name, df in largest:
    report.append(f"{table_name:<35}{len(df):>12,} rows")

report.append("")
report.append("CANDIDATE PRIMARY KEYS")
report.append("-" * 80)

for table_name, keys in candidate_keys.items():
    if keys:
        report.append(f"{table_name}: {', '.join(keys)}")

report.append("")
report.append("TOP RELATIONSHIPS")
report.append("-" * 80)

if relationships:
    sorted_rels = sorted(relationships, key=lambda x: x["OVERLAP_COUNT"], reverse=True)[
        :100
    ]

    for rel in sorted_rels:
        report.append(
            f"{rel['TABLE_A']}.{rel['COLUMN']} "
            f"<-> "
            f"{rel['TABLE_B']}.{rel['COLUMN']} "
            f" | Matches={rel['OVERLAP_COUNT']} "
            f" | A={rel['A_MATCH_PCT']}% "
            f" | B={rel['B_MATCH_PCT']}%"
        )

with open("database_discovery_report.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(report))

print("\nGenerated:")
print("  database_catalog.csv")
print("  candidate_keys.csv")
print("  relationship_report.csv")
print("  database_discovery_report.txt")
print("\nDone.")
