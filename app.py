import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from strategy import (
    run_ma_strategy,
    run_macd_strategy,
    run_kdj_strategy,
    optimize_ma,
    strategy_rank
)

# =========================
# 基本設定
# =========================
st.set_page_config(page_title="量化回測系統", layout="wide")
st.title("台積電量化交易回測系統")

# =========================
# 讀資料
# =========================
df = pd.read_excel("kbars_1d_2330_2020-01-02_To_2025-03-04.xlsx")
df["time"] = pd.to_datetime(df["time"])

# =========================
# 日期區間
# =========================
st.sidebar.subheader("時間區間")

start = st.sidebar.date_input("開始日期", pd.to_datetime("2022-01-01"))
end = st.sidebar.date_input("結束日期", pd.to_datetime("2025-03-04"))

df = df[(df["time"] >= pd.to_datetime(start)) &
        (df["time"] <= pd.to_datetime(end))]

# =========================
# 策略選擇
# =========================
strategy = st.sidebar.selectbox(
    "選擇策略",
    ["MA策略", "MACD策略", "KDJ策略"]
)

use_opt = st.sidebar.checkbox("啟用MA最佳化")

# =========================
# 回測
# =========================
if st.button("開始回測"):

    results = {}

    # ===== MA =====
    if strategy == "MA策略":

        if use_opt:
            result, params, score = optimize_ma(df)
            st.success(f"最佳MA：{params}")
            st.info(f"最佳分數：{score:.4f}")
        else:
            result = run_ma_strategy(df)

        results["MA策略"] = result

    # ===== MACD =====
    elif strategy == "MACD策略":
        result = run_macd_strategy(df)
        results["MACD策略"] = result

    # ===== KDJ =====
    else:
        result = run_kdj_strategy(df)
        results["KDJ策略"] = result

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
    st.pyplot(fig2)

    # =========================
    # 交易紀錄
    # =========================
    st.subheader("交易紀錄")

    trade_df = pd.DataFrame(result["trade_record"])
    st.dataframe(trade_df)

    st.download_button(
        "下載CSV",
        trade_df.to_csv(index=False).encode("utf-8-sig"),
        "trade.csv",
        "text/csv"
    )

    # =========================
    # AI分析
    # =========================
    st.subheader("AI策略分析")

    text = f"""
- 淨利：{result['profit']}
- 勝率：{result['winrate']:.2%}
- 最大回撤：{result['mdd']}
- Sharpe：{result['sharpe']:.2f}
"""

    if result["sharpe"] > 1:
        text += "\n✔ 策略優秀"
    elif result["sharpe"] > 0.5:
        text += "\n⚠ 策略普通"
    else:
        text += "\n❌ 策略較弱"

    st.write(text)

    # =========================
    # 排行榜（單策略版本）
    # =========================
    st.subheader("策略排行榜")

    ranking = strategy_rank(results)
    rank_df = pd.DataFrame(ranking)

    st.dataframe(rank_df)

    best = ranking[0]["strategy"]
    st.success(f"最佳策略：{best}")

    best_result = results[best]

    col1, col2, col3 = st.columns(3)
    col1.metric("Profit", round(best_result["profit"], 2))
    col2.metric("Winrate", f"{best_result['winrate']*100:.2f}%")
    col3.metric("MDD", round(best_result["mdd"], 2))

    st.metric("Sharpe", round(best_result["sharpe"], 2))

    st.pyplot(best_result["fig"])

    fig3, ax3 = plt.subplots()
    ax3.plot(best_result["equity_curve"])
    st.pyplot(fig3)

    st.subheader("交易紀錄")
    st.dataframe(pd.DataFrame(best_result["trade_record"]))
