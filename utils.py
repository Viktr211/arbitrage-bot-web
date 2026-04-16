# utils.py
from datetime import datetime

def format_trade(asset, profit, buy_ex, sell_ex):
    return f"✅ {datetime.now().strftime('%H:%M:%S')} | {asset} | Куплен на {buy_ex.upper()} | Продан на {sell_ex.upper()} | +{profit:.2f} USDT"
