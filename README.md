# Forex Bot 10USD

A Python-based algorithmic trading bot designed for scalping forex and gold pairs with strict risk management. Designed to work with small account sizes ($10+ minimum) using MetaTrader 5.

## Overview

**Strategy:** ScalpVWAP - A momentum-based scalping strategy using VWAP, ADX, and RSI signals.

**Pairs Traded:** 
- EURUSD (Forex)
- XAUUSD (Gold)

**Timeframes:** M1 (scalping), M15 (trend confirmation)

---

## Features

✅ **Strict Risk Management**
- Per-trade risk limits ($3 max per trade, 0.25% account risk)
- Daily P&L limits (50% profit target, 50% loss limit)
- Drawdown tracking (80% max drawdown)
- Position sizing based on risk calculations
- Account risk cap (no trade risks >35% of account)

✅ **Smart Order Management**
- Partial profit-taking at 1:1 risk-reward ratio
- Trailing stops using ATR
- Breakeven protection
- Spread/slippage filtering

✅ **Trading Filters**
- Session filtering (London, New York hours only)
- Liquidity hour detection (1-4 PM UTC for tighter spreads)
- Minimum ADX requirement (trend strength filter)
- Spread monitoring

✅ **Safe Testing**
- Paper trading mode for backtesting
- Comprehensive logging
- MetaTrader 5 integration with retry logic

---

## Installation

### Prerequisites
- Python 3.8+
- MetaTrader 5 terminal (installed and running)
- Active trading account (demo or live)

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/Ceejaythenerd/forex_bot_10usd.git
cd forex_bot_10usd
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure MetaTrader 5:**
   - Open MetaTrader 5 terminal
   - Ensure the terminal is running (bot connects to it)
   - Verify account balance and broker connection

---

## Configuration

Edit `config.py` to customize trading parameters:

### Trading Pairs & Timeframes
```python
pairs: tuple = ('EURUSD', 'XAUUSD')      # Currency pairs to trade
timeframe: str = 'M1'                     # Scalping timeframe
htf_timeframe: str = 'M15'                # Higher timeframe for trend filter
```

### Risk Management
```python
risk_per_trade: float = 0.25              # Risk % of account per trade
max_risk_usd: float = 3.00                # Maximum loss per trade (USD)
max_daily_loss_pct: float = 0.50          # Max daily loss (% of account)
max_daily_profit_pct: float = 0.50        # Max daily profit target (% of account)
max_drawdown_pct: float = 0.80            # Max drawdown tolerance
max_trades_per_day: int = 5               # Trading limit per day
max_open_trades: int = 1                  # Concurrent open positions
```

### Strategy Parameters
```python
atr_period: int = 14                      # ATR calculation period
atr_stop_multiple_fx: float = 0.6         # ATR multiplier for FX stops
atr_stop_multiple_gold: float = 0.5       # ATR multiplier for Gold stops
atr_trail_multiple: float = 0.8           # ATR multiplier for trailing stops
rr_target: float = 2.0                    # Risk-reward target ratio
partial_close_pct: float = 0.5            # Partial close percentage at 1:1 RR
partial_close_at_rr: float = 1.0          # RR level to trigger partial close
min_adx: int = 15                         # Minimum ADX for trend confirmation
```

### Session & Liquidity
```python
use_htf_filter: bool = False              # Enable higher timeframe trend filter
session_filter: list = ['London', 'NewYork']  # Active trading sessions
```

Available sessions: 'London', 'NewYork', 'Tokyo'

---

## Running the Bot

### Paper Trading Mode (Recommended for Testing)
```bash
python live_trader.py
```

The bot will log all activity to `bot.log` and simulate orders without executing real trades.

### Live Trading Mode
```python
# In live_trader.py, change:
bot = TradingBot(paper_mode=False)  # Enable live trading
bot.run()
```

⚠️ **WARNING:** Only enable live trading after thorough backtesting and paper trading validation.

---

## Strategy Details

### ScalpVWAP Strategy

**Entry Signals:**

**LONG Signal:**
- Price bounces above VWAP
- ADX > 15 (trending market)
- RSI < 60 (not overbought)
- Optional: Price > EMA200 (uptrend filter)

**SHORT Signal:**
- Price rejects below VWAP
- ADX > 15
- RSI > 40 (not oversold)
- Optional: Price < EMA200 (downtrend filter)

**Exit Strategy:**
1. **Partial Close:** Automatically close 50% of position at 1:1 risk-reward
2. **Trailing Stop:** Remaining 50% uses ATR-based trailing stop
3. **Breakeven:** Move stop-loss to entry after reaching 1:1 RR

---

## Performance & Logging

All trades are logged to `bot.log`:
```
2026-05-10 12:34:56 | INFO | Bot started. Balance: $10.00
2026-05-10 12:34:57 | INFO | PAPER ORDER: LONG EURUSD 0.01 lots @ 1.0850
2026-05-10 12:35:02 | INFO | Order placed: 12345
```

Monitor the log file to:
- Track executed trades and P&L
- Debug strategy signals
- Identify risk manager stops

---

## File Structure

```
forex_bot_10usd/
├── README.md              # This file
├── config.py              # Configuration parameters
├── live_trader.py         # Main bot engine
├── strategy.py            # Signal generation (ScalpVWAP)
├── indicators.py          # Technical indicators
├── risk_manager.py        # Position sizing & risk controls
├── utils.py               # Helper functions
├── requirements.txt       # Python dependencies
├── bot.log                # Trading log (auto-generated)
└── backtest_results/      # Backtesting results (future)
```

---

## Planned Improvements

- [ ] Backtesting module using historical data
- [ ] Unit tests for strategy and risk manager
- [ ] Multiple strategy support
- [ ] Real-time P&L dashboard
- [ ] Email/Discord notifications on trades
- [ ] Configurable magic number via config.py
- [ ] Additional currency pairs
- [ ] Machine learning signal optimization

---

## Troubleshooting

### MetaTrader 5 Connection Failed
- Ensure MetaTrader 5 terminal is running
- Check broker connection status
- Verify account is active

### Spread Too High
- Adjust `session_filter` to higher liquidity hours
- Lower `spread_pips_fx` and `spread_cents_gold` thresholds
- Trade during London/New York overlap (1-4 PM UTC)

### No Trades Generated
- Check ADX > 15 requirement
- Verify HTF trend filter is not too strict
- Review `bot.log` for rejection reasons

### Account Balance Not Updating
- Manually refresh account info in MT5
- Check for order execution failures in logs
- Verify broker permissions for the account

---

## Risk Disclaimer

⚠️ **IMPORTANT:** Forex and futures trading carries substantial risk of loss. This bot:
- Is provided as-is without warranty
- Should be tested extensively in paper trading first
- May lose money; only use funds you can afford to lose
- Requires active monitoring, especially in early deployments
- Is not financial advice; consult a financial advisor before trading

---

## License

This project is open source. Feel free to fork, modify, and improve.

---

## Support & Contributions

Found a bug? Have an improvement? Open an issue or submit a pull request!

For questions:
- Check the Troubleshooting section
- Review `bot.log` for diagnostic information
- Examine strategy signals in `strategy.py`

---

## Changelog

### v1.0 (2026-05-10)
- Initial release
- ScalpVWAP strategy
- Risk management system
- MetaTrader 5 integration
- Paper trading support
