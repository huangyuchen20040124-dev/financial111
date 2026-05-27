import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf

from strategy import (
    run_ma_strategy,
    run_rsi_strategy,
    run_macd_strategy,
    run_kdj_strategy
)

################################################
# 頁面設定
################################################

st.set_page_config(
    page_title="量化交易回測系統",
    layout="wide"
)

st.title("台積電量化交易回測系統")

################################################
# 讀取資料
################################################

try:

    df = pd.read_excel(
        "kbars_1d_2330_2020-01-02_To_2025-03-04.xlsx"
    )

    st.success("資料讀取成功")

except Exception as e:

    st.error(f"資料讀取失敗: {e}")
    st.stop()

################################################
# 顯示資料
################################################

st.subheader("KBar資料")

st.dataframe(df.head())

################################################
# 側邊欄
################################################

strategy_name = st.sidebar.selectbox(
    "選擇策略",
    [
        "MA策略",
        "RSI策略",
        "MACD策略",
        "KDJ策略"
    ]
)

################################################
# 開始回測
################################################

if st.button("開始回測"):

    ################################################
    # 執行策略
    ################################################

    if strategy_name == "MA策略":

        result = run_ma_strategy(df)

    elif strategy_name == "RSI策略":

        result = run_rsi_strategy(df)

    elif strategy_name == "MACD策略":

        result = run_macd_strategy(df)

    elif strategy_name == "KDJ策略":

        result = run_kdj_strategy(df)

    ################################################
    # 回測績效
    ################################################

    st.subheader("回測結果")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "淨利",
        round(result["profit"], 2)
    )

    col2.metric(
        "勝率",
        f"{round(result['winrate'] * 100, 2)}%"
    )

    col3.metric(
        "最大回落",
        round(result["mdd"], 2)
    )

    ################################################
    # K線圖
    ################################################

    st.subheader("K線圖")

    chart_df = df.copy()

    chart_df['time'] = pd.to_datetime(
        chart_df['time']
    )

    chart_df.set_index(
        'time',
        inplace=True
    )

    fig, axlist = mpf.plot(
        chart_df,
        type='candle',
        volume=True,
        style='charles',
        returnfig=True
    )

    st.pyplot(fig)

    ################################################
    # 策略圖
    ################################################

    st.subheader("策略指標圖")

    st.pyplot(result['fig'])

    ################################################
    # Equity Curve
    ################################################

    st.subheader("Equity Curve")

    fig2, ax2 = plt.subplots(
        figsize=(10, 4)
    )

    ax2.plot(result['equity_curve'])

    ax2.set_title("Equity Curve")
    ax2.set_xlabel("Trade")
    ax2.set_ylabel("Profit")

    st.pyplot(fig2)

    ################################################
    # 交易紀錄
    ################################################

    st.subheader("交易紀錄")

    trade_df = pd.DataFrame(
        result['trade_record']
    )

    st.dataframe(trade_df)

    ################################################
    # 下載CSV
    ################################################

    csv = trade_df.to_csv(
        index=False
    ).encode('utf-8-sig')

    st.download_button(
        label="下載交易紀錄CSV",
        data=csv,
        file_name='trade_record.csv',
        mime='text/csv'
    )
