import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from talib.abstract import SMA, MACD, STOCH


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
# MA策略
# =========================
def run_ma_strategy(df, short=5, long=20):

    k = build_kbar(df)
    close = k["close"]

    sma_s = SMA(k, timeperiod=short)
    sma_l = SMA(k, timeperiod=long)

    equity = 0
    equity_curve = []
    trade = []

    pos = 0
    entry = 0
    wins = losses = 0

    fig, ax = plt.subplots()
    ax.plot(sma_s, label="SMA short")
    ax.plot(sma_l, label="SMA long")
    ax.legend()

    for i in range(1, len(close)):

        if np.isnan(sma_s[i]) or np.isnan(sma_l[i]):
            equity_curve.append(equity)
            continue

        # BUY
        if sma_s[i] > sma_l[i] and sma_s[i-1] <= sma_l[i-1] and pos == 0:
            pos = 1
            entry = close[i]
            trade.append({
                "time": k["time"][i],
                "type": "BUY",
                "price": entry
            })

        # SELL
        elif sma_s[i] < sma_l[i] and sma_s[i-1] >= sma_l[i-1] and pos == 1:
            pnl = close[i] - entry
            equity += pnl
            pos = 0

            trade.append({
                "time": k["time"][i],
                "type": "SELL",
                "price": close[i],
                "pnl": pnl
            })

            wins += pnl > 0
            losses += pnl <= 0

        equity_curve.append(equity)

    # 強制平倉
    if pos == 1:
        pnl = close[-1] - entry
        equity += pnl
        trade.append({"type": "SELL", "price": close[-1], "pnl": pnl})

    return pack(equity, equity_curve, trade, wins, losses, fig)


# =========================
# MACD
# =========================
def run_macd_strategy(df):

    k = build_kbar(df)
    close = k["close"]

    macd, signal, hist = MACD(k)

    equity = 0
    equity_curve = []
    trade = []

    pos = 0
    entry = 0
    wins = losses = 0

    fig, ax = plt.subplots()
    ax.plot(macd, label="MACD")
    ax.plot(signal, label="Signal")
    ax.legend()

    for i in range(1, len(close)):

        if np.isnan(macd[i]):
            equity_curve.append(equity)
            continue

        if macd[i] > signal[i] and macd[i-1] <= signal[i-1] and pos == 0:
            pos = 1
            entry = close[i]
            trade.append({"time": k["time"][i], "type": "BUY", "price": entry})

        elif macd[i] < signal[i] and macd[i-1] >= signal[i-1] and pos == 1:
            pnl = close[i] - entry
            equity += pnl
            pos = 0

            trade.append({
                "time": k["time"][i],
                "type": "SELL",
                "price": close[i],
                "pnl": pnl
            })

            wins += pnl > 0
            losses += pnl <= 0

        equity_curve.append(equity)

    return pack(equity, equity_curve, trade, wins, losses, fig)


# =========================
# KDJ
# =========================
def run_kdj_strategy(df):

    k = build_kbar(df)
    close = k["close"]

    slowk, slowd = STOCH(k)

    equity = 0
    equity_curve = []
    trade = []

    pos = 0
    entry = 0
    wins = losses = 0

    fig, ax = plt.subplots()
    ax.plot(slowk, label="K")
    ax.plot(slowd, label="D")
    ax.legend()

    for i in range(1, len(close)):

        if np.isnan(slowk[i]):
            equity_curve.append(equity)
            continue

        if slowk[i] > slowd[i] and slowk[i-1] <= slowd[i-1] and slowk[i] < 20 and pos == 0:
            pos = 1
            entry = close[i]
            trade.append({"time": k["time"][i], "type": "BUY", "price": entry})

        elif slowk[i] < slowd[i] and slowk[i-1] >= slowd[i-1] and slowk[i] > 80 and pos == 1:
            pnl = close[i] - entry
            equity += pnl
            pos = 0

            trade.append({"time": k["time"][i], "type": "SELL", "price": close[i], "pnl": pnl})

            wins += pnl > 0
            losses += pnl <= 0

        equity_curve.append(equity)

    return pack(equity, equity_curve, trade, wins, losses, fig)


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
    r = pd.Series(curve).diff().fillna(0)
    if r.std() == 0:
        return 0
    return r.mean() / r.std()


# =========================
# MA最佳化
# =========================
def optimize_ma(df):

    best_result = None
    best_score = -1e9
    best_params = None

    for short in range(5, 30, 5):
        for long in range(10, 60, 10):

            if short >= long:
                continue

            result = run_ma_strategy(df, short, long)

            score = result["sharpe"] * 100 + result["profit"] - result["mdd"] * 2

            if score > best_score:
                best_score = score
                best_result = result
                best_params = (short, long)

    return best_result, best_params, best_score


# =========================
# 排行榜
# =========================
def strategy_rank(results):

    ranking = []

    for name, r in results.items():
        ranking.append({
            "strategy": name,
            "profit": r["profit"],
            "winrate": r["winrate"],
            "mdd": r["mdd"],
            "sharpe": r["sharpe"]
        })

    ranking = sorted(ranking, key=lambda x: x["sharpe"], reverse=True)

    return ranking
