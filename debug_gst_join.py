from dbfread import DBF
import pandas as pd

# Check VTYPE mapping for SALE LOCAL RD
try:
    v_table = DBF("jwerp/1001/vtype.db", load=False, ignore_missing_memofile=True, char_decode_errors='ignore')
    df_v = pd.DataFrame(iter(v_table))
    print("--- VTYPE Mapping ---")
    print(df_v[df_v['VTYPECODE'] == 21][['VTYPECODE', 'VTYPE', 'VNAME', 'PNAME']])
except Exception as e:
    print(e)

# Check ITRAN1.DB for the weight for TRNID = 68
try:
    i_table = DBF("jwerp/1001/ITRAN1.DB", load=False, ignore_missing_memofile=True, char_decode_errors='ignore')
    df_i = pd.DataFrame(iter(i_table))
    print("\n--- ITRAN1.DB Weight Mapping ---")
    sample_items = df_i[df_i['TRNID'] == 68]
    print(f"Items found for TRNID=68: {len(sample_items)}")
    if len(sample_items) > 0:
        print(f"Total WT for TRNID=68: {sample_items['WT'].sum()}")
except Exception as e:
    print(e)

