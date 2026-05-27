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
try:
    df = pd.read_excel("kbars_1d_2330_2020-01-02_To_2025-03-04.xlsx")
    st.success("資料讀取成功")
except Exception as e:
    st.error(f"讀取失敗: {e}")
    st.stop()

st.dataframe(df.head())


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
    # 績效
    # =========================
    st.subheader("回測績效")

    col1, col2, col3 = st.columns(3)

    col1.metric("淨利", round(result["profit"], 2))
    col2.metric("勝率", f"{result['winrate']*100:.2f}%")
    col3.metric("最大回撤", round(result["mdd"], 2))

    st.metric("Sharpe", round(result["sharpe"], 2))


    # =========================
    # 圖
    # =========================
    st.subheader("策略圖")
    st.pyplot(result["fig"])

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


    csv = trade_df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "下載交易紀錄",
        csv,
        "trade.csv",
        "text/csv"
    )


    # =========================
    # AI分析
    # =========================
    st.subheader("AI策略分析")

    text = f"""
策略分析：

- 淨利：{result['profit']}
- 勝率：{result['winrate']:.2%}
- 最大回撤：{result['mdd']}
- Sharpe：{result['sharpe']:.2f}

結論：
"""

    if result["sharpe"] > 1:
        text += "策略表現良好（風險報酬佳）"
    elif result["sharpe"] > 0.5:
        text += "策略普通，可優化"
    else:
        text += "策略偏弱，建議調整"

    st.write(text)
