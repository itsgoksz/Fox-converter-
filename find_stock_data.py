from dbfread import DBF

def inspect_file(filename):
    try:
        table = DBF(filename, load=False, ignore_missing_memofile=True, char_decode_errors='ignore')
        cols = [f.name for f in table.fields]
        print(f"\nFile: {filename}")
        print(f"Columns: {', '.join(cols)}")
    except Exception as e:
        pass

inspect_file("jwerp/1001/itstd1.db")
inspect_file("jwerp/1001/clstk1.db")
inspect_file("jwerp/1001/tgm1.db")
