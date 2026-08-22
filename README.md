# Policy-Driven Approval Agent

A Streamlit-based policy automation agent that converts **plain-English business rules** into structured rules and applies them to a batch of expense claims.

The system uses an **LLM only for policy interpretation**. Final approval decisions are made by a **deterministic Python rule engine**, ensuring that every decision is reproducible and traceable to the exact rule that matched.

## 🎥 Demo Video

**5-minute demo:** [Watch the Demo Video](YOUR_GOOGLE_DRIVE_OR_ONEDRIVE_LINK)

The demo covers:

- Application overview
- Plain-English policy configuration
- LLM-based policy interpretation
- Structured JSON rule generation
- Deterministic rule evaluation
- Approval, rejection, and escalation results
- Traceable decision rationale
- Non-technical policy modification
- One design tradeoff

## 🎯 Assignment Objective

The agent is designed to:

- Accept plain-English business rules as configuration
- Convert those rules into structured conditions
- Apply the configured rules to sample expense claims
- Produce **Approved, Rejected, or Escalated** decisions
- Provide a traceable rationale for every decision
- Allow non-technical users to add or edit policies without changing Python code
- Handle unsupported or ambiguous policies safely

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
- Streamlit user interface

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
