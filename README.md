# Policy-Driven Approval Agent

A Streamlit-based policy automation agent that converts **plain-English business rules** into structured rules and applies them to a batch of expense claims.

The application uses an **LLM only for policy interpretation**. Final approval decisions are made by a **deterministic Python rule engine**, making each decision reproducible, explainable, and traceable to the configured policy.

---

## 🔗 Submission Links

### 🚀 Live Application

https://policy-approval-agent.streamlit.app/

## 🎯 Assignment Objective

The agent is designed to:

- Accept plain-English business rules as configuration
- Convert those rules into structured conditions
- Apply the configured rules to sample expense claims
- Produce **Approved, Rejected, or Escalated** decisions
- Provide a traceable rationale for every decision
- Allow non-technical users to add or edit policies without changing Python code
- Handle unsupported or ambiguous policies safely

---

## ✨ Key Features

- Plain-English policy configuration
- LLM-powered policy interpretation
- Structured JSON rule generation
- Deterministic rule execution
- Rule priority and first-match evaluation
- Department-based conditions
- Expense category conditions
- Amount comparisons and ranges
- Receipt-based conditions
- AND conditions
- Same-field OR conditions
- Ambiguous/unsupported policy detection
- Batch claim evaluation
- Decision statistics
- Traceable decision rationale
- CSV result export
- Streamlit web interface

---

## 🏗️ Architecture

```text
Plain-English Business Policy
            ↓
       LLM Parser
            ↓
    Structured JSON Rules
            ↓
 Deterministic Python Rule Engine
            ↓
      Expense Claims
            ↓
   ┌────────┬──────────┬───────────┐
   ↓        ↓          ↓
Approved  Rejected  Escalated
            ↓
    Traceable Rationale
            ↓
        CSV Export
