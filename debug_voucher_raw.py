import pandas as pd
from dbfread import DBF

def dump_raw():
    folder = "jwerp/1001"
    
    tran_table = DBF(f"{folder}/TRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
    df_tran = pd.DataFrame(iter(tran_table))
    df_tran['TRNID'] = pd.to_numeric(df_tran['TRNID'], errors='coerce')
    header = df_tran[df_tran['TRNID'] == 212]
    
    if header.empty:
        print("Header not found")
        return
        
    print("=== HEADER ===")
    for k, v in header.iloc[0].to_dict().items():
        if pd.notnull(v) and v != '' and v != 0:
            print(f"{k}: {v}")
            
    itran_table = DBF(f"{folder}/ITRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
    df_itran = pd.DataFrame(iter(itran_table))
    df_itran['TRNID'] = pd.to_numeric(df_itran['TRNID'], errors='coerce')
    items = df_itran[df_itran['TRNID'] == 212]
    
    print("\n=== ITEMS ===")
    for i, (_, row) in enumerate(items.iterrows()):
        print(f"--- Item {i+1} ---")
        for k, v in row.to_dict().items():
            if pd.notnull(v) and v != '' and v != 0:
                print(f"{k}: {v}")

dump_raw()
