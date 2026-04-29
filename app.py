import streamlit as st
from tabs import materials, total_loss, customers

st.set_page_config(
    page_title="All County Collision Dashboard",
    page_icon="",
    layout="wide"
)

st.title("All County Collision — Dashboard")
st.markdown("---")

tab1, tab2, tab3 = st.tabs([
    "  Materials Comparator",
    "  Customer Database",
    " Storage & Fees Calculator"
])

with tab1:
    materials.show()

with tab2:
    customers.show()

with tab3:
    total_loss.show()