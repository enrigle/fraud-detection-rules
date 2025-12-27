# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Rule-based fraud detection engine with LLM explanations. **Critical anti-hallucination principle**: LLM never computes risk scores or makes decisions—only explains deterministic rule outcomes.

## Architecture

3-layer design ensures LLM cannot influence decisions:

1. **Rule Engine** (`src/rules_engine.py`): Evaluates YAML rules, outputs `RuleResult` with risk score + decision
2. **LLM Explainer** (`src/llm_explainer.py`): Receives `RuleResult`, generates human-readable `LLMExplanation`
3. **Models** (`src/models.py`): Pydantic schemas enforce structured I/O, prevent hallucinations

Data flow: Transaction → Rule Engine → RuleResult → LLM → LLMExplanation → FinalDecisionOutput

## Rule Configuration

Rules in `config/rules_v1.yaml`:
- Decision tree structure (first match wins)
- Must have DEFAULT rule with `logic: ALWAYS` as final fallback
- Operators: `>`, `<`, `>=`, `<=`, `==`, `!=`, `in`, `not_in`
- Logics: `AND`, `OR`, `ALWAYS`

## Development Commands

```bash
# Setup
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt

# Environment
cp .env.example .env
# Add ANTHROPIC_API_KEY to .env

# Run notebook
jupyter notebook decision_engine.ipynb

# Format/lint
black src/
ruff check src/

# Execute notebook programmatically
jupyter nbconvert --to notebook --execute decision_engine.ipynb --output executed.ipynb
```

## Key Constraints

- **No placeholders**: Complete implementations only, no `pass` or `TODO`
- **Structured output**: LLM uses Pydantic `LLMExplanation` with `Confidence` enum (not float probabilities)
- **Import validation**: All modules in `src/` use relative imports (`from models import ...`)
- **Rule engine isolation**: `RuleEngine.evaluate()` never calls LLM
- **LLM prompt structure**: Always includes transaction JSON + existing `RuleResult` to prevent decision override

## Common Pitfalls

- Changing `LLMExplainer` to compute risk scores → violates architecture
- Adding LLM-based "override" logic → defeats deterministic guarantee
- Using `confidence` field to adjust decisions → LLM only assesses explanation quality
- Missing DEFAULT rule → `evaluate()` raises ValueError
