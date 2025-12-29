import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config_manager import ConfigManager
from src.visualizer import RuleVisualizer

st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide"
)

# Sidebar
with st.sidebar:
    st.title("📊 Dashboard")
    st.markdown("---")
    st.markdown("### Navigation")
    st.page_link("app.py", label="🔧 Rule Builder")
    st.page_link("pages/1_📊_Dashboard.py", label="📊 Dashboard", icon="🏠")
    st.page_link("pages/2_🧪_Test_Transactions.py", label="🧪 Test Transactions")
    st.page_link("pages/3_📜_Audit_Log.py", label="📜 Audit Log")

# Main content
st.title("📊 Fraud Detection Dashboard")

# Coming soon placeholder
st.info("🚧 Dashboard features coming in Phase 3")

st.markdown("""
**Planned features:**
- Interactive decision tree visualization
- Rule management (view, edit, delete, reorder)
- Summary statistics
- Analytics charts
""")

# Show current rules as table for now
try:
    config_mgr = ConfigManager()
    config = config_mgr.load_rules()
    rules = config.get('rules', [])

    st.subheader(f"Current Rules ({len(rules)})")

    for idx, rule in enumerate(rules, 1):
        with st.expander(f"{idx}. {rule.get('name', 'Unnamed')} (`{rule.get('id', '')}`)", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Decision:** {rule.get('outcome', {}).get('decision', 'N/A')}")
                st.markdown(f"**Risk Score:** {rule.get('outcome', {}).get('risk_score', 0)}/100")
            with col2:
                st.markdown(f"**Logic:** {rule.get('logic', 'N/A')}")
                st.markdown(f"**Conditions:** {len(rule.get('conditions', []))}")

            st.markdown(f"**Reason:** {rule.get('outcome', {}).get('reason', 'N/A')}")

            if rule.get('conditions'):
                st.markdown("**Conditions:**")
                for cond in rule['conditions']:
                    st.markdown(f"- `{cond.get('field')}` {cond.get('operator')} `{cond.get('value')}`")

except FileNotFoundError:
    st.warning("⚠️ No rules file found. Create your first rule using the Rule Builder!")
except Exception as e:
    st.error(f"Error loading rules: {str(e)}")
