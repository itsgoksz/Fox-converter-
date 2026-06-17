from dbfread import DBF
import pandas as pd
import streamlit as st

df = pd.DataFrame(list(DBF("itemmast.dbf")))

st.title("FoxPro Table Browser")

st.dataframe(df, use_container_width=True, height=700)
