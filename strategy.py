import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# =========================
# KBar
# =========================
def build_kbar(df):
    return {
        "open": df["open"].astype(float).values,
        "high": df["high"].astype(float).values,
        "low": df["low"].astype(float).values,
        "close": df["close"].astype(float).values,
        "time": pd.to_datetime(df["time"]).values
    }


# =========================
# SMA
# =========================
def SMA(arr, n):
    return pd.Series(arr).rolling(n).mean().values


# =========================
# RSI（均值回歸）
# =========================
def RSI(close, period=14):
    delta = np.diff(close, prepend=close[0])
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = pd.Series(gain).rolling(period).mean()
    avg_loss = pd.Series(loss).rolling(period).mean()

    rs = avg_gain / (avg_loss + 1e-9)
    return (100 - (100 / (1 + rs))).values


def run_rsi_strategy(df):
    k = build_kbar(df)
    close = k["close"]

    rsi = RSI(close)

    # 👉 均值回歸（超賣買、但要趨勢過濾）
    ma = SMA(close, 50)

    buy = (rsi < 30) & (close > ma)
    sell = (rsi > 70) | (close < ma)

    return backtest(close, buy, sell, "RSI Mean Reversion")


# =========================
# 布林通道（突破策略）
# =========================
def BBANDS(close, n=20):
    mid = pd.Series(close).rolling(n).mean().values
    std = pd.Series(close).rolling(n).std().values

    upper = mid + 2 * std
    lower = mid - 2 * std

    return upper, mid, lower


def run_bollinger_strategy(df):
    k = build_kbar(df)
    close = k["close"]

    upper, mid, lower = BBANDS(close)

    # 👉 突破策略（不是反轉！）
    buy = close > upper      # 突破上軌追多
    sell = close < mid       # 跌回均線出場

    return backtest(close, buy, sell, "BB Breakout")


# =========================
# KDJ（動能趨勢）
# =========================
def KDJ(high, low, close, n=9):
    low_min = pd.Series(low).rolling(n).min()
    high_max = pd.Series(high).rolling(n).max()

    rsv = (close - low_min) / (high_max - low_min + 1e-9)

    k = pd.Series(rsv).rolling(3).mean().values
    d = pd.Series(k).rolling(3).mean().values

    return k, d


def run_kdj_strategy(df):
    k = build_kbar(df)
    close = k["close"]

    kdj_k, kdj_d = KDJ(k["high"], k["low"], close)

    ma20 = SMA(close, 20)

    # 👉 動能順勢（不是超買超賣）
    buy = (kdj_k > kdj_d) & (close > ma20)
    sell = (kdj_k < kdj_d) | (close < ma20)

    return backtest(close, buy, sell, "KDJ Momentum")


# =========================
# MA / MACD（保留）
# =========================
def run_ma_strategy(df):
    k = build_kbar(df)
    close = k["close"]

    sma_s = SMA(close, 5)
    sma_l = SMA(close, 20)

    return backtest(close, sma_s > sma_l, sma_s < sma_l, "MA")


def run_macd_strategy(df):
    ema12 = pd.Series(df["close"]).ewm(span=12).mean().values
    ema26 = pd.Series(df["close"]).ewm(span=26).mean().values

    macd = ema12 - ema26
    signal = pd.Series(macd).ewm(span=9).mean().values

    return backtest(df["close"].values, macd > signal, macd < signal, "MACD")


# =========================
# 回測核心
# =========================
def backtest(close, buy, sell, name):

    equity = 0
    curve = []
    trade = []

    pos = 0
    entry = 0
    wins = losses = 0

    fig, ax = plt.subplots()
    ax.set_title(name)

    for i in range(len(close)):

        if i == 0:
            curve.append(0)
            continue

        if buy[i] and pos == 0:
            pos = 1
            entry = close[i]
            trade.append({"type": "BUY", "price": entry})

        elif sell[i] and pos == 1:
            pnl = close[i] - entry
            equity += pnl
            pos = 0

            trade.append({"type": "SELL", "price": close[i], "pnl": pnl})

            if pnl > 0:
                wins += 1
            else:
                losses += 1

        curve.append(equity)

    return pack(equity, curve, trade, wins, losses, fig)


# =========================
# pack
# =========================
def pack(equity, curve, trade, wins, losses, fig):

    winrate = wins / (wins + losses) if (wins + losses) > 0 else 0

    return {
        "profit": equity,
        "winrate": winrate,
        "mdd": max_drawdown(curve),
        "sharpe": sharpe_ratio(curve),
        "equity_curve": curve,
        "trade_record": trade,
        "fig": fig
    }


def max_drawdown(curve):
    peak = -1e9
    mdd = 0
    for x in curve:
        peak = max(peak, x)
        mdd = max(mdd, peak - x)
    return mdd


def sharpe_ratio(curve):
    r = np.diff(curve)
    if len(r) == 0 or np.std(r) == 0:
        return 0
    return np.mean(r) / np.std(r)
