import re

def clean_table_name(symbol: str) -> str:
    return re.sub(r'\W+', '_', symbol.replace("&", "_and_")).lower()
