import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from strategy import (
    run_ma_strategy,
    run_macd_strategy,
    run_kdj_strategy,
    run_swing_strategy,
    optimize_ma
)

st.set_page_config(page_title="量化回測系統", layout="wide")
st.title("📊 量化交易回測系統")


df = pd.read_excel("kbars_1d_2330_2020-01-02_To_2025-03-04.xlsx")
df["time"] = pd.to_datetime(df["time"])


# 日期
start = st.sidebar.date_input("開始日期", pd.to_datetime("2022-01-01"))
end = st.sidebar.date_input("結束日期", pd.to_datetime("2025-03-04"))

df = df[(df["time"] >= start) & (df["time"] <= end)]


# 策略
strategy = st.sidebar.selectbox(
    "選擇策略",
    ["MA策略", "MACD策略", "KDJ策略", "Swing策略"]
)

use_opt = st.sidebar.checkbox("MA最佳化")


if st.button("開始回測"):

    if strategy == "MA策略":

        if use_opt:
            result, params, score = optimize_ma(df)
            st.success(f"最佳MA: {params}")
        else:
            result = run_ma_strategy(df)

    elif strategy == "MACD策略":
        result = run_macd_strategy(df)

    elif strategy == "KDJ策略":
        result = run_kdj_strategy(df)

    else:
        result = run_swing_strategy(df)


    # 績效
    col1, col2, col3 = st.columns(3)
    col1.metric("Profit", round(result["profit"], 2))
    col2.metric("Winrate", f"{result['winrate']*100:.2f}%")
    col3.metric("MDD", round(result["mdd"], 2))

    st.metric("Sharpe", round(result["sharpe"], 2))

    st.pyplot(result["fig"])


    # Equity
    fig2, ax2 = plt.subplots()
    ax2.plot(result["equity_curve"])
    st.pyplot(fig2)


    # Trade
    st.dataframe(pd.DataFrame(result["trade_record"]))
