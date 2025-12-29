import streamlit as st
from typing import Dict, Any, List
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config_manager import ConfigManager
from src.data_validator import DataValidator

# Page config
st.set_page_config(
    page_title="Fraud Detection - Rule Builder",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'rule_step' not in st.session_state:
    st.session_state.rule_step = 1
if 'new_rule' not in st.session_state:
    st.session_state.new_rule = {
        'id': '',
        'name': '',
        'conditions': [],
        'logic': 'AND',
        'outcome': {
            'risk_score': 50,
            'decision': 'REVIEW',
            'reason': ''
        }
    }
if 'conditions' not in st.session_state:
    st.session_state.conditions = []

# Initialize managers
config_mgr = ConfigManager()
data_validator = DataValidator()

# Sidebar
with st.sidebar:
    st.title("🔧 Rule Builder")
    st.markdown("---")
    st.markdown("### Navigation")
    st.page_link("app.py", label="🔧 Rule Builder", icon="🏠")
    st.page_link("pages/1_📊_Dashboard.py", label="📊 Dashboard")
    st.page_link("pages/2_🧪_Test_Transactions.py", label="🧪 Test Transactions")
    st.page_link("pages/3_📜_Audit_Log.py", label="📜 Audit Log")

    st.markdown("---")
    st.markdown(f"**Current Step:** {st.session_state.rule_step}/4")

# Main content
st.title("🔧 Fraud Detection Rule Builder")
st.markdown("Create a new fraud detection rule using the step-by-step wizard below.")

# Progress indicator
progress_cols = st.columns(4)
steps = ["Identity", "Conditions", "Logic & Outcome", "Preview"]
for i, (col, step) in enumerate(zip(progress_cols, steps), 1):
    with col:
        if i < st.session_state.rule_step:
            st.success(f"✓ {step}", icon="✅")
        elif i == st.session_state.rule_step:
            st.info(f"→ {step}", icon="▶")
        else:
            st.text(f"  {step}")

st.markdown("---")

# Step 1: Rule Identity
if st.session_state.rule_step == 1:
    st.header("Step 1: Rule Identity")

    col1, col2 = st.columns(2)

    with col1:
        # Generate next rule ID
        try:
            config = config_mgr.load_rules()
            next_id = config_mgr.get_next_rule_id(config)
        except FileNotFoundError:
            next_id = "RULE_001"

        st.text_input(
            "Rule ID",
            value=next_id,
            disabled=True,
            help="Auto-generated unique identifier"
        )
        st.session_state.new_rule['id'] = next_id

    with col2:
        rule_name = st.text_input(
            "Rule Name *",
            value=st.session_state.new_rule.get('name', ''),
            placeholder="e.g., High-value crypto from new device",
            help="Short, descriptive name for this rule"
        )
        st.session_state.new_rule['name'] = rule_name

    description = st.text_area(
        "Description (Optional)",
        placeholder="Explain when this rule should trigger and why...",
        help="Additional context about this rule"
    )

    st.markdown("---")

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Next Step →", type="primary", disabled=not rule_name):
            st.session_state.rule_step = 2
            st.rerun()

# Step 2: Add Conditions
elif st.session_state.rule_step == 2:
    st.header("Step 2: Add Conditions")
    st.markdown("Define what transaction attributes to check.")

    # Get available fields
    field_info = data_validator.get_field_info()
    field_names = list(field_info.keys())

    # Display existing conditions
    if st.session_state.conditions:
        st.subheader("Current Conditions")
        for idx, cond in enumerate(st.session_state.conditions):
            col1, col2, col3, col4 = st.columns([3, 2, 3, 1])
            with col1:
                st.text(f"**{cond['field']}**")
            with col2:
                st.text(cond['operator'])
            with col3:
                st.text(str(cond['value']))
            with col4:
                if st.button("🗑️", key=f"del_{idx}"):
                    st.session_state.conditions.pop(idx)
                    st.rerun()
        st.markdown("---")

    # Add new condition
    st.subheader("Add New Condition")

    col1, col2, col3 = st.columns([3, 2, 3])

    with col1:
        selected_field = st.selectbox(
            "Field",
            options=field_names,
            help="Select transaction attribute to check"
        )

        # Show field info
        if selected_field:
            info = field_info[selected_field]
            st.caption(f"Type: {info['type']} | {info['description']}")

    with col2:
        # Operators based on field type
        field_type = field_info[selected_field]['type'] if selected_field else 'string'

        if field_type in ['number', 'integer']:
            operators = ['>', '<', '>=', '<=', '==', '!=']
        elif field_type == 'boolean':
            operators = ['==', '!=']
        else:
            operators = ['==', '!=', 'in', 'not_in']

        selected_operator = st.selectbox("Operator", options=operators)

    with col3:
        # Value input based on field type
        if field_type in ['number', 'integer']:
            value = st.number_input(
                "Value",
                min_value=0.0 if field_type == 'number' else 0,
                step=0.01 if field_type == 'number' else 1,
                format="%g"
            )
        elif field_type == 'boolean':
            value = st.selectbox("Value", options=[True, False])
        elif selected_field == 'merchant_category':
            value = st.selectbox(
                "Value",
                options=data_validator.MERCHANT_CATEGORIES
            )
        else:
            value = st.text_input("Value")

    if st.button("➕ Add Condition", type="secondary"):
        new_condition = {
            'field': selected_field,
            'operator': selected_operator,
            'value': value
        }
        st.session_state.conditions.append(new_condition)
        st.rerun()

    st.markdown("---")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        if st.button("← Back"):
            st.session_state.rule_step = 1
            st.rerun()
    with col3:
        if st.button("Next Step →", type="primary", disabled=len(st.session_state.conditions) == 0):
            st.session_state.new_rule['conditions'] = st.session_state.conditions
            st.session_state.rule_step = 3
            st.rerun()

# Step 3: Logic & Outcome
elif st.session_state.rule_step == 3:
    st.header("Step 3: Logic & Outcome")

    # Logic selection
    st.subheader("Condition Logic")
    logic = st.radio(
        "How should conditions be evaluated?",
        options=['AND', 'OR'],
        index=0 if st.session_state.new_rule['logic'] == 'AND' else 1,
        help="AND = all conditions must match | OR = any condition can match"
    )
    st.session_state.new_rule['logic'] = logic

    # Show logic explanation
    num_conditions = len(st.session_state.conditions)
    if logic == 'AND':
        st.info(f"✓ Transaction must satisfy **all {num_conditions}** conditions to trigger this rule")
    else:
        st.info(f"✓ Transaction must satisfy **at least one** of {num_conditions} conditions to trigger this rule")

    st.markdown("---")

    # Outcome settings
    st.subheader("Outcome")

    col1, col2 = st.columns(2)

    with col1:
        decision = st.selectbox(
            "Decision *",
            options=['ALLOW', 'REVIEW', 'BLOCK'],
            index=1,  # Default to REVIEW
            help="What action to take if this rule matches"
        )
        st.session_state.new_rule['outcome']['decision'] = decision

        # Decision helper
        if decision == 'BLOCK':
            st.error("🔴 Transaction will be automatically declined")
        elif decision == 'REVIEW':
            st.warning("🟡 Transaction will be flagged for manual review")
        else:
            st.success("🟢 Transaction will be approved")

    with col2:
        risk_score = st.slider(
            "Risk Score *",
            min_value=0,
            max_value=100,
            value=st.session_state.new_rule['outcome'].get('risk_score', 50),
            help="0-100 risk assessment (higher = riskier)"
        )
        st.session_state.new_rule['outcome']['risk_score'] = risk_score

        # Risk level indicator
        if risk_score >= 90:
            st.error("🔴 Very High Risk")
        elif risk_score >= 70:
            st.warning("🟠 High Risk")
        elif risk_score >= 50:
            st.warning("🟡 Medium Risk")
        else:
            st.success("🟢 Low Risk")

    reason = st.text_area(
        "Reason *",
        value=st.session_state.new_rule['outcome'].get('reason', ''),
        placeholder="e.g., High-value cryptocurrency transaction from unrecognized device",
        help="Explanation shown to reviewers when this rule triggers"
    )
    st.session_state.new_rule['outcome']['reason'] = reason

    st.markdown("---")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        if st.button("← Back"):
            st.session_state.rule_step = 2
            st.rerun()
    with col3:
        if st.button("Next Step →", type="primary", disabled=not reason):
            st.session_state.rule_step = 4
            st.rerun()

# Step 4: Preview & Save
elif st.session_state.rule_step == 4:
    st.header("Step 4: Preview & Save")

    # Generate YAML preview
    import yaml

    rule_dict = {
        'id': st.session_state.new_rule['id'],
        'name': st.session_state.new_rule['name'],
        'conditions': st.session_state.conditions,
        'logic': st.session_state.new_rule['logic'],
        'outcome': st.session_state.new_rule['outcome']
    }

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Rule Summary")
        st.markdown(f"**ID:** `{rule_dict['id']}`")
        st.markdown(f"**Name:** {rule_dict['name']}")
        st.markdown(f"**Conditions:** {len(rule_dict['conditions'])} ({rule_dict['logic']})")
        st.markdown(f"**Decision:** {rule_dict['outcome']['decision']}")
        st.markdown(f"**Risk Score:** {rule_dict['outcome']['risk_score']}/100")

        st.markdown("#### Conditions:")
        for cond in rule_dict['conditions']:
            st.markdown(f"- `{cond['field']}` {cond['operator']} `{cond['value']}`")

    with col2:
        st.subheader("YAML Preview")
        yaml_str = yaml.dump([rule_dict], default_flow_style=False, sort_keys=False)
        st.code(yaml_str, language='yaml')

    # Validation
    st.markdown("---")
    st.subheader("Validation")

    errors = config_mgr.validate_rule(rule_dict)
    if errors:
        st.error("❌ Rule has validation errors:")
        for err in errors:
            st.markdown(f"- {err}")
    else:
        st.success("✅ Rule is valid and ready to save")

    st.markdown("---")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        if st.button("← Back"):
            st.session_state.rule_step = 3
            st.rerun()
    with col2:
        if st.button("Cancel", type="secondary"):
            # Reset
            st.session_state.rule_step = 1
            st.session_state.conditions = []
            st.session_state.new_rule = {
                'id': '',
                'name': '',
                'conditions': [],
                'logic': 'AND',
                'outcome': {'risk_score': 50, 'decision': 'REVIEW', 'reason': ''}
            }
            st.rerun()
    with col3:
        if st.button("💾 Save Rule", type="primary", disabled=bool(errors)):
            try:
                config_mgr.add_rule(rule_dict)
                st.success(f"✅ Rule '{rule_dict['name']}' saved successfully!")
                st.balloons()

                # Reset for next rule
                st.session_state.rule_step = 1
                st.session_state.conditions = []
                st.session_state.new_rule = {
                    'id': '',
                    'name': '',
                    'conditions': [],
                    'logic': 'AND',
                    'outcome': {'risk_score': 50, 'decision': 'REVIEW', 'reason': ''}
                }

                st.info("👉 Go to Dashboard to view your new rule in the decision tree")

            except Exception as e:
                st.error(f"Error saving rule: {str(e)}")

# Footer
st.markdown("---")
st.caption("🤖 Fraud Detection Rule Builder | Anti-hallucination design: LLM explains, never decides")
