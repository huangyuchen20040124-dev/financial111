from strategy import (
    run_ma_strategy,
    run_macd_strategy,
    run_kdj_strategy,
    run_rsi_strategy,
    run_bollinger_strategy


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

        # ✔ 防止未來函數（i-1）
        if buy[i-1] and pos == 0:
            pos = 1
            entry = close[i]
            trade.append({"type": "BUY", "price": entry})

        elif sell[i-1] and pos == 1:
            pnl = close[i] - entry
            equity += pnl
            pos = 0

            trade.append({"type": "SELL", "price": close[i], "pnl": pnl})

            wins += pnl > 0
            losses += pnl <= 0

        curve.append(equity)

    # 強制平倉
    if pos == 1:
        equity += close[-1] - entry

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
# RSI策略
# =========================
def run_rsi_strategy(df):
    close, _, _ = build_kbar(df)
    rsi = RSI(close)
    return backtest(close, rsi < 30, rsi > 70, "RSI")


# =========================
# MACD策略
# =========================
def run_macd_strategy(df):
    close, _, _ = build_kbar(df)
    macd, sig = MACD(close)
    return backtest(close, macd > sig, macd < sig, "MACD")


# =========================
# MA策略
# =========================
def run_ma_strategy(df):
    close, _, _ = build_kbar(df)
    sma_s = SMA(close, 5)
    sma_l = SMA(close, 20)
    return backtest(close, sma_s > sma_l, sma_s < sma_l, "MA")


# =========================
# BB策略
# =========================
def run_bollinger_strategy(df):
    close, _, _ = build_kbar(df)
    upper, mid, lower = BBANDS(close)
    return backtest(close, close < lower, close > upper, "BB")


# =========================
# KDJ（簡化版）
# =========================
def run_kdj_strategy(df):
    close, high, low = build_kbar(df)

    low_min = pd.Series(low).rolling(9).min()
    high_max = pd.Series(high).rolling(9).max()

    rsv = (close - low_min) / (high_max - low_min + 1e-9)
    k = pd.Series(rsv).rolling(3).mean().fillna(0).values

    return backtest(close, k < 0.2, k > 0.8, "KDJ")


# =========================
# 指標
# =========================
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
    return np.mean(r) / (np.std(r) + 1e-9)
