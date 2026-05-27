# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
st.set_page_config(
    page_title='量化交易回測系統',
    layout='wide'
)

st.title('台積電量化交易回測系統')


# 讀取資料
@st.cache_data

def load_data():
    df = pd.read_excel(
        'kbars_1d_2330_2020-01-02_To_2025-03-04.xlsx'
    )
    return df


try:
    df = load_data()

    st.success('資料載入成功')

    st.write(df.head())

except Exception as e:
    st.error(f'資料讀取失敗: {e}')
    st.stop()


# 側邊欄
strategy = st.sidebar.selectbox(
    '選擇策略',
    [
        'MA 均線策略',
        'RSI 順勢策略',
        '布林通道策略'
    ]
)


if st.button('開始回測'):

    if strategy == 'MA 均線策略':
        result = run_ma_strategy(df)

    elif strategy == 'RSI 順勢策略':
        result = run_rsi_strategy(df)

    elif strategy == '布林通道策略':
        result = run_bbands_strategy(df)


    st.subheader('回測結果')

    col1, col2, col3 = st.columns(3)

    col1.metric('淨利', result['profit'])
    col2.metric('勝率', result['winrate'])
    col3.metric('最大回落', result['mdd'])


    st.pyplot(result['fig'])
