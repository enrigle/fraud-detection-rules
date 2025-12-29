import streamlit as st

st.set_page_config(
    page_title="Audit Log",
    page_icon="📜",
    layout="wide"
)

# Sidebar
with st.sidebar:
    st.title("📜 Audit Log")
    st.markdown("---")
    st.markdown("### Navigation")
    st.page_link("app.py", label="🔧 Rule Builder")
    st.page_link("pages/1_📊_Dashboard.py", label="📊 Dashboard")
    st.page_link("pages/2_🧪_Test_Transactions.py", label="🧪 Test Transactions")
    st.page_link("pages/3_📜_Audit_Log.py", label="📜 Audit Log", icon="🏠")

st.title("📜 Audit Log")

st.info("🚧 Audit log features coming in Phase 5")

st.markdown("""
**Planned features:**
- Session-based transaction history
- Decision timeline
- Filter and search
- Export audit trail
""")
