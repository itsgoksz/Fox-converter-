from dbfread import DBF
import pandas as pd
import os

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", 500)

frx_files = [
    r"/Users/gokulgautham/Downloads/jwerp/_gstinv.frx",
]

for frx in frx_files:
    print("\n" + "=" * 120)
    print("REPORT:", os.path.basename(frx))
    print("=" * 120)

    try:
        # =====================================================
        # LOAD FRX
        # =====================================================

        df = pd.DataFrame(list(DBF(frx, load=True, ignore_missing_memofile=False)))

        print(f"\nRows: {len(df)}")
        print(f"Columns: {len(df.columns)}")

        print("\nFIELD NAMES")
        print("-" * 120)
        print(df.columns.tolist())

        # =====================================================
        # OBJECT TYPES
        # =====================================================

        if "OBJTYPE" in df.columns:
            print("\nOBJECT TYPES")
            print("-" * 120)
            print(df["OBJTYPE"].value_counts())

        # =====================================================
        # OBJTYPE + OBJCODE MATRIX
        # =====================================================

        if "OBJTYPE" in df.columns and "OBJCODE" in df.columns:
            print("\nOBJTYPE / OBJCODE COMBINATIONS")
            print("-" * 120)

            combo = (
                df.groupby(["OBJTYPE", "OBJCODE"])
                .size()
                .reset_index(name="COUNT")
                .sort_values("COUNT", ascending=False)
            )

            print(combo.to_string(index=False))

        # =====================================================
        # FIRST 50 REPORT OBJECTS
        # =====================================================

        interesting_cols = [
            "OBJTYPE",
            "OBJCODE",
            "NAME",
            "EXPR",
            "COMMENT",
            "TAG",
            "TAG2",
            "USER",
            "VPOS",
            "HPOS",
            "HEIGHT",
            "WIDTH",
        ]

        existing_cols = [c for c in interesting_cols if c in df.columns]

        print("\nFIRST 50 OBJECTS")
        print("-" * 120)

        print(df[existing_cols].head(50).to_string())

        # =====================================================
        # SCAN EVERY TEXT COLUMN
        # =====================================================

        print("\nTEXT VALUES DISCOVERY")
        print("-" * 120)

        for col in df.columns:
            try:
                if df[col].dtype == object:
                    vals = df[col].dropna().astype(str).unique()

                    useful = []

                    for v in vals:
                        v = str(v).strip()

                        if len(v) > 0 and v.lower() != "none" and v.lower() != "nan":
                            useful.append(v)

                    if useful:
                        print("\n" + "=" * 80)
                        print("COLUMN:", col)
                        print("=" * 80)

                        for v in useful[:50]:
                            print(v)

            except Exception as e:
                pass

        # =====================================================
        # SAVE RAW CSV
        # =====================================================

        csv_name = os.path.basename(frx) + "_dump.csv"

        df.to_csv(csv_name, index=False)

        print(f"\nSaved CSV dump: {csv_name}")

        # =====================================================
        # RAW RECORD INSPECTION
        # =====================================================

        print("\nRAW RECORD INSPECTION")
        print("-" * 120)

        table = DBF(frx, load=False, ignore_missing_memofile=False)

        for i, record in enumerate(table):
            print(f"\nRecord #{i}")
            print(record)

            if i >= 5:
                break

    except Exception as e:
        print("ERROR:", e)
