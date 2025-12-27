# How to Define Fraud Detection Rules

**For fraud analysts**: This guide shows you how to create and modify fraud detection rules without coding knowledge.

## Table of Contents
1. [How Rules Work](#how-rules-work)
2. [Rule Structure Explained](#rule-structure-explained)
3. [Quick Start Templates](#quick-start-templates)
4. [Common Fraud Scenarios](#common-fraud-scenarios)
5. [Available Fields & Operators](#available-fields--operators)
6. [Rule Ordering & Priority](#rule-ordering--priority)
7. [Testing Your Rules](#testing-your-rules)

---

## How Rules Work

Think of rules as a **decision tree**. When a transaction comes in:

1. The system checks rules **from top to bottom**
2. The **first rule that matches** determines the outcome
3. Once a match is found, it stops (no other rules are checked)
4. If no rules match, the DEFAULT rule at the bottom catches everything

**Visual example**:

```
Transaction: $6,000 crypto purchase from new device

↓ Check Rule 1: High-value crypto from new device?
  ├─ Amount > $5,000? ✓ YES
  ├─ Category = crypto? ✓ YES
  └─ New device? ✓ YES
  → ALL conditions match → BLOCK (95 risk score)

  ✋ STOP HERE (don't check other rules)
```

---

## Rule Structure Explained

Each rule has 4 parts:

### 1. **ID & Name** (identification)
```yaml
id: "RULE_001"
name: "High-value crypto from new device"
```
- `id`: Unique identifier (use RULE_001, RULE_002, etc.)
- `name`: Short description (what pattern you're catching)

### 2. **Conditions** (what to check)
```yaml
conditions:
  - field: "transaction_amount"
    operator: ">"
    value: 5000
```
- `field`: What data to check (amount, category, velocity, etc.)
- `operator`: How to compare (>, <, ==, etc.)
- `value`: The threshold or expected value

### 3. **Logic** (how conditions combine)
```yaml
logic: "AND"
```
- `AND`: ALL conditions must be true
- `OR`: ANY condition can be true
- `ALWAYS`: Rule always matches (used for DEFAULT)

### 4. **Outcome** (what happens)
```yaml
outcome:
  risk_score: 95
  decision: "BLOCK"
  reason: "High-value crypto transaction from unrecognized device"
```
- `risk_score`: 0-100 (higher = riskier)
- `decision`: ALLOW | REVIEW | BLOCK
- `reason`: Why this rule triggered (shown to reviewers)

---

## Quick Start Templates

### Template 1: Block high-risk transactions

```yaml
- id: "RULE_XXX"
  name: "Your rule name here"
  conditions:
    - field: "transaction_amount"
      operator: ">"
      value: 10000
  logic: "AND"
  outcome:
    risk_score: 90
    decision: "BLOCK"
    reason: "Explain why this is risky"
```

**How to use**:
1. Copy this template
2. Change `RULE_XXX` to next number (RULE_004, RULE_005, etc.)
3. Change `value: 10000` to your threshold
4. Update the `reason` text
5. Paste into `config/rules_v1.yaml` before the DEFAULT rule

### Template 2: Flag for manual review

```yaml
- id: "RULE_XXX"
  name: "Your rule name here"
  conditions:
    - field: "transaction_velocity_24h"
      operator: ">"
      value: 5
    - field: "is_new_device"
      operator: "=="
      value: true
  logic: "AND"
  outcome:
    risk_score: 75
    decision: "REVIEW"
    reason: "Multiple transactions from new device"
```

**How to use**:
1. Copy this template
2. Modify conditions to match your pattern
3. Set `risk_score` between 50-89 (review threshold)
4. Keep `decision: "REVIEW"` for manual review

### Template 3: Multiple conditions (any match)

```yaml
- id: "RULE_XXX"
  name: "High-risk merchant categories"
  conditions:
    - field: "merchant_category"
      operator: "=="
      value: "gambling"
    - field: "merchant_category"
      operator: "=="
      value: "crypto"
  logic: "OR"
  outcome:
    risk_score: 60
    decision: "REVIEW"
    reason: "Transaction in high-risk category"
```

**How to use**: When you want to catch **any** of several conditions (not all)

---

## Common Fraud Scenarios

### 🔴 Payment Fraud Scenarios

#### High-Value Transfer from New Device
```yaml
- id: "RULE_101"
  name: "Large transfer from unrecognized device"
  conditions:
    - field: "transaction_amount"
      operator: ">"
      value: 10000
    - field: "is_new_device"
      operator: "=="
      value: true
  logic: "AND"
  outcome:
    risk_score: 95
    decision: "BLOCK"
    reason: "High-value transaction from new device requires verification"
```

**When to use**: Catch account takeover attempts

**Customize**:
- Change `10000` to your risk threshold
- Lower to `5000` for stricter blocking
- Raise to `20000` for fewer false positives

#### Velocity Attack (Card Testing)
```yaml
- id: "RULE_102"
  name: "Suspicious transaction velocity"
  conditions:
    - field: "transaction_velocity_24h"
      operator: ">"
      value: 10
  logic: "AND"
  outcome:
    risk_score: 85
    decision: "REVIEW"
    reason: "Unusually high transaction frequency detected"
```

**When to use**: Detect automated card testing or account abuse

**Customize**:
- `value: 10` = more than 10 transactions in 24 hours
- Adjust based on your normal customer behavior
- Add `is_new_device: true` for stricter check

#### Geographic Anomaly
```yaml
- id: "RULE_103"
  name: "Country mismatch with velocity"
  conditions:
    - field: "country_mismatch"
      operator: "=="
      value: true
    - field: "transaction_velocity_24h"
      operator: ">"
      value: 5
  logic: "AND"
  outcome:
    risk_score: 80
    decision: "REVIEW"
    reason: "Multiple transactions from foreign location"
```

**When to use**: Catch compromised credentials used from different country

**Customize**:
- Combine with `transaction_amount` for high-value foreign transactions
- Add account age check for new accounts

#### Rapid-Fire Small Transactions (Card Validation)
```yaml
- id: "RULE_104"
  name: "Card testing pattern"
  conditions:
    - field: "transaction_velocity_24h"
      operator: ">"
      value: 15
    - field: "transaction_amount"
      operator: "<"
      value: 10
  logic: "AND"
  outcome:
    risk_score: 90
    decision: "BLOCK"
    reason: "Multiple small transactions indicate card testing"
```

**When to use**: Detect fraudsters validating stolen card numbers

### 🛒 E-Commerce Fraud Scenarios

#### High-Value Electronics Rush Order
```yaml
- id: "RULE_201"
  name: "Expensive electronics from new account"
  conditions:
    - field: "transaction_amount"
      operator: ">"
      value: 2000
    - field: "merchant_category"
      operator: "=="
      value: "electronics"
    - field: "account_age_days"
      operator: "<"
      value: 30
  logic: "AND"
  outcome:
    risk_score: 75
    decision: "REVIEW"
    reason: "High-value electronics purchase from new account"
```

**When to use**: Catch stolen payment methods buying resellable items

**Customize**:
- Adjust `account_age_days` (30 = accounts less than 1 month old)
- Change `transaction_amount` for your product mix
- Add `is_new_device: true` for extra caution

#### Bulk Purchase Velocity (Reseller Fraud)
```yaml
- id: "RULE_202"
  name: "Multiple high-value purchases"
  conditions:
    - field: "transaction_velocity_24h"
      operator: ">"
      value: 5
    - field: "transaction_amount"
      operator: ">"
      value: 500
  logic: "AND"
  outcome:
    risk_score: 70
    decision: "REVIEW"
    reason: "Multiple expensive purchases in short time"
```

**When to use**: Detect fraudulent bulk buying for resale

#### New Account + High-Risk Category
```yaml
- id: "RULE_203"
  name: "New account gambling"
  conditions:
    - field: "account_age_days"
      operator: "<"
      value: 7
    - field: "merchant_category"
      operator: "=="
      value: "gambling"
  logic: "AND"
  outcome:
    risk_score: 65
    decision: "REVIEW"
    reason: "Gambling transaction from newly created account"
```

**When to use**: Catch bonus abuse or money laundering

#### Cross-Border High-Value Retail
```yaml
- id: "RULE_204"
  name: "Foreign high-value retail"
  conditions:
    - field: "transaction_amount"
      operator: ">"
      value: 3000
    - field: "country_mismatch"
      operator: "=="
      value: true
    - field: "merchant_category"
      operator: "=="
      value: "retail"
  logic: "AND"
  outcome:
    risk_score: 70
    decision: "REVIEW"
    reason: "Large retail purchase from different country than account"
```

**When to use**: Flag unusual cross-border shopping patterns

---

## Available Fields & Operators

### Transaction Fields

| Field | Type | Description | Example Values |
|-------|------|-------------|----------------|
| `transaction_amount` | Number | Dollar amount | `500`, `10000.50` |
| `transaction_velocity_24h` | Number | # of transactions in 24h | `1`, `15`, `50` |
| `merchant_category` | Text | Type of merchant | `"retail"`, `"crypto"`, `"gambling"` |
| `is_new_device` | True/False | Unrecognized device? | `true`, `false` |
| `country_mismatch` | True/False | Different country? | `true`, `false` |
| `account_age_days` | Number | How old is account | `1`, `30`, `365` |

### Merchant Categories

Available categories:
- `"retail"` - General shopping
- `"travel"` - Airlines, hotels, car rental
- `"gambling"` - Casinos, betting sites
- `"crypto"` - Cryptocurrency purchases
- `"electronics"` - Tech products

### Operators

| Operator | Meaning | Use With | Example |
|----------|---------|----------|---------|
| `>` | Greater than | Numbers | `transaction_amount > 5000` |
| `<` | Less than | Numbers | `account_age_days < 30` |
| `>=` | Greater or equal | Numbers | `transaction_velocity_24h >= 10` |
| `<=` | Less or equal | Numbers | `transaction_amount <= 100` |
| `==` | Equals | Any | `merchant_category == "crypto"` |
| `!=` | Not equals | Any | `merchant_category != "retail"` |
| `in` | In a list | Text/Numbers | `merchant_category in ["gambling", "crypto"]` |
| `not_in` | Not in list | Text/Numbers | `merchant_category not_in ["retail", "travel"]` |

### Logic Types

- **`AND`**: ALL conditions must match
  ```yaml
  # Transaction must be BOTH high-value AND crypto
  conditions:
    - transaction_amount > 5000
    - merchant_category == "crypto"
  logic: "AND"
  ```

- **`OR`**: ANY condition can match
  ```yaml
  # Flag if EITHER gambling OR crypto
  conditions:
    - merchant_category == "gambling"
    - merchant_category == "crypto"
  logic: "OR"
  ```

- **`ALWAYS`**: No conditions (matches everything)
  ```yaml
  # Only use for DEFAULT rule at the end
  logic: "ALWAYS"
  ```

### Decision Types

| Decision | Risk Score | Meaning | When to Use |
|----------|-----------|---------|-------------|
| `ALLOW` | 0-49 | Let transaction through | Low/no risk detected |
| `REVIEW` | 50-89 | Send to human reviewer | Medium risk, needs context |
| `BLOCK` | 90-100 | Automatically decline | High confidence fraud |

**Risk score guidelines**:
- **0-30**: Clean transactions
- **31-49**: Minor flags, still approve
- **50-69**: Review recommended
- **70-89**: Review required
- **90-100**: Block immediately

---

## Rule Ordering & Priority

### ⚠️ IMPORTANT: Order Matters!

Rules are checked **top to bottom**. The **first match wins**.

**Example**: What happens to a $6,000 crypto transaction?

```yaml
# ❌ BAD ORDERING
rules:
  - id: "DEFAULT"
    logic: "ALWAYS"
    outcome:
      decision: "ALLOW"  # This matches first!

  - id: "RULE_001"
    conditions:
      - transaction_amount > 5000
      - merchant_category == "crypto"
    outcome:
      decision: "BLOCK"  # Never reached!
```

**Result**: Transaction is ALLOWED (bad!)

```yaml
# ✅ GOOD ORDERING
rules:
  - id: "RULE_001"
    conditions:
      - transaction_amount > 5000
      - merchant_category == "crypto"
    outcome:
      decision: "BLOCK"  # Checked first!

  - id: "DEFAULT"
    logic: "ALWAYS"
    outcome:
      decision: "ALLOW"  # Only if no other rules match
```

**Result**: Transaction is BLOCKED (correct!)

### Best Practices

1. **Most specific rules first**
   - High-risk patterns at the top
   - General patterns below
   - DEFAULT always last

2. **High-severity rules first**
   - BLOCK rules before REVIEW rules
   - REVIEW rules before ALLOW rules

3. **Keep DEFAULT at the bottom**
   - Catches everything that doesn't match
   - Must use `logic: "ALWAYS"`

**Example ordering**:
```
1. BLOCK: High-value crypto from new device (very specific)
2. BLOCK: Card testing velocity pattern (specific)
3. REVIEW: Country mismatch with velocity (medium)
4. REVIEW: High-value electronics (medium)
5. REVIEW: Gambling transactions (general)
6. ALLOW: Everything else (DEFAULT)
```

---

## Testing Your Rules

### Step 1: Add Your Rule

1. Open `config/rules_v1.yaml`
2. Copy a template from this guide
3. Paste it **above** the DEFAULT rule
4. Customize the values
5. Save the file

### Step 2: Test With Sample Data

Create a test transaction that should match:

```python
# Example: Testing a velocity rule
test_transaction = {
    "transaction_id": "test_001",
    "transaction_amount": 500,
    "transaction_velocity_24h": 15,  # Triggers your rule
    "is_new_device": False,
    "country_mismatch": False,
    "merchant_category": "retail"
}
```

### Step 3: Verify the Outcome

Run the notebook and check:
- ✅ Did the correct rule match?
- ✅ Is the risk score appropriate?
- ✅ Is the decision (ALLOW/REVIEW/BLOCK) correct?
- ✅ Does the reason make sense?

### Common Testing Mistakes

❌ **Forgot to save the YAML file**
- Save `rules_v1.yaml` before running notebook

❌ **Rule placed after DEFAULT**
- DEFAULT must always be last

❌ **Typo in field name**
- Use exact names: `transaction_amount` not `amount`

❌ **Wrong operator for type**
- Numbers: use `>`, `<`, `>=`, `<=`
- Text: use `==`, `!=`, `in`, `not_in`
- True/False: use `==` with `true` or `false`

---

## Quick Reference

### Copy-Paste Checklist

When creating a new rule:

- [ ] Unique `id` (RULE_XXX)
- [ ] Descriptive `name`
- [ ] Correct `field` names
- [ ] Appropriate `operator` for field type
- [ ] Realistic `value` thresholds
- [ ] Correct `logic` (AND/OR/ALWAYS)
- [ ] Risk score 0-100
- [ ] Decision: ALLOW/REVIEW/BLOCK
- [ ] Clear `reason` text
- [ ] Placed **before** DEFAULT rule
- [ ] File saved before testing

### Need Help?

**Common questions**:

1. **"Should I use AND or OR?"**
   - AND: All conditions must be true (stricter)
   - OR: Any condition can be true (broader)

2. **"What risk score should I use?"**
   - BLOCK: 90-100
   - REVIEW: 50-89
   - ALLOW: 0-49

3. **"How do I test if a rule works?"**
   - Run the notebook with test data
   - Check which rule matched
   - Verify the decision is correct

4. **"Can I have multiple rules for the same scenario?"**
   - Yes, but only the first match will trigger
   - Order them from most specific to least specific

5. **"What if I want to check a field that's not listed?"**
   - Request new fields from the development team
   - They'll add it to `features:` section and data generator

---

## Example: Building a Rule from Scratch

**Scenario**: You want to block high-value travel purchases from new accounts in foreign countries.

**Step 1: Identify conditions**
- High-value: `transaction_amount > 2000`
- Travel: `merchant_category == "travel"`
- New account: `account_age_days < 30`
- Foreign: `country_mismatch == true`

**Step 2: Choose logic**
- Want ALL conditions to match → `logic: "AND"`

**Step 3: Set outcome**
- High risk → `risk_score: 90`
- Block immediately → `decision: "BLOCK"`

**Step 4: Write the rule**
```yaml
- id: "RULE_301"
  name: "High-value foreign travel from new account"
  conditions:
    - field: "transaction_amount"
      operator: ">"
      value: 2000
    - field: "merchant_category"
      operator: "=="
      value: "travel"
    - field: "account_age_days"
      operator: "<"
      value: 30
    - field: "country_mismatch"
      operator: "=="
      value: true
  logic: "AND"
  outcome:
    risk_score: 90
    decision: "BLOCK"
    reason: "High-value international travel booking from new account"
```

**Step 5: Test**
- Add to `rules_v1.yaml` above DEFAULT
- Run notebook with matching test data
- Verify it blocks correctly

Done! 🎉
