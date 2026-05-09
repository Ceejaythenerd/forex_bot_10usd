from config import config

class ScalpVWAPStrategy:
    name = "ScalpVWAP"

    def generate_signal(self, df, htf_df, pair):
        last = df.iloc[-1]
        if last['ADX'] < config.min_adx:
            return None, None, None

        htf_trend_up = True
        if config.use_htf_filter and htf_df is not None:
            htf_trend_up = htf_df.iloc[-1]['Close'] > htf_df.iloc[-1]['EMA200']

        atr_mult = config.atr_stop_multiple_gold if 'XAU' in pair else config.atr_stop_multiple_fx

        if htf_trend_up and last['Low'] < last['VWAP'] and last['Close'] > last['VWAP'] and last['RSI'] < 60:
            sl = last['Close'] - atr_mult * last['ATR']
            tp = last['Close'] + config.rr_target * (last['Close'] - sl)
            return 'LONG', sl, tp

        if not htf_trend_up and last['High'] > last['VWAP'] and last['Close'] < last['VWAP'] and last['RSI'] > 40:
            sl = last['Close'] + atr_mult * last['ATR']
            tp = last['Close'] - config.rr_target * (sl - last['Close'])
            return 'SHORT', sl, tp

        return None, None, None
