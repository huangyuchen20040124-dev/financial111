import streamlit as st
        "最大回落",
        round(result['mdd'], 2)
    )


    ################################################
    # K線圖
    ################################################

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


    ################################################
    # 策略圖
    ################################################

    st.subheader("策略指標圖")
    st.pyplot(result['fig'])


    ################################################
    # Equity Curve
    ################################################

    st.subheader("Equity Curve")

    fig2, ax2 = plt.subplots(figsize=(10, 4))

    ax2.plot(result['equity_curve'])

    ax2.set_title("Equity Curve")
    ax2.set_xlabel("Trade")
    ax2.set_ylabel("Profit")

    st.pyplot(fig2)


    ################################################
    # 交易紀錄
    ################################################

    st.subheader("交易紀錄")

    trade_df = pd.DataFrame(result['trade_record'])

    st.dataframe(trade_df)


    ################################################
    # 下載CSV
    ################################################

    csv = trade_df.to_csv(index=False).encode('utf-8-sig')

    st.download_button(
        label="下載交易紀錄CSV",
        data=csv,
        file_name='trade_record.csv',
        mime='text/csv'
    )
