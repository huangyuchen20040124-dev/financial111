if st.button("開始回測"):

    if strategy_name == "MA策略":
        result = run_ma_strategy(df)

    elif strategy_name == "RSI策略":
        result = run_rsi_strategy(df)

    elif strategy_name == "MACD策略":
        result = run_macd_strategy(df)

    elif strategy_name == "KDJ策略":
        result = run_kdj_strategy(df)

    # =========================
    # 績效
    # =========================
    st.subheader("回測結果")

    col1, col2, col3 = st.columns(3)

    col1.metric("淨利", round(result["profit"], 2))
    col2.metric("勝率", f"{round(result['winrate'] * 100, 2)}%")
    col3.metric("最大回撤", round(result["mdd"], 2))

    st.metric("Sharpe", round(result["sharpe"], 2))

    # =========================
    # K線圖
    # =========================
    st.subheader("K線圖")

    chart_df = df.copy()
    chart_df['time'] = pd.to_datetime(chart_df['time'])
    chart_df.set_index('time', inplace=True)

    fig, axlist = mpf.plot(
        chart_df,
        type='candle',
        volume=True,
        style='charles',
        returnfig=True
    )

    st.pyplot(fig)

    # =========================
    # 策略圖
    # =========================
    st.subheader("策略指標圖")
    st.pyplot(result['fig'])

    # =========================
    # Equity Curve
    # =========================
    st.subheader("Equity Curve")

    fig2, ax2 = plt.subplots(figsize=(10, 4))
    ax2.plot(result['equity_curve'])
    ax2.set_title("Equity Curve")
    ax2.set_xlabel("Trade")
    ax2.set_ylabel("Profit")

    st.pyplot(fig2)

    # =========================
    # 交易紀錄
    # =========================
    st.subheader("交易紀錄")

    trade_df = pd.DataFrame(result['trade_record'])
    st.dataframe(trade_df)

    csv = trade_df.to_csv(index=False).encode('utf-8-sig')

    st.download_button(
        label="下載交易紀錄CSV",
        data=csv,
        file_name='trade_record.csv',
        mime='text/csv'
    )

    # =========================
    # AI分析
    # =========================
    st.subheader("📊 AI策略分析")

    analysis = f"""
策略結果分析：

- 淨利：{result['profit']}
- 勝率：{result['winrate']:.2%}
- 最大回撤：{result['mdd']}
- Sharpe：{result['sharpe']:.2f}

👉 簡易判斷：
"""

    if result["sharpe"] > 1:
        analysis += "此策略風險報酬比佳，可視為有效策略。"
    elif result["sharpe"] > 0.5:
        analysis += "策略普通，有優化空間。"
    else:
        analysis += "策略風險較高或不穩定。"

    st.write(analysis)
