# Rule-Based Decision Engine

Fraud detection system using deterministic rules + LLM explanations.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Add ANTHROPIC_API_KEY to .env

jupyter notebook decision_engine.ipynb
```

## Project Structure

```
├── decision_engine.ipynb  # Main demo notebook
├── config/rules_v1.yaml   # Fraud detection rules
└── src/
    ├── models.py          # Pydantic schemas
    ├── rule_engine.py     # Deterministic rule evaluation
    ├── llm_explainer.py   # Claude explanations
    └── data_generator.py  # Synthetic test data
```

## Documentation

- **[HOW_TO_USE.md](HOW_TO_USE.md)** - Guide for fraud analysts to define rules (non-technical)
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Technical architecture and design decisions

**Key principle**: LLM never computes risk scores or makes decisions—only explains deterministic rule outcomes.