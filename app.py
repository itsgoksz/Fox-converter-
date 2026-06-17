import streamlit as st

st.set_page_config(
    page_title="FoxPro Reporting Portal",
    page_icon="🦊",
    layout="wide"
)

st.title("🦊 FoxPro Replica: Reporting Portal")
st.markdown("""
Welcome to the live FoxPro Reporting Portal. 

Please use the **navigation menu on the left sidebar** to seamlessly switch between your generated reports:
- **Sale Typewise Report**
- **Purchase Typewise Report**

All reports are wired directly into `TRAN1.DB` and calculate 100% dynamically in real-time.
""")
