import streamlit as st
import pandas as pd

from strategy import run_ma_strategy

st.title("量化交易回測系統")

df = pd.read_pickle(
    "kbars_2330_2022-01-01-2024-04-09.pkl"
)

if st.button("開始回測"):

    result = run_ma_strategy(df)

    st.write("淨利:", result["profit"])
    st.write("勝率:", result["winrate"])
    st.write("最大回落:", result["mdd"])

    st.pyplot(result["fig"])
