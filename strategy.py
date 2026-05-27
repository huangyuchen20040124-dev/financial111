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
# MA策略
# =========================
def run_ma_strategy(df, short=5, long=20):

    k = build_kbar(df)
    close = k["close"]

    sma_s = SMA(k, timeperiod=short)
    sma_l = SMA(k, timeperiod=long)

    buy = sma_s > sma_l
    sell = sma_s < sma_l

    return backtest(close, buy, sell, "MA")


# =========================
# MACD策略
# =========================
def run_macd_strategy(df):

    k = build_kbar(df)
    close = k["close"]

    macd, signal, _ = MACD(k)

    buy = macd > signal
    sell = macd < signal

    return backtest(close, buy, sell, "MACD")


# =========================
# KDJ策略
# =========================
def run_kdj_strategy(df):

    k = build_kbar(df)
    close = k["close"]

    kdj_k, kdj_d = STOCH(k)

    buy = kdj_k < 20
    sell = kdj_k > 80

    return backtest(close, buy, sell, "KDJ")


# =========================
# RSI策略（新增）
# =========================
def run_rsi_strategy(df):

    k = build_kbar(df)
    close = k["close"]

    rsi = RSI(k, timeperiod=14)

    buy = rsi < 30
    sell = rsi > 70

    return backtest(close, buy, sell, "RSI")


# =========================
# 布林通道策略（新增）
# =========================
def run_bollinger_strategy(df):

    k = build_kbar(df)
    close = k["close"]

    upper, mid, lower = BBANDS(k, timeperiod=20)

    buy = close < lower
    sell = close > upper

    return backtest(close, buy, sell, "BB")


# =========================
# 回傳封裝
# =========================
def pack(equity, curve, trade, wins, losses, fig):

    winrate = wins / (wins + losses) if (wins + losses) > 0 else 0
    mdd = max_drawdown(curve)
    sharpe = sharpe_ratio(curve)

    return {
        "profit": equity,
        "winrate": winrate,
        "mdd": mdd,
        "sharpe": sharpe,
        "equity_curve": curve,
        "trade_record": trade,
        "fig": fig
    }


# =========================
# MDD
# =========================
def max_drawdown(curve):
    peak = -1e9
    mdd = 0
    for x in curve:
        peak = max(peak, x)
        mdd = max(mdd, peak - x)
    return mdd


# =========================
# Sharpe
# =========================
def sharpe_ratio(curve):
    r = np.diff(curve)
    if len(r) == 0 or np.std(r) == 0:
        return 0
    return np.mean(r) / np.std(r)


# =========================
# 🏆 排行榜
# =========================
def strategy_rank(results):

    ranking = []

    for name, r in results.items():

        score = r["sharpe"] * 0.6 + r["profit"] * 0.001 - r["mdd"] * 0.5

        ranking.append({
            "strategy": name,
            "score": score,
            "profit": r["profit"],
            "sharpe": r["sharpe"],
            "mdd": r["mdd"]
        })

    return sorted(ranking, key=lambda x: x["score"], reverse=True)
