from dbfread import DBF
import pandas as pd

table = DBF("jwerp/1001/formprn.db", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))

# Find any form that contains the column headers from the screenshot
matches = df[df['DISPNAME'].astype(str).str.contains("Dia Wt|Stn Wt|Net Wt|Gr\.Wt", case=False, na=False)]

print("--- Forms containing the Stock Headers ---")
unique_forms = matches['FORMNAME'].unique()
for form in unique_forms:
    print(f"Match Found in Form: {form}")
    
    # Let's print the actual columns for this form to verify
    cols = df[df['FORMNAME'] == form].sort_values(by='SRNO')
    col_names = cols['DISPNAME'].tolist()
    print(f"Columns in this grid: {', '.join([str(c) for c in col_names if c])}\n")

