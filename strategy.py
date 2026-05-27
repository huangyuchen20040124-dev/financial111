import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from talib.abstract import SMA, MACD, RSI, BBANDS, STOCH


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
# fallback 防炸工具
# =========================
def safe_nan():
    return {
        "profit": 0,
        "winrate": 0,
        "mdd": 0,
        "sharpe": 0,
        "equity_curve": [],
        "trade_record": [],
        "fig": plt.figure()
    }


# =========================
# 通用回測
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

        if buy[i] and not buy[i-1] and pos == 0:
            pos = 1
            entry = close[i]
            trade.append({"type": "BUY", "price": entry})

        elif sell[i] and not sell[i-1] and pos == 1:
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
def run_ma_strategy(df):

    try:
        k = build_kbar(df)
        close = k["close"]

        sma_s = SMA(k, 5)
        sma_l = SMA(k, 20)

        return backtest(close, sma_s > sma_l, sma_s < sma_l, "MA")

    except:
        return safe_nan()


# =========================
# MACD
# =========================
def run_macd_strategy(df):

    try:
        k = build_kbar(df)
        close = k["close"]

        macd, signal, _ = MACD(k)

        return backtest(close, macd > signal, macd < signal, "MACD")

    except:
        return safe_nan()


# =========================
# KDJ
# =========================
def run_kdj_strategy(df):

    try:
        k = build_kbar(df)
        close = k["close"]

        kdj_k, kdj_d = STOCH(k)

        return backtest(close, kdj_k < 20, kdj_k > 80, "KDJ")

    except:
        return safe_nan()


# =========================
# RSI
# =========================
def run_rsi_strategy(df):

    try:
        k = build_kbar(df)
        close = k["close"]

        rsi = RSI(k, 14)

        return backtest(close, rsi < 30, rsi > 70, "RSI")

    except:
        return safe_nan()


# =========================
# BB
# =========================
def run_bollinger_strategy(df):

    try:
        k = build_kbar(df)
        close = k["close"]

        upper, mid, lower = BBANDS(k, 20)

        return backtest(close, close < lower, close > upper, "BB")

    except:
        return safe_nan()


# =========================
# ranking（超穩版）
# =========================
def strategy_rank(results):

    ranking = []

    for name, r in results.items():

        try:
            score = r.get("sharpe", 0) * 0.6 + r.get("profit", 0) * 0.001 - r.get("mdd", 0) * 0.5

            ranking.append({
                "strategy": name,
                "score": score,
                "profit": r.get("profit", 0),
                "sharpe": r.get("sharpe", 0),
                "mdd": r.get("mdd", 0)
            })

        except:
            continue

    return sorted(ranking, key=lambda x: x["score"], reverse=True)


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
