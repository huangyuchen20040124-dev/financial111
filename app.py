import streamlit as st
import pandas as pd

from strategy import (
    run_ma_strategy,
    run_rsi_strategy,
    run_macd_strategy,
    run_kdj_strategy
)

st.set_page_config(
    page_title="量化交易回測系統",
    layout="wide"
)

st.title("台積電量化交易回測系統")

# 讀資料
df = pd.read_excel(
    "kbars_1d_2330_2020-01-02_To_2025-03-04.xlsx"
)

st.write(df.head())

# 選擇策略
strategy_name = st.sidebar.selectbox(
    "選擇策略",
    [
        "MA策略",
        "RSI策略",
        "MACD策略",
        "KDJ策略"
    ]
)

# 執行回測
if st.button("開始回測"):

    if strategy_name == "MA策略":
        result = run_ma_strategy(df)

    elif strategy_name == "RSI策略":
        result = run_rsi_strategy(df)

    elif strategy_name == "MACD策略":
        result = run_macd_strategy(df)

    elif strategy_name == "KDJ策略":
        result = run_kdj_strategy(df)

    st.subheader("回測結果")

    col1, col2, col3 = st.columns(3)

    col1.metric("淨利", result["profit"])
    col2.metric("勝率", result["winrate"])
    col3.metric("最大回落", result["mdd"])

    st.pyplot(result["fig"])
