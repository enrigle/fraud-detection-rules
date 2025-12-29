# Stage 2: Streamlit Fraud Detection App

Production-ready web interface for fraud detection rule management and testing.

## Setup

```bash
cd stage2_streamlit
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Add ANTHROPIC_API_KEY to .env

streamlit run app.py
```

## Features

### 🔧 Rule Builder (app.py)
- Step-by-step wizard to create fraud detection rules
- No YAML knowledge required
- Real-time validation
- YAML preview before saving

### 📊 Dashboard
- Interactive decision tree visualization (Plotly)
- View all rules
- Drag-and-drop rule reordering
- Summary statistics

### 🧪 Test Transactions
- Upload CSV files or generate sample data
- Preview and select transactions to test
- Run through rule engine
- On-demand LLM explanations
- Export results

### 📜 Audit Log
- Session-based transaction history
- Decision timeline
- Filter and export

## Project Structure

```
stage2_streamlit/
├── app.py                        # Rule Builder wizard
├── pages/
│   ├── 1_📊_Dashboard.py
│   ├── 2_🧪_Test_Transactions.py
│   └── 3_📜_Audit_Log.py
├── src/
│   ├── rule_engine.py            # From Stage 1
│   ├── llm_explainer.py          # From Stage 1
│   ├── models.py                 # From Stage 1
│   ├── data_generator.py         # From Stage 1
│   ├── config_manager.py         # Rule versioning & validation
│   ├── data_validator.py         # Input validation
│   └── visualizer.py             # Plotly decision trees
├── config/
│   └── rules_v1.yaml             # Rule definitions
└── .streamlit/
    └── config.toml               # Red/yellow/green theme
```

## Development Status

- [x] Phase 1: Project setup
- [ ] Phase 2: Rule Builder wizard
- [ ] Phase 3: Dashboard with visualization
- [ ] Phase 4: Transaction testing
- [ ] Phase 5: Audit log
- [ ] Phase 6: Polish & UX

## Key Features

**Anti-hallucination design**: LLM never computes risk scores or makes decisions—only provides explanations for deterministic rule outcomes.

**Color scheme**: Red/Yellow/Green for risk levels
- 🔴 Red (BLOCK): High risk, automatic decline
- 🟡 Yellow (REVIEW): Medium risk, manual review
- 🟢 Green (ALLOW): Low risk, approved

**Session-based**: All data resets on browser refresh (no database required for local development)
