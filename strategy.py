import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# =========================
# KBar
# =========================
def build_kbar(df):
    close = df["close"].astype(float).values
    high = df["high"].astype(float).values
    low = df["low"].astype(float).values
    return close, high, low


# =========================
# SMA
# =========================
def SMA(arr, n):
    return pd.Series(arr).rolling(n).mean().values


# =========================
# RSI
# =========================
def RSI(close, period=14):

    close = pd.Series(close)

    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()

    rs = avg_gain / (avg_loss + 1e-9)

    return (100 - (100 / (1 + rs))).values


# =========================
# MACD
# =========================
def MACD(close):

    close = pd.Series(close)

    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()

    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()

    return macd.values, signal.values


# =========================
# BBANDS
# =========================
def BBANDS(close, n=20):

    close = pd.Series(close)

    mid = close.rolling(n).mean()
    std = close.rolling(n).std()

    upper = mid + 2 * std
    lower = mid - 2 * std

    return upper.values, mid.values, lower.values


# =========================
# 回測核心（穩定版）
# =========================
def backtest(close, buy, sell, name):

    equity = 0
    curve = []
    trade = []

    pos = 0
    entry = 0
    wins = losses = 0

    for i in range(len(close)):

        if i == 0:
            curve.append(0)
            continue

        # 防止未來函數（避免 look-ahead bias）
        if buy[i-1] and pos == 0:
            pos = 1
            entry = close[i]
            trade.append({"type": "BUY", "price": entry})

        elif sell[i-1] and pos == 1:
            pnl = close[i] - entry
            equity += pnl
            pos = 0

            trade.append({"type": "SELL", "price": close[i], "pnl": pnl})

            if pnl > 0:
                wins += 1
            else:
                losses += 1

        curve.append(equity)

    # 強制平倉
    if pos == 1:
        equity += close[-1] - entry

    fig, ax = plt.subplots()
    ax.set_title(name)
    ax.plot(curve)

    return {
        "profit": equity,
        "winrate": wins / (wins + losses) if (wins + losses) > 0 else 0,
        "mdd": max_drawdown(curve),
        "sharpe": sharpe_ratio(curve),
        "equity_curve": curve,
        "trade_record": trade,
        "fig": fig
    }


# =========================
# RSI策略（完整可用）
# =========================
def run_rsi_strategy(df):

    close, _, _ = build_kbar(df)
    rsi = RSI(close)

    rsi = np.nan_to_num(rsi, nan=50)

    buy = rsi < 30
    sell = rsi > 70

    return backtest(close, buy, sell, "RSI")


# =========================
# MACD策略
# =========================
def run_macd_strategy(df):

    close, _, _ = build_kbar(df)
    macd, sig = MACD(close)

    macd = np.nan_to_num(macd, nan=0)
    sig = np.nan_to_num(sig, nan=0)

    buy = macd > sig
    sell = macd < sig

    return backtest(close, buy, sell, "MACD")


# =========================
# MA策略
# =========================
def run_ma_strategy(df):

    close, _, _ = build_kbar(df)

    sma_s = SMA(close, 5)
    sma_l = SMA(close, 20)

    sma_s = np.nan_to_num(sma_s, nan=0)
    sma_l = np.nan_to_num(sma_l, nan=0)

    buy = sma_s > sma_l
    sell = sma_s < sma_l

    return backtest(close, buy, sell, "MA")


# =========================
# 布林通道策略（完整可用）
# =========================
def run_bollinger_strategy(df):

    close, _, _ = build_kbar(df)

    upper, mid, lower = BBANDS(close)

    upper = np.nan_to_num(upper, nan=np.inf)
    lower = np.nan_to_num(lower, nan=-np.inf)
    mid = np.nan_to_num(mid, nan=np.mean(close))

    buy = close < lower
    sell = close > upper

    return backtest(close, buy, sell, "Bollinger")


# =========================
# KDJ策略（穩定版）
# =========================
def run_kdj_strategy(df):

    close, high, low = build_kbar(df)

    low_min = pd.Series(low).rolling(9).min()
    high_max = pd.Series(high).rolling(9).max()

    rsv = (close - low_min) / (high_max - low_min + 1e-9)

    k = pd.Series(rsv).rolling(3).mean().fillna(0).values

    buy = k < 0.2
    sell = k > 0.8

    return backtest(close, buy, sell, "KDJ")


# =========================
# 指標：最大回撤
# =========================
def max_drawdown(curve):

    peak = -1e9
    mdd = 0

    for x in curve:
        peak = max(peak, x)
        mdd = max(mdd, peak - x)

    return mdd


# =========================
# Sharpe Ratio
# =========================
def sharpe_ratio(curve):

    r = np.diff(curve)

    if len(r) == 0 or np.std(r) == 0:
        return 0

    return np.mean(r) / (np.std(r) + 1e-9)
