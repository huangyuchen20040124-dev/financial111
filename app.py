import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf

from strategy import (
    run_ma_strategy,
    run_macd_strategy,
    run_kdj_strategy
)

# =========================
# UI設定
# =========================
st.set_page_config(page_title="量化回測系統", layout="wide")
st.title("台積電量化交易回測系統")


# =========================
# 讀資料
# =========================
df = pd.read_excel("kbars_1d_2330_2020-01-02_To_2025-03-04.xlsx")
df["time"] = pd.to_datetime(df["time"])


# =========================
# 📅 日期區間（你要的）
# =========================
st.sidebar.subheader("回測時間設定")

start_date = st.sidebar.date_input(
    "開始日期",
    value=pd.to_datetime("2022-01-01"),
    min_value=pd.to_datetime("2022-01-01"),
    max_value=pd.to_datetime("2025-03-04")
)

end_date = st.sidebar.date_input(
    "結束日期",
    value=pd.to_datetime("2025-03-04"),
    min_value=pd.to_datetime("2022-01-01"),
    max_value=pd.to_datetime("2025-03-04")
)


# 篩選資料
df = df[(df["time"] >= pd.to_datetime(start_date)) &
        (df["time"] <= pd.to_datetime(end_date))]


st.write(f"回測區間：{start_date} ~ {end_date}")


# =========================
# 📊 K棒設定（你要的）
# =========================
st.sidebar.subheader("K棒設定")

kbar_unit = st.sidebar.selectbox(
    "K棒時間單位",
    ["日K"]
)

kbar_length = st.sidebar.number_input(
    "一根K棒時間長度（天）",
    min_value=1,
    max_value=30,
    value=1
)


st.info(f"目前設定：{kbar_unit}，{kbar_length} 天K")


# =========================
# 策略選擇
# =========================
strategy = st.sidebar.selectbox(
    "選擇策略",
    ["MA策略", "MACD策略", "KDJ策略"]
)


# =========================
# 回測
# =========================
if st.button("開始回測"):

    if strategy == "MA策略":
        result = run_ma_strategy(df)

    elif strategy == "MACD策略":
        result = run_macd_strategy(df)

    else:
        result = run_kdj_strategy(df)


    # =========================
    # K線圖 + MACD / KDJ（重點）
    # =========================
    st.subheader("K線圖 + 技術指標")


    chart_df = df.copy()
    chart_df.set_index("time", inplace=True)


    # ========= MACD K線圖 =========
    if strategy == "MACD策略":

        macd_fig, ax = plt.subplots()

        mpf.plot(
            chart_df,
            type='candle',
            style='charles',
            volume=True,
            addplot=[
                mpf.make_addplot(result["fig"].axes[0].lines[0].get_ydata(), color='r'),
                mpf.make_addplot(result["fig"].axes[0].lines[1].get_ydata(), color='b')
            ],
            ax=ax,
            returnfig=False
        )

        st.pyplot(macd_fig)


    # ========= KDJ K線圖 =========
    elif strategy == "KDJ策略":

        kdj_fig, ax = plt.subplots()

        mpf.plot(
            chart_df,
            type='candle',
            style='charles',
            volume=True,
            ax=ax
        )

        st.pyplot(kdj_fig)


    # ========= MA（一般K線） =========
    else:

        fig, _ = mpf.plot(
            chart_df,
            type='candle',
            volume=True,
            style='charles',
            returnfig=True
        )

        st.pyplot(fig)


    # =========================
    # 績效
    # =========================
    st.subheader("回測績效")

    col1, col2, col3 = st.columns(3)

    col1.metric("淨利", round(result["profit"], 2))
    col2.metric("勝率", f"{result['winrate']*100:.2f}%")
    col3.metric("最大回撤", round(result["mdd"], 2))

    st.metric("Sharpe", round(result["sharpe"], 2))


    # =========================
    # Equity Curve
    # =========================
    st.subheader("Equity Curve")

    fig2, ax2 = plt.subplots()
    ax2.plot(result["equity_curve"])
    ax2.set_title("Equity Curve")

    st.pyplot(fig2)


    # =========================
    # 交易紀錄
    # =========================
    st.subheader("交易紀錄")

    trade_df = pd.DataFrame(result["trade_record"])
    st.dataframe(trade_df)

    st.download_button(
        "下載交易紀錄",
        trade_df.to_csv(index=False).encode("utf-8-sig"),
        "trade.csv",
        "text/csv"
    )


    # =========================
    # AI分析
    # =========================
    st.subheader("AI策略分析")

    analysis = f"""
策略分析：

- 淨利：{result['profit']}
- 勝率：{result['winrate']:.2%}
- 最大回撤：{result['mdd']}
- Sharpe：{result['sharpe']:.2f}

結論：
"""

    if result["sharpe"] > 1:
        analysis += "策略表現良好（風險報酬佳）"
    elif result["sharpe"] > 0.5:
        analysis += "策略普通，可優化"
    else:
        analysis += "策略偏弱，建議調整"

    st.write(analysis)
