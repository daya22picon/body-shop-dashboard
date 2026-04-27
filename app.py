import streamlit as st

st.set_page_config(
    page_title="All County Collision Dashboard",
    layout="wide"
)

st.title("All County Collision — Dashboard")
st.markdown("---")

tab1, tab2, tab3 = st.tabs([
    "Materials Comparator",
    "Customer Database",
    "Storage & Fees Calculator"
])

with tab1:
    st.header("Tab 1 coming soon")

with tab2:
    st.header("Tab 2 coming soon")

with tab3:
    st.header("Tab 3 coming soon")