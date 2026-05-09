from dataclasses import dataclass

@dataclass
class Config:
    pairs: tuple = ('EURUSD', 'XAUUSD')
    timeframe: str = 'M1'
    htf_timeframe: str = 'M15'
    broker: str = 'MT5'

    risk_per_trade: float = 0.25
    max_risk_usd: float = 3.00
    max_daily_loss_pct: float = 0.50
    max_daily_profit_pct: float = 0.50
    max_drawdown_pct: float = 0.80
    max_trades_per_day: int = 5
    max_open_trades: int = 1

    atr_period: int = 14
    atr_stop_multiple_fx: float = 0.6
    atr_stop_multiple_gold: float = 0.5
    atr_trail_multiple: float = 0.8
    rr_target: float = 2.0
    partial_close_pct: float = 0.5
    partial_close_at_rr: float = 1.0

    use_htf_filter: bool = False
    min_adx: int = 15
    session_filter: list = ['London', 'NewYork']

    spread_pips_fx: float = 1.5
    spread_cents_gold: float = 40
    slippage_pips_fx: float = 1.0
    slippage_cents_gold: float = 60
    commission_per_lot: float = 0.0

config = Config()
