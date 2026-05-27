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
st.set_page_config(page_title="回測系統", layout="wide")
st.title("📊 台積電交易回測系統")

# =========================
df = pd.read_excel("kbars_1d_2330_2020-01-02_To_2025-03-04.xlsx")
df["time"] = pd.to_datetime(df["time"])

start = st.sidebar.date_input("開始日期")
end = st.sidebar.date_input("結束日期")

df = df[(df["time"] >= pd.to_datetime(start)) &
        (df["time"] <= pd.to_datetime(end))]

# =========================
strategy = st.sidebar.selectbox(
    "選擇策略",
    ["MA策略", "MACD策略", "KDJ策略", "RSI策略", "布林通道策略"]
)

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

    st.metric("Profit", round(result["profit"], 2))
    st.metric("Winrate", f"{result['winrate']*100:.2f}%")
    st.metric("MDD", round(result["mdd"], 2))
    st.metric("Sharpe", round(result["sharpe"], 2))

    st.pyplot(result["fig"])

    st.subheader("Equity Curve")
    fig2, ax2 = plt.subplots()
    ax2.plot(result["equity_curve"])
    st.pyplot(fig2)

    st.subheader("交易紀錄")
    st.dataframe(pd.DataFrame(result["trade_record"]))
