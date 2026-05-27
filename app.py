
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from talib import MACD, STOCH

st.title("📈 程式交易回測系統")
st.write("MACD 與 KDJ 策略回測")

uploaded_file = st.file_uploader("請上傳股票資料 CSV", type=["csv"])

strategy = st.selectbox(
    "選擇策略",
    ["MACD", "KDJ"]
)

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    st.subheader("原始資料")
    st.dataframe(df.head())

    close = df['close']
    high = df['high']
    low = df['low']

    # =========================
    # MACD
    # =========================
    if strategy == "MACD":

        macd, signal, hist = MACD(
            close,
            fastperiod=12,
            slowperiod=26,
            signalperiod=9
        )

        df['MACD'] = macd
        df['Signal'] = signal

        st.subheader("MACD 指標")

        fig, ax = plt.subplots()
        ax.plot(df['MACD'], label='MACD')
        ax.plot(df['Signal'], label='Signal')
        ax.legend()

        st.pyplot(fig)

        trade_log = []

        position = 0

        for i in range(1, len(df)):

            if np.isnan(df['MACD'][i]):
                continue

            # 黃金交叉
            if position == 0 and \
               df['MACD'][i-1] < df['Signal'][i-1] and \
               df['MACD'][i] > df['Signal'][i]:

                trade_log.append(
                    f"Buy at {df['close'][i]}"
                )

                position = 1

            # 死亡交叉
            elif position == 1 and \
                 df['MACD'][i-1] > df['Signal'][i-1] and \
                 df['MACD'][i] < df['Signal'][i]:

                trade_log.append(
                    f"Sell at {df['close'][i]}"
                )

                position = 0

        st.subheader("交易紀錄")

        for t in trade_log:
            st.write(t)

    # =========================
    # KDJ
    # =========================
    elif strategy == "KDJ":

        K, D = STOCH(
            high,
            low,
            close,
            fastk_period=9,
            slowk_period=3,
            slowd_period=3
        )

        J = 3 * K - 2 * D

        df['K'] = K
        df['D'] = D
        df['J'] = J

        st.subheader("KDJ 指標")

        fig, ax = plt.subplots()
        ax.plot(df['K'], label='K')
        ax.plot(df['D'], label='D')
        ax.plot(df['J'], label='J')
        ax.legend()

        st.pyplot(fig)

        trade_log = []

        position = 0

        for i in range(1, len(df)):

            if np.isnan(df['K'][i]):
                continue

            # 黃金交叉
            if position == 0 and \
               df['K'][i-1] < df['D'][i-1] and \
               df['K'][i] > df['D'][i]:

                trade_log.append(
                    f"Buy at {df['close'][i]}"
                )

                position = 1

            # 死亡交叉
            elif position == 1 and \
                 df['K'][i-1] > df['D'][i-1] and \
                 df['K'][i] < df['D'][i]:

                trade_log.append(
                    f"Sell at {df['close'][i]}"
                )

                position = 0

        st.subheader("交易紀錄")

        for t in trade_log:
            st.write(t)

st.write("✅ Streamlit App 執行完成")
