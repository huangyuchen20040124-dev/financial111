import streamlit as st
import pandas as pd

from strategy import run_ma_strategy

st.title("量化交易回測系統")

df = pd.read_excel(
    "kbars_1d_2330_2020-01-02_To_2025-03-04.xlsx"
)

st.write(df.head())

if st.button("開始回測"):

    result = run_ma_strategy(df)

    st.write("淨利:", result["profit"])
    st.write("勝率:", result["winrate"])
    st.write("最大回落:", result["mdd"])

    st.pyplot(result["fig"])
