import datetime
import pandas as pd
from sale_tax_register import load_and_pivot_sale_register

df = load_and_pivot_sale_register(datetime.date(2025, 4, 1), datetime.date(2026, 3, 31))
print("\n--- FINAL GRID ---")
print(df[['Month', 'Retail Sale', 'Tax Invoice', 'Total', 'Central Sale', 'Net Amount']].head(6))

