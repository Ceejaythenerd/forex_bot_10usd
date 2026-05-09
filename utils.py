import logging
from datetime import datetime

def setup_logger(name):
    logging.basicConfig(
        filename='bot.log',
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s'
    )
    return logging.getLogger(name)

def pip_value(pair, lot_size=0.01):
    if 'XAU' in pair:
        return 0.1 * (lot_size / 0.01)
    if 'JPY' in pair:
        return 1000 * lot_size
    return 10 * lot_size

def in_trading_session(session_list):
    utc_hour = datetime.utcnow().hour
    sessions = {'London': (8, 16), 'NewYork': (13, 22), 'Tokyo': (0, 9)}
    for s in session_list:
        start, end = sessions[s]
        if start <= utc_hour < end:
            return True
    return False

def is_high_liquidity():
    utc_hour = datetime.utcnow().hour
    return 13 <= utc_hour < 16
