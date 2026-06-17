import sys
sys.path.append('.')
from backend.main import get_voucher_details
import traceback

def call_api():
    try:
        from fastapi import Query
        # We need to simulate how FastAPI calls it, but we can just import the code directly and bypass the try/except
        import backend.main
        # Re-define without try/except
        import pandas as pd
        from dbfread import DBF
        import os
        
        trn_id = "212"
        trn_id_num = float(trn_id)
        
        folder = "jwerp/1001"
        tran_path = os.path.join(folder, "TRAN1.DB")
        itran_path = os.path.join(folder, "ITRAN1.DB")
        acc_path = os.path.join(folder, "ACCMAST.DB")
        item_path = os.path.join(folder, "ITEMMAST.DB")
        
        tran_table = DBF(tran_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
        df_tran = pd.DataFrame(iter(tran_table))
        df_tran.columns = [str(c).upper() for c in df_tran.columns]
        df_tran['TRNID'] = pd.to_numeric(df_tran['TRNID'], errors='coerce')
        header_df = df_tran[df_tran['TRNID'] == trn_id_num]
        
        header_row = header_df.iloc[0].to_dict()
        
        acc_table = DBF(acc_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
        df_acc = pd.DataFrame(iter(acc_table))
        df_acc.columns = [str(c).upper() for c in df_acc.columns]
        df_acc['ACNO'] = pd.to_numeric(df_acc['ACNO'], errors='coerce')
        
        party_name = ""
        address = ""
        gstin = ""
        state = ""
        
        if pd.notnull(header_row.get('ACNO')):
            acc_match = df_acc[df_acc['ACNO'] == header_row['ACNO']]
            if not acc_match.empty:
                acc_r = acc_match.iloc[0]
                party_name = str(acc_r.get('CNAME', ''))
                address = f"{str(acc_r.get('ADD1', ''))} {str(acc_r.get('ADD2', ''))}".strip()
                gstin = str(acc_r.get('GSTIN', ''))
                state = str(acc_r.get('STATEID', ''))
                
        header_data = {
            'Party_Name': party_name,
            'Address': address,
            'GSTIN': gstin,
            'State': state,
            'Series': str(header_row.get('VTYPE', '')),
            'Date': pd.to_datetime(header_row.get('TDATE')).strftime('%d/%m/%Y') if pd.notnull(header_row.get('TDATE')) else "",
            'Vou_No': str(header_row.get('VONO', '')),
            'Bill_No': str(header_row.get('BILLNO', '')),
            'Total_Sale': abs(float(header_row.get('AMOUNT', 0))),
            'SGST': abs(float(header_row.get('SGST', 0))),
            'CGST': abs(float(header_row.get('CGST', 0))),
            'IGST': abs(float(header_row.get('IGST', 0)))
        }
        
        itran_table = DBF(itran_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
        df_itran = pd.DataFrame(iter(itran_table))
        df_itran.columns = [str(c).upper() for c in df_itran.columns]
        df_itran['TRNID'] = pd.to_numeric(df_itran['TRNID'], errors='coerce')
        items_df = df_itran[df_itran['TRNID'] == trn_id_num]
        
        item_table = DBF(item_path, load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
        df_item = pd.DataFrame(iter(item_table))
        df_item.columns = [str(c).upper() for c in df_item.columns]
        df_item['INO'] = pd.to_numeric(df_item['INO'], errors='coerce')
        
        items_list = []
        for _, r in items_df.iterrows():
            item_name = ""
            if pd.notnull(r.get('INO')):
                i_match = df_item[df_item['INO'] == pd.to_numeric(r['INO'])]
                if not i_match.empty:
                    item_name = str(i_match.iloc[0].get('PNAME', ''))
                    
            items_list.append({
                'Type': str(r.get('TYPE', '')),
                'Tag_No': str(r.get('TGNO', '')),
                'Item_Name': item_name,
                'Stamp': str(r.get('BATCH', '')),
                'Remarks': str(r.get('REMARKS', '')),
                'Unit': str(r.get('RATEUNIT', '')),
                'Pc': float(r.get('PC', 0)),
                'Weight': float(r.get('WT', 0)),
                'Less': float(r.get('LESSWT', 0)) if 'LESSWT' in r else 0,
                'Net_Wt': float(r.get('NWT', 0)) if 'NWT' in r else float(r.get('WT', 0)),
                'Tunch': float(r.get('PURTUNCH', 0)) if 'PURTUNCH' in r else 0,
                'Fine': float(r.get('FINE', 0)) if 'FINE' in r else 0,
                'Rate': float(r.get('RATE', 0)),
                'Amount': abs(float(r.get('AMOUNT', 0))),
                'Dia_Wt': float(r.get('DIAWT', 0)) if 'DIAWT' in r else 0,
                'Stn_Wt': float(r.get('STNWT', 0)) if 'STNWT' in r else 0,
                'Lbr': float(r.get('LABOUR', 0)) if 'LABOUR' in r else 0
            })
            
        print("Success")
    except Exception as e:
        traceback.print_exc()

call_api()
