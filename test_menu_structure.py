from dbfread import DBF

def inspect_db(filename):
    print(f"\n--- Structure for {filename} ---")
    try:
        table = DBF(filename, load=False, ignore_missing_memofile=True)
        print("SUCCESS! Valid DBF.")
        print(f"Columns ({len(table.fields)}):")
        print(", ".join([field.name for field in table.fields]))
    except Exception as e:
        print(f"Failed: {e}")

inspect_db("jwerp/1001/mnu.db")
