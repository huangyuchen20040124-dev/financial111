import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from talib.abstract import SMA, MACD, STOCH, RSI, BBANDS


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
# MA / MACD / KDJ（略同前，已修正 i-1 + 平倉）
# =========================
# 👉 你已經有，我就不重複貼，保持原修正版即可


# =========================================================
# RSI策略
# =========================================================
def run_rsi_strategy(df, period=14):

    k = build_kbar(df)
    close = k["close"]

    rsi = RSI(k, timeperiod=period)

    equity = 0
    equity_curve = []
    trade = []

    pos = 0
    entry = 0
    wins = losses = 0

    fig, ax = plt.subplots()
    ax.plot(rsi, label="RSI")
    ax.axhline(70, color="red")
    ax.axhline(30, color="green")
    ax.legend()

    for i in range(1, len(close)):

        if np.isnan(rsi[i]):
            equity_curve.append(equity)
            continue

        # 超賣買進
        if rsi[i] < 30 and pos == 0:
            pos = 1
            entry = close[i]
            trade.append({
                "time": k["time"][i],
                "type": "BUY",
                "price": entry
            })

        # 超買賣出
        elif rsi[i] > 70 and pos == 1:
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


# =========================================================
# 布林通道策略
# =========================================================
def run_bollinger_strategy(df, period=20):

    k = build_kbar(df)
    close = k["close"]

    upper, middle, lower = BBANDS(k, timeperiod=period)

    equity = 0
    equity_curve = []
    trade = []

    pos = 0
    entry = 0
    wins = losses = 0

    fig, ax = plt.subplots()
    ax.plot(close, label="Close")
    ax.plot(upper, label="Upper")
    ax.plot(middle, label="Middle")
    ax.plot(lower, label="Lower")
    ax.legend()

    for i in range(1, len(close)):

        if np.isnan(upper[i]):
            equity_curve.append(equity)
            continue

        # 跌破下軌買
        if close[i] < lower[i] and pos == 0:
            pos = 1
            entry = close[i]
            trade.append({
                "time": k["time"][i],
                "type": "BUY",
                "price": entry
            })

        # 碰上軌賣
        elif close[i] > upper[i] and pos == 1:
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


# =========================================================
# 共用封裝
# =========================================================
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
