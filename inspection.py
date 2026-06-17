from dbfread import DBF

table = DBF(
    "/Users/gokulgautham/Downloads/jwerp/_gstinv.frx",
    load=False,
    ignore_missing_memofile=True,
)

print("Filename:", table.filename)

print("\nFields:")
for field in table.fields:
    print(field.name, field.type, field.length, field.decimal_count)
