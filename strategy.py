import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# =========================
# KBAR
# =========================
def build_kbar(df):
    return {
        "open": df["open"].values,
        "high": df["high"].values,
        "low": df["low"].values,
        "close": df["close"].values,
        "time": df["time"].values
    }


# =========================
# MA
# =========================
def run_ma_strategy(df, short=5, long=20):

    k = build_kbar(df)
    close = k["close"]

    sma_s = pd.Series(close).rolling(short).mean().values
    sma_l = pd.Series(close).rolling(long).mean().values

    equity = 0
    curve = []
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
            curve.append(equity)
            continue

        if sma_s[i] > sma_l[i] and sma_s[i-1] <= sma_l[i-1] and pos == 0:
            pos = 1
            entry = close[i]
            trade.append({"time": k["time"][i], "type": "BUY", "price": entry})

        elif sma_s[i] < sma_l[i] and sma_s[i-1] >= sma_l[i-1] and pos == 1:
            pnl = close[i] - entry
            equity += pnl
            pos = 0

            trade.append({"time": k["time"][i], "type": "SELL", "price": close[i], "pnl": pnl})

            wins += pnl > 0
            losses += pnl <= 0

        curve.append(equity)

    if pos == 1:
        pnl = close[-1] - entry
        equity += pnl
        trade.append({"type": "SELL", "price": close[-1], "pnl": pnl})

    return pack(equity, curve, trade, wins, losses, fig)


# =========================
# MACD（純 numpy）
# =========================
def ema(series, span):
    return pd.Series(series).ewm(span=span, adjust=False).mean().values


def run_macd_strategy(df):

    k = build_kbar(df)
    close = k["close"]

    ema12 = ema(close, 12)
    ema26 = ema(close, 26)

    macd = ema12 - ema26
    signal = ema(macd, 9)

    equity = 0
    curve = []
    trade = []

    pos = 0
    entry = 0
    wins = losses = 0

    fig, ax = plt.subplots()
    ax.plot(macd, label="MACD")
    ax.plot(signal, label="Signal")
    ax.legend()

    for i in range(1, len(close)):

        if pos == 0 and macd[i] > signal[i] and macd[i-1] <= signal[i-1]:
            pos = 1
            entry = close[i]
            trade.append({"time": k["time"][i], "type": "BUY", "price": entry})

        elif pos == 1 and macd[i] < signal[i] and macd[i-1] >= signal[i-1]:
            pnl = close[i] - entry
            equity += pnl
            pos = 0

            trade.append({"time": k["time"][i], "type": "SELL", "price": close[i], "pnl": pnl})

            wins += pnl > 0
            losses += pnl <= 0

        curve.append(equity)

    if pos == 1:
        pnl = close[-1] - entry
        equity += pnl

    return pack(equity, curve, trade, wins, losses, fig)


# =========================
# RSI（純 numpy）
# =========================
def calc_rsi(close, period=14):

    delta = np.diff(close, prepend=close[0])
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = pd.Series(gain).rolling(period).mean()
    avg_loss = pd.Series(loss).rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi.values


def run_rsi_strategy(df):

    k = build_kbar(df)
    close = k["close"]

    rsi = calc_rsi(close)

    equity = 0
    curve = []
    trade = []

    pos = 0
    entry = 0
    wins = losses = 0

    fig, ax = plt.subplots()
    ax.plot(rsi)
    ax.axhline(70, color="red")
    ax.axhline(30, color="green")

    for i in range(1, len(close)):

        if rsi[i] < 30 and pos == 0:
            pos = 1
            entry = close[i]
            trade.append({"time": k["time"][i], "type": "BUY", "price": entry})

        elif rsi[i] > 70 and pos == 1:
            pnl = close[i] - entry
            equity += pnl
            pos = 0

            trade.append({"time": k["time"][i], "type": "SELL", "price": close[i], "pnl": pnl})

            wins += pnl > 0
            losses += pnl <= 0

        curve.append(equity)

    if pos == 1:
        equity += close[-1] - entry

    return pack(equity, curve, trade, wins, losses, fig)


# =========================
# 布林通道
# =========================
def bollinger(close, period=20):

    mid = pd.Series(close).rolling(period).mean()
    std = pd.Series(close).rolling(period).std()

    upper = mid + 2 * std
    lower = mid - 2 * std

    return upper.values, mid.values, lower.values


def run_bollinger_strategy(df):

    k = build_kbar(df)
    close = k["close"]

    upper, mid, lower = bollinger(close)

    equity = 0
    curve = []
    trade = []

    pos = 0
    entry = 0
    wins = losses = 0

    fig, ax = plt.subplots()
    ax.plot(close)
    ax.plot(upper)
    ax.plot(lower)

    for i in range(1, len(close)):

        if close[i] < lower[i] and pos == 0:
            pos = 1
            entry = close[i]
            trade.append({"time": k["time"][i], "type": "BUY", "price": entry})

        elif close[i] > upper[i] and pos == 1:
            pnl = close[i] - entry
            equity += pnl
            pos = 0

            trade.append({"time": k["time"][i], "type": "SELL", "price": close[i], "pnl": pnl})

            wins += pnl > 0
            losses += pnl <= 0

        curve.append(equity)

    if pos == 1:
        equity += close[-1] - entry

    return pack(equity, curve, trade, wins, losses, fig)


# =========================
# 共用
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


def max_drawdown(curve):
    peak = -1e9
    mdd = 0
    for x in curve:
        peak = max(peak, x)
        mdd = max(mdd, peak - x)
    return mdd


def sharpe_ratio(curve):
    r = pd.Series(curve).diff().fillna(0)
    return 0 if r.std() == 0 else r.mean() / r.std()


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

            result = run_ma_strategy(df, s, l)

            score = result["sharpe"] * 100 + result["profit"] - result["mdd"] * 2

            if score > best_score:
                best_score = score
                best = result
                best_params = (s, l)

    return best, best_params, best_score
