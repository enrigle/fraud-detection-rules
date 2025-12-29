import streamlit as st

st.set_page_config(
    page_title="Test Transactions",
    page_icon="🧪",
    layout="wide"
)

# Sidebar
with st.sidebar:
    st.title("🧪 Test Transactions")
    st.markdown("---")
    st.markdown("### Navigation")
    st.page_link("app.py", label="🔧 Rule Builder")
    st.page_link("pages/1_📊_Dashboard.py", label="📊 Dashboard")
    st.page_link("pages/2_🧪_Test_Transactions.py", label="🧪 Test Transactions", icon="🏠")
    st.page_link("pages/3_📜_Audit_Log.py", label="📜 Audit Log")

st.title("🧪 Test Transactions")

st.info("🚧 Transaction testing features coming in Phase 4")

st.markdown("""
**Planned features:**
- Upload CSV files
- Generate sample transactions
- Preview and select rows to test
- Run through rule engine
- Display results with on-demand LLM explanations
- Export results
""")
