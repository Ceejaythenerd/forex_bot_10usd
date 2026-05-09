from config import config
from utils import pip_value, setup_logger

logger = setup_logger('risk')

class RiskManager:
    def __init__(self, account_balance):
        self.balance = account_balance
        self.daily_pnl = 0
        self.peak_equity = account_balance
        self.trading_enabled = True

    def check_risk(self, pair, signal, sl_price, entry_price):
        if not self.trading_enabled:
            return False, 0, "Trading paused"

        if self.daily_pnl >= self.balance * config.max_daily_profit_pct:
            self.trading_enabled = False
            return False, 0, "Daily profit target hit"

        if self.daily_pnl <= -self.balance * config.max_daily_loss_pct:
            self.trading_enabled = False
            return False, 0, "Daily loss limit hit"

        current_dd = (self.peak_equity - self.balance) / self.peak_equity
        if current_dd >= config.max_drawdown_pct:
            self.trading_enabled = False
            return False, 0, "Max drawdown hit"

        max_risk_usd = min(self.balance * config.risk_per_trade, config.max_risk_usd)
        stop_distance = abs(entry_price - sl_price)

        if 'XAU' in pair:
            lots = max_risk_usd / (stop_distance * 100)
        else:
            lots = max_risk_usd / (stop_distance * pip_value(pair) / 0.0001)

        lots = max(0.01, round(lots, 2))

        trade_risk = lots * stop_distance * pip_value(pair) / 0.0001 if 'XAU' not in pair else lots * stop_distance * 100
        if trade_risk > self.balance * 0.35:
            return False, 0, "Trade risks >35% of account"

        return True, lots, ""

    def update_pnl(self, pnl):
        self.daily_pnl += pnl
        self.balance += pnl
        self.peak_equity = max(self.peak_equity, self.balance)
