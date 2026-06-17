import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from main import get_vat_data

df = get_vat_data("2025-01-01", "2025-01-31")
print("df length:", len(df))
if not df.empty:
    print(df['VTYPE'].head())
