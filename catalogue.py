import os
import pandas as pd
from dbfread import DBF
from collections import defaultdict

tables = {}

print("Loading tables...\n")

# -----------------------------
# Load all DBF files
# -----------------------------
for file in os.listdir("."):
    if file.lower().endswith(".dbf"):
        try:
            table_name = os.path.splitext(file)[0].upper()

            df = pd.DataFrame(iter(DBF(file, load=True, ignore_missing_memofile=True)))

            df.columns = [c.upper() for c in df.columns]

            tables[table_name] = df

            print(f"Loaded {table_name} ({len(df):,} rows, {len(df.columns)} cols)")

        except Exception as e:
            print(f"Failed to load {file}: {e}")

print(f"\nLoaded {len(tables)} tables")

# -----------------------------
# Catalog
# -----------------------------
catalog = []

for table_name, df in tables.items():
    catalog.append(
        {
            "TABLE": table_name,
            "ROWS": len(df),
            "COLUMNS": len(df.columns),
            "COLUMN_NAMES": ", ".join(df.columns),
        }
    )

catalog_df = pd.DataFrame(catalog)

catalog_df.sort_values(by="ROWS", ascending=False).to_csv(
    "database_catalog.csv", index=False
)

print("Saved database_catalog.csv")

# -----------------------------
# Database Discovery
# -----------------------------

inventory_keywords = ["ITEM", "PRODUCT", "STOCK", "QTY", "QUANTITY", "SKU", "PART"]

customer_keywords = ["CUSTOMER", "CLIENT", "CUST"]

sales_keywords = ["SALE", "INVOICE", "ORDER", "TRANSACTION"]

vendor_keywords = ["VENDOR", "SUPPLIER"]

accounting_keywords = ["ACCOUNT", "LEDGER", "GL", "AR", "AP"]

inventory_tables = []
customer_tables = []
sales_tables = []
vendor_tables = []
accounting_tables = []

all_columns = defaultdict(list)

for table_name, df in tables.items():
    table_upper = table_name.upper()

    cols = [c.upper() for c in df.columns]

    # relationship discovery
    for col in cols:
        all_columns[col].append(table_name)

    text = table_upper + " " + " ".join(cols)

    if any(k in text for k in inventory_keywords):
        inventory_tables.append(table_name)

    if any(k in text for k in customer_keywords):
        customer_tables.append(table_name)

    if any(k in text for k in sales_keywords):
        sales_tables.append(table_name)

    if any(k in text for k in vendor_keywords):
        vendor_tables.append(table_name)

    if any(k in text for k in accounting_keywords):
        accounting_tables.append(table_name)

# -----------------------------
# Largest Tables
# -----------------------------
largest_tables = sorted(tables.items(), key=lambda x: len(x[1]), reverse=True)[:20]

# -----------------------------
# Common Columns
# -----------------------------
relationships = {col: tbls for col, tbls in all_columns.items() if len(tbls) >= 2}

# -----------------------------
# Report
# -----------------------------
report = []

report.append("FOXPRO DATABASE DISCOVERY REPORT")
report.append("=" * 60)

report.append(f"\nTotal Tables: {len(tables)}")
report.append(f"Total Rows: {sum(len(df) for df in tables.values()):,}")

report.append("\nLARGEST TABLES")
report.append("-" * 60)

for table_name, df in largest_tables:
    report.append(f"{table_name:<30} {len(df):>12,} rows")

report.append("\nLIKELY INVENTORY TABLES")
report.append("-" * 60)
report.extend(sorted(set(inventory_tables)))

report.append("\nLIKELY CUSTOMER TABLES")
report.append("-" * 60)
report.extend(sorted(set(customer_tables)))

report.append("\nLIKELY SALES TABLES")
report.append("-" * 60)
report.extend(sorted(set(sales_tables)))

report.append("\nLIKELY VENDOR TABLES")
report.append("-" * 60)
report.extend(sorted(set(vendor_tables)))

report.append("\nLIKELY ACCOUNTING TABLES")
report.append("-" * 60)
report.extend(sorted(set(accounting_tables)))

report.append("\nPOTENTIAL RELATIONSHIPS")
report.append("-" * 60)

for col, tbls in sorted(relationships.items(), key=lambda x: len(x[1]), reverse=True):
    if len(tbls) >= 3:
        report.append(f"{col}: {', '.join(tbls[:10])}")

with open("database_discovery_report.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(report))

print("Saved database_discovery_report.txt")
