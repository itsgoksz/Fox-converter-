from dbfread import DBF
import pandas as pd

# 1. Find the Menu Command
mnu = pd.DataFrame(iter(DBF("jwerp/1001/mnu.db", ignore_missing_memofile=True, char_decode_errors='ignore')))
in_hand = mnu[mnu['MNUCAP'].astype(str).str.contains("In Hand", case=False, na=False)]

print("--- Menu Commands for 'In Hand' ---")
for _, row in in_hand.iterrows():
    print(f"Caption: {row['MNUCAP']} | Command: {row.get('CMD')}")

# 2. Find Form Blueprints related to Stock
formmst = pd.DataFrame(iter(DBF("jwerp/1001/formmst.db", ignore_missing_memofile=True, char_decode_errors='ignore')))
stock_forms = formmst[formmst['FORMNAME'].astype(str).str.contains("STOCK|STATUS|INHAND|HAND", case=False, na=False)]

print("\n--- Available Stock Forms in formmst.db ---")
for _, row in stock_forms.iterrows():
    print(f"Form ID: {row['FORMID']} | Form Name: {row['FORMNAME']}")

