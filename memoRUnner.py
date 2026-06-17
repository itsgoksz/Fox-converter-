frt = "/Users/gokulgautham/Downloads/jwerp/_gstinv.FRT"

with open(frt, "rb") as f:
    data = f.read()

print("FRT Size:", len(data))

strings = []
current = bytearray()

for b in data:
    if 32 <= b <= 126:
        current.append(b)
    else:
        if len(current) >= 4:
            strings.append(current.decode("ascii", errors="ignore"))
        current = bytearray()

print("\nFOUND STRINGS:\n")

for s in strings[:1000]:
    print(s)
