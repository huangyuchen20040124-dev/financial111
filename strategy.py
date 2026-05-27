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
# EMA
# =========================
def EMA(arr, span):
    return pd.Series(arr).ewm(span=span, adjust=False).mean().values


# =========================
# RSI（無TA-Lib）
# =========================
def RSI(close, period=14):
    delta = np.diff(close, prepend=close[0])
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = pd.Series(gain).rolling(period).mean()
    avg_loss = pd.Series(loss).rolling(period).mean()

    rs = avg_gain / (avg_loss + 1e-9)
    return (100 - (100 / (1 + rs))).values


# =========================
# MACD
# =========================
def MACD(close):
    ema12 = EMA(close, 12)
    ema26 = EMA(close, 26)
    macd = ema12 - ema26
    signal = EMA(macd, 9)
    return macd, signal, None


# =========================
# 布林通道
# =========================
def BBANDS(close, n=20):
    mid = pd.Series(close).rolling(n).mean().values
    std = pd.Series(close).rolling(n).std().values

    upper = mid + 2 * std
    lower = mid - 2 * std

    return upper, mid, lower


# =========================
# KDJ（簡化穩定版）
# =========================
def KDJ(high, low, close, n=9):

    low_min = pd.Series(low).rolling(n).min()
    high_max = pd.Series(high).rolling(n).max()

    rsv = (close - low_min) / (high_max - low_min + 1e-9)

    k = pd.Series(rsv).rolling(3).mean().values
    d = pd.Series(k).rolling(3).mean().values

    return k, d


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
# MA
# =========================
def run_ma_strategy(df, short=5, long=20):
    k = build_kbar(df)
    close = k["close"]

    sma_s = SMA(close, short)
    sma_l = SMA(close, long)

    return backtest(close, sma_s > sma_l, sma_s < sma_l, "MA")


# =========================
# MACD
# =========================
def run_macd_strategy(df):
    k = build_kbar(df)
    close = k["close"]

    macd, signal, _ = MACD(close)

    return backtest(close, macd > signal, macd < signal, "MACD")


# =========================
# KDJ
# =========================
def run_kdj_strategy(df):
    k = build_kbar(df)
    close = k["close"]

    kdj_k, kdj_d = KDJ(k["high"], k["low"], close)

    return backtest(close, kdj_k < kdj_d, kdj_k > kdj_d, "KDJ")


# =========================
# RSI
# =========================
def run_rsi_strategy(df):
    k = build_kbar(df)
    close = k["close"]

    rsi = RSI(close)

    return backtest(close, rsi < 30, rsi > 70, "RSI")


# =========================
# 布林通道
# =========================
def run_bollinger_strategy(df):
    k = build_kbar(df)
    close = k["close"]

    upper, mid, lower = BBANDS(close)

    return backtest(close, close < lower, close > upper, "BB")


# =========================
# MA最佳化
# =========================
def optimize_ma(df):

    best = None
    best_score = -1e9
    best_params = None

    for s in range(5, 30, 5):
        for l in range(10, 60, 10):

            if s >= l:
                continue

            r = run_ma_strategy(df, s, l)

            score = r["sharpe"] * 0.6 + r["profit"] * 0.001 - r["mdd"] * 0.5

            if score > best_score:
                best_score = score
                best = r
                best_params = (s, l)

    return best, best_params, best_score


# =========================
# ranking
# =========================
def strategy_rank(results):

    out = []

    for name, r in results.items():

        score = r["sharpe"] * 0.6 + r["profit"] * 0.001 - r["mdd"] * 0.5

        out.append({
            "strategy": name,
            "score": score,
            "profit": r["profit"],
            "winrate": r["winrate"],
            "mdd": r["mdd"],
            "sharpe": r["sharpe"]
        })

    return sorted(out, key=lambda x: x["score"], reverse=True)


# =========================
# metrics
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
