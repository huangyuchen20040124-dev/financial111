import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from strategy import (
    run_ma_strategy,
    run_macd_strategy,
    run_kdj_strategy,
    run_rsi_strategy,
    run_bollinger_strategy
)

# =========================
# UI
# =========================
st.set_page_config(page_title="回測系統", layout="wide")
st.title("📊 台積電回測系統")

# =========================
# 讀資料（確保檔案存在）
# =========================
df = pd.read_excel("kbars_1d_2330_2020-01-02_To_2025-03-04.xlsx")
df["time"] = pd.to_datetime(df["time"])

# =========================
# 日期篩選
# =========================
start = st.sidebar.date_input("開始日期", pd.to_datetime("2022-01-01"))
end = st.sidebar.date_input("結束日期", pd.to_datetime("2025-03-04"))

df = df[(df["time"] >= pd.to_datetime(start)) &
        (df["time"] <= pd.to_datetime(end))]

# =========================
# 策略選擇
# =========================
strategy = st.sidebar.selectbox(
    "選擇策略",
    ["MA策略", "MACD策略", "KDJ策略", "RSI策略", "布林通道策略"]
)

# =========================
# 回測
# =========================
if st.button("開始回測"):

    if strategy == "MA策略":
        result = run_ma_strategy(df)

    elif strategy == "MACD策略":
        result = run_macd_strategy(df)

    elif strategy == "KDJ策略":
        result = run_kdj_strategy(df)

    elif strategy == "RSI策略":
        result = run_rsi_strategy(df)

    else:
        result = run_bollinger_strategy(df)

    # =========================
    # 績效
    # =========================
    st.subheader("績效")

    col1, col2, col3 = st.columns(3)
    col1.metric("Profit", round(result["profit"], 2))
    col2.metric("Winrate", f"{result['winrate']*100:.2f}%")
    col3.metric("MDD", round(result["mdd"], 2))

    st.metric("Sharpe", round(result["sharpe"], 2))

    # =========================
    # 圖
    # =========================
    st.subheader("策略圖")
    st.pyplot(result["fig"])

    # =========================
    # Equity Curve
    # =========================
    st.subheader("Equity Curve")
    fig2, ax2 = plt.subplots()
    ax2.plot(result["equity_curve"])
    st.pyplot(fig2)

    # =========================
    # 交易紀錄
    # =========================
    st.subheader("交易紀錄")
    st.dataframe(pd.DataFrame(result["trade_record"]))
