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
# RSI
# =========================
def RSI(close, period=14):

    delta = np.diff(close, prepend=close[0])

    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = pd.Series(gain).rolling(period).mean()
    avg_loss = pd.Series(loss).rolling(period).mean()

    rs = avg_gain / (avg_loss + 1e-9)

    rsi = 100 - (100 / (1 + rs))

    return rsi.values


# =========================
# MACD
# =========================
def MACD(close):

    ema12 = EMA(close, 12)
    ema26 = EMA(close, 26)

    macd = ema12 - ema26
    signal = EMA(macd, 9)
    hist = macd - signal

    return macd, signal, hist


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
# KDJ
# =========================
def KDJ(high, low, close, n=9):

    low_min = pd.Series(low).rolling(n).min()
    high_max = pd.Series(high).rolling(n).max()

    rsv = (close - low_min) / (high_max - low_min + 1e-9) * 100

    k = pd.Series(rsv).ewm(com=2).mean()
    d = k.ewm(com=2).mean()

    return k.values, d.values


# =========================
# 回測核心
# =========================
def backtest(close, buy, sell, fig):

    equity = 0
    equity_curve = []

    trade = []

    pos = 0
    entry = 0

    wins = 0
    losses = 0

    for i in range(len(close)):

        if i == 0:
            equity_curve.append(0)
            continue

        # =====================
        # BUY
        # =====================
        if buy[i] and pos == 0:

            pos = 1
            entry = close[i]

            trade.append({
                "type": "BUY",
                "price": round(entry, 2)
            })

        # =====================
        # SELL
        # =====================
        elif sell[i] and pos == 1:

            pnl = close[i] - entry

            equity += pnl

            pos = 0

            trade.append({
                "type": "SELL",
                "price": round(close[i], 2),
                "pnl": round(pnl, 2)
            })

            if pnl > 0:
                wins += 1
            else:
                losses += 1

        equity_curve.append(equity)

    return pack(
        equity,
        equity_curve,
        trade,
        wins,
        losses,
        fig
    )


# =========================
# MA策略
# =========================
def run_ma_strategy(df, short=5, long=20):

    k = build_kbar(df)

    close = k["close"]

    sma_s = SMA(close, short)
    sma_l = SMA(close, long)

    buy = (
        (sma_s > sma_l) &
        (pd.Series(sma_s).shift(1) <= pd.Series(sma_l).shift(1))
    )

    sell = (
        (sma_s < sma_l) &
        (pd.Series(sma_s).shift(1) >= pd.Series(sma_l).shift(1))
    )

    # =====================
    # 圖形
    # =====================
    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(close, label="Close")
    ax.plot(sma_s, label=f"SMA {short}")
    ax.plot(sma_l, label=f"SMA {long}")

    ax.set_title("MA Strategy")
    ax.legend()

    return backtest(close, buy, sell, fig)


# =========================
# MACD策略
# =========================
def run_macd_strategy(df):

    k = build_kbar(df)

    close = k["close"]

    macd, signal, hist = MACD(close)

    buy = (
        (macd > signal) &
        (pd.Series(macd).shift(1) <= pd.Series(signal).shift(1))
    )

    sell = (
        (macd < signal) &
        (pd.Series(macd).shift(1) >= pd.Series(signal).shift(1))
    )

    # =====================
    # 圖形
    # =====================
    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(macd, label="MACD")
    ax.plot(signal, label="Signal")

    ax.set_title("MACD Strategy")
    ax.legend()

    return backtest(close, buy, sell, fig)


# =========================
# RSI策略（均值回歸）
# =========================
def run_rsi_strategy(df):

    k = build_kbar(df)

    close = k["close"]

    rsi = RSI(close)

    ma50 = SMA(close, 50)

    # =====================
    # 真正不同邏輯
    # =====================
    buy = (
        (rsi < 30) &
        (close > ma50)
    )

    sell = (
        (rsi > 70) |
        (close < ma50)
    )

    # =====================
    # 圖形
    # =====================
    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(rsi, label="RSI")

    ax.axhline(70, color="red")
    ax.axhline(30, color="green")

    ax.set_title("RSI Mean Reversion")
    ax.legend()

    return backtest(close, buy, sell, fig)


# =========================
# KDJ策略（動能策略）
# =========================
def run_kdj_strategy(df):

    k = build_kbar(df)

    close = k["close"]

    k_value, d_value = KDJ(
        k["high"],
        k["low"],
        close
    )

    ma20 = SMA(close, 20)

    # =====================
    # 順勢動能
    # =====================
    buy = (
        (k_value > d_value) &
        (close > ma20)
    )

    sell = (
        (k_value < d_value) |
        (close < ma20)
    )

    # =====================
    # 圖形
    # =====================
    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(k_value, label="K")
    ax.plot(d_value, label="D")

    ax.axhline(80, color="red")
    ax.axhline(20, color="green")

    ax.set_title("KDJ Momentum")
    ax.legend()

    return backtest(close, buy, sell, fig)


# =========================
# 布林通道策略（突破）
# =========================
def run_bollinger_strategy(df):

    k = build_kbar(df)

    close = k["close"]

    upper, mid, lower = BBANDS(close)

    # =====================
    # Breakout
    # =====================
    buy = close > upper

    sell = close < mid

    # =====================
    # 圖形
    # =====================
    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(close, label="Close")
    ax.plot(upper, label="Upper")
    ax.plot(mid, label="Middle")
    ax.plot(lower, label="Lower")

    ax.set_title("Bollinger Breakout")
    ax.legend()

    return backtest(close, buy, sell, fig)


# =========================
# MA最佳化
# =========================
def optimize_ma(df):

    best_result = None
    best_score = -999999
    best_params = None

    for short in range(5, 30, 5):

        for long in range(10, 60, 10):

            if short >= long:
                continue

            result = run_ma_strategy(
                df,
                short,
                long
            )

            score = (
                result["sharpe"] * 0.6 +
                result["profit"] * 0.001 -
                result["mdd"] * 0.5
            )

            if score > best_score:

                best_score = score
                best_result = result
                best_params = (short, long)

    return best_result, best_params, best_score


# =========================
# 策略排行榜
# =========================
def strategy_rank(results):

    ranking = []

    for name, result in results.items():

        score = (
            result["sharpe"] * 0.6 +
            result["profit"] * 0.001 -
            result["mdd"] * 0.5
        )

        ranking.append({
            "策略": name,
            "分數": round(score, 4),
            "淨利": round(result["profit"], 2),
            "勝率": round(result["winrate"] * 100, 2),
            "最大回撤": round(result["mdd"], 2),
            "Sharpe": round(result["sharpe"], 2)
        })

    rank_df = pd.DataFrame(ranking)

    rank_df = rank_df.sort_values(
        by="分數",
        ascending=False
    )

    return rank_df


# =========================
# 最大回撤
# =========================
def max_drawdown(curve):

    peak = -999999

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

    if len(r) == 0:
        return 0

    if np.std(r) == 0:
        return 0

    return np.mean(r) / np.std(r)


# =========================
# pack
# =========================
def pack(
    equity,
    curve,
    trade,
    wins,
    losses,
    fig
):

    total = wins + losses

    if total == 0:
        winrate = 0
    else:
        winrate = wins / total

    return {

        "profit": equity,

        "winrate": winrate,

        "mdd": max_drawdown(curve),

        "sharpe": sharpe_ratio(curve),

        "equity_curve": curve,

        "trade_record": trade,

        "fig": fig
    }
