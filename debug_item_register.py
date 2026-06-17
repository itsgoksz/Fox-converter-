import sys
import traceback
sys.path.append('.')
from backend.main import get_item_register

try:
    get_item_register("2025-04-01", "2026-03-31", "SALE", "SILVER JEWELLERY")
except Exception as e:
    traceback.print_exc()
