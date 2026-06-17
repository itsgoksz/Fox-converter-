financial_keywords = [
    "SALE",
    "PURCHASE",
    "LEDGER",
    "ACCOUNT",
    "TRANSACTION",
    "INVOICE",
    "PAYMENT",
    "RECEIPT",
    "ITEM",
    "STOCK",
    "INVENTORY",
]

for table_name, df in tables.items():
    matches = []

    for col in df.columns:
        for keyword in financial_keywords:
            if keyword in col.upper():
                matches.append(col)

    if matches:
        print("\n" + "=" * 80)
        print(table_name)
        print(matches)
