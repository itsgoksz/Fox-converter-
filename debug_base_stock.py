import sys
sys.path.append('.')
from backend.main import get_base_stock_data
import pandas as pd

df = get_base_stock_data('2026-03-31', '2026-03-31')
print(f"Dataframe length: {len(df)}")
if not df.empty:
    print(df[['VTYPE', 'DIR', 'ITEM_NAME']].head())
