import json
import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")

with open("report_definition.json") as f:
    report = json.load(f)

st.title("FoxPro Report Explorer")

st.subheader(report["report_name"])

st.metric("Objects", report["object_count"])

df = pd.DataFrame(report["objects"])

st.dataframe(df, use_container_width=True, height=700)
