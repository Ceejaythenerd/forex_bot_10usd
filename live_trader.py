import MetaTrader5 as mt5
import pandas as pd
import time
from datetime import datetime
from config import config
from risk_manager import RiskManager
from strategy import ScalpVWAPStrategy
from indicators import add_indicators
from utils import setup_logger, in_trading_session, is_high_liquidity

logger = setup_logger('live')

class TradingBot:
    def __init__(self, paper_mode=True):
        self.paper_mode = paper_mode
        if not mt5.initialize():
            raise Exception("MT5 init failed")

        self.account_info = mt5.account_info()
        self.risk_manager = RiskManager(self.account_info.balance)
        self.strategy = ScalpVWAPStrategy()
        self.trades_today = 0
        self.last_day = datetime.utcnow().date()
        logger.info(f"Bot started. Balance: ${self.account_info.balance:.2f}")

    def reset_daily_counters(self):
        today = datetime.utcnow().date()
        if today!= self.last_day:
            self.trades_today = 0
            self.last_day = today
            self.risk_manager.daily_pnl = 0
            self.risk_manager.trading_enabled = True

    def get_market_data(self, pair, tf, bars=500):
        tf_map = {'M1': mt5.TIMEFRAME_M1, 'M5': mt5.TIMEFRAME_M5, 'M15': mt5.TIMEFRAME_M15}
        rates = mt5.copy_rates_from_pos(pair, tf_map[tf], 0, bars)
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df

    def get_spread(self, pair):
        tick = mt5.symbol_info_tick(pair)
        if not tick: return float('inf')
        return (tick.ask - tick.bid) / mt5.symbol_info(pair).point

    def send_order(self, pair, signal, lots, entry, sl, tp):
        if self.paper_mode:
            logger.info(f"PAPER ORDER: {signal} {pair} {lots:.2f} lots @ {entry}")
            return True

        order_type = mt5.ORDER_TYPE_BUY_LIMIT if signal == 'LONG' else mt5.ORDER_TYPE_SELL_LIMIT
        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": pair,
            "volume": lots,
            "type": order_type,
            "price": entry,
            "sl": sl,
            "tp": tp,
            "deviation": 20,
            "magic": 12345,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        for attempt in range(3):
            result = mt5.order_send(request)
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"Order placed: {result.order}")
                return True
            time.sleep(0.5)
        return False

    def manage_positions(self):
        positions = mt5.positions_get()
        if not positions: return

        for pos in positions:
            df = self.get_market_data(pos.symbol, config.timeframe, 50)
            df = add_indicators(df)
            last = df.iloc[-1]

            entry = pos.price_open
            current = pos.price_current
            point = mt5.symbol_info(pos.symbol).point
            profit_pips = (current - entry) / point if pos.type == 0 else (entry - current) / point
            risk_pips = abs(entry - pos.sl) / point

            if profit_pips >= config.partial_close_at_rr * risk_pips and pos.volume > 0.01:
                close_vol = round(pos.volume * config.partial_close_pct, 2)
                self.close_partial(pos, close_vol)

            if profit_pips >= risk_pips and ((pos.type == 0 and pos.sl < entry) or (pos.type == 1 and pos.sl > entry)):
                new_sl = entry + (1 * point if pos.type == 0 else -1 * point)
                self.modify_sl(pos, new_sl)

            trail_dist = config.atr_trail_multiple * last['ATR']
            new_trail_sl = current - trail_dist if pos.type == 0 else current + trail_dist
            if (pos.type == 0 and new_trail_sl > pos.sl) or (pos.type == 1 and new_trail_sl < pos.sl):
                self.modify_sl(pos, new_trail_sl)

    def close_partial(self, pos, volume):
        request = {"action": mt5.TRADE_ACTION_DEAL, "symbol": pos.symbol, "volume": volume,
                   "type": mt5.ORDER_TYPE_SELL if pos.type == 0 else mt5.ORDER_TYPE_BUY,
                   "position": pos.ticket, "deviation": 20, "magic": 12345}
        mt5.order_send(request)

    def modify_sl(self, pos, new_sl):
        request = {"action": mt5.TRADE_ACTION_SLTP, "symbol": pos.symbol, "position": pos.ticket,
                   "sl": new_sl, "tp": pos.tp}
        mt5.order_send(request)

    def run_cycle(self):
        self.reset_daily_counters()

        if not in_trading_session(config.session_filter):
            return
        if not is_high_liquidity():
            return
        if self.trades_today >= config.max_trades_per_day:
            return
        if len(mt5.positions_get()) >= config.max_open_trades:
            return

        for pair in config.pairs:
            spread = self.get_spread(pair)
            max_spread = 1.5 if 'EUR' in pair else 4.0
            if spread > max_spread:
                continue

            df = self.get_market_data(pair, config.timeframe)
            htf_df = self.get_market_data(pair, config.htf_timeframe)
            df = add_indicators(df)
            htf_df = add_indicators(htf_df)

            signal, sl, tp = self.strategy.generate_signal(df, htf_df, pair)
            if not signal:
                continue

            entry_price = df.iloc[-1]['Close']
            ok, lots, msg = self.risk_manager.check_risk(pair, signal, sl, entry_price)
            if not ok:
                logger.warning(msg)
                continue

            limit_price = entry_price - 0.0001 if signal == 'LONG' else entry_price + 0.0001
            if self.send_order(pair, signal, lots, limit_price, sl, tp):
                self.trades_today += 1

        self.manage_positions()

    def run(self):
        while True:
            try:
                self.run_cycle()
                time.sleep(5)
            except Exception as e:
                logger.error(f"Error: {e}")
                time.sleep(30)

if __name__ == "__main__":
    bot = TradingBot(paper_mode=True)
    bot.run()
