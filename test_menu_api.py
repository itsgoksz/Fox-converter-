from dbfread import DBF
import pandas as pd
import json

def get_menu_tree():
    try:
        table = DBF("jwerp/1001/mnu.db", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
        df = pd.DataFrame(iter(table))
        
        df['MNUCAP'] = df['MNUCAP'].astype(str).str.strip().str.replace(r'[\&\<]', '', regex=True)
        if 'MNUORDER' in df.columns:
            df['MNUORDER'] = pd.to_numeric(df['MNUORDER'], errors='coerce').fillna(0)
        if 'HIDE' in df.columns:
            df = df[df['HIDE'] != True]
            df = df[df['HIDE'] != 'T']
            
        tree = []
        main_menus = df[df['SMNO1'] == 0].sort_values('MNUORDER')
        for _, main_row in main_menus.iterrows():
            mno = main_row['MNO']
            main_item = {
                "id": str(main_row['MNUID']).strip(),
                "label": main_row['MNUCAP'],
                "children": []
            }
            
            sub1_items = df[(df['MNO'] == mno) & (df['SMNO1'] > 0) & (df['SMNO2'] == 0)].sort_values('MNUORDER')
            for _, sub1_row in sub1_items.iterrows():
                smno1 = sub1_row['SMNO1']
                sub1_item = {
                    "id": str(sub1_row['MNUID']).strip(),
                    "label": sub1_row['MNUCAP'],
                    "children": []
                }
                
                sub2_items = df[(df['MNO'] == mno) & (df['SMNO1'] == smno1) & (df['SMNO2'] > 0)].sort_values('MNUORDER')
                for _, sub2_row in sub2_items.iterrows():
                    sub2_item = {
                        "id": str(sub2_row['MNUID']).strip(),
                        "label": sub2_row['MNUCAP'],
                        "cmd": str(sub2_row.get('CMD', '')).strip()
                    }
                    sub1_item["children"].append(sub2_item)
                    
                if not sub1_item["children"]:
                    sub1_item["cmd"] = str(sub1_row.get('CMD', '')).strip()
                    
                main_item["children"].append(sub1_item)
                
            tree.append(main_item)
            
        return tree
    except Exception as e:
        return str(e)

print(json.dumps(get_menu_tree(), indent=2)[:500])
