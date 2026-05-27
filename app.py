import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ===== safe import（防炸）=====
try:
    from strategy import (
        run_ma_strategy,
        run_macd_strategy,
        run_kdj_strategy,
        run_rsi_strategy,
        run_bollinger_strategy,
        strategy_rank
    )
except:
    st.error("strategy import failed")
    st.stop()


st.set_page_config(layout="wide")
st.title("📊 最穩量化回測系統")


# =========================
# load data
# =========================
df = pd.read_excel("kbars_1d_2330_2020-01-02_To_2025-03-04.xlsx")
df["time"] = pd.to_datetime(df["time"])


# =========================
# date filter（safe）
# =========================
start = pd.to_datetime(st.sidebar.date_input("開始", "2022-01-01"))
end = pd.to_datetime(st.sidebar.date_input("結束", "2025-03-04"))

df = df[(df["time"] >= start) & (df["time"] <= end)]


# =========================
# run
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
    # ranking safe
    # =========================
    st.subheader("🏆 策略排行榜")

    ranking = strategy_rank(results)
    st.dataframe(pd.DataFrame(ranking))


    if len(ranking) > 0:
        best = ranking[0]["strategy"]
        st.success(f"最佳策略：{best}")

        r = results[best]

        col1, col2, col3 = st.columns(3)
        col1.metric("Profit", round(r["profit"], 2))
        col2.metric("Winrate", f"{r['winrate']*100:.2f}%")
        col3.metric("MDD", round(r["mdd"], 2))

        st.metric("Sharpe", round(r["sharpe"], 2))

        st.pyplot(r["fig"])

        fig2, ax2 = plt.subplots()
        ax2.plot(r["equity_curve"])
        st.pyplot(fig2)

        st.dataframe(pd.DataFrame(r["trade_record"]))
