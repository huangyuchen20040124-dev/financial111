import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from strategy import (
    run_ma_strategy,
    run_macd_strategy,
    run_kdj_strategy,
    run_rsi_strategy,
    run_bollinger_strategy,
    strategy_rank
)

st.set_page_config(layout="wide")
st.title("📊 量化交易回測系統")


# =========================
# 讀資料
# =========================
df = pd.read_excel("kbars_1d_2330_2020-01-02_To_2025-03-04.xlsx")
df["time"] = pd.to_datetime(df["time"])


# =========================
# 日期（已修正）
# =========================
start = pd.to_datetime(st.sidebar.date_input("開始日期", "2022-01-01"))
end = pd.to_datetime(st.sidebar.date_input("結束日期", "2025-03-04"))

df = df[(df["time"] >= start) & (df["time"] <= end)]


# =========================
# 回測
# =========================
if st.button("開始回測"):

    results = {
        "MA": run_ma_strategy(df),
        "MACD": run_macd_strategy(df),
        "KDJ": run_kdj_strategy(df),
        "RSI": run_rsi_strategy(df),
        "BB": run_bollinger_strategy(df)
    }


    # =========================
    # 🏆 排行榜
    # =========================
    st.subheader("策略排行榜")

    ranking = strategy_rank(results)
    rank_df = pd.DataFrame(ranking)

    st.dataframe(rank_df)

    best = ranking[0]["strategy"]
    st.success(f"最佳策略：{best}")


    # =========================
    # 顯示最佳策略
    # =========================
    result = results[best]

    col1, col2, col3 = st.columns(3)
    col1.metric("Profit", round(result["profit"], 2))
    col2.metric("Winrate", f"{result['winrate']*100:.2f}%")
    col3.metric("MDD", round(result["mdd"], 2))

    st.metric("Sharpe", round(result["sharpe"], 2))

    st.pyplot(result["fig"])


    fig2, ax2 = plt.subplots()
    ax2.plot(result["equity_curve"])
    st.pyplot(fig2)


    st.subheader("交易紀錄")
    st.dataframe(pd.DataFrame(result["trade_record"]))
