import sys
sys.path.append('.')
from backend.main import DBF
import pandas as pd
table = DBF("jwerp/1001/ITRAN1.DB", load=True, ignore_missing_memofile=True, char_decode_errors='ignore')
df = pd.DataFrame(iter(table))
print([str(c).upper() for c in df.columns])
