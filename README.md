# Policy-Driven Approval Agent

A Streamlit-based AI-assisted policy approval agent that converts plain-English business rules into structured rules and applies them to expense claims.

The LLM is used only to interpret the policy. Final decisions are made by a deterministic Python rule engine, making each decision reproducible and traceable to the matching rule.

---



- **Live App:** https://policy-approval-agent.streamlit.app/
- **Demo Link:** https://drive.google.com/file/d/1zVho-r6APjEdYsDqz2_4E7l60WzpAc6Z/view?usp=sharing

---

## ✨ Features

- Plain-English business policy configuration
- LLM-based policy interpretation
- Structured JSON rule generation
- Deterministic rule evaluation
- Approved / Rejected / Escalated decisions
- Traceable rationale for each decision
- Rule priority and first-match evaluation
- Department, category, amount, and receipt conditions
- AND conditions and same-field OR conditions
- Handling of unsupported/ambiguous policies
- CSV export of results
- Non-technical users can edit policies without modifying Python code

---

## 🏗️ Architecture

```
Plain-English Policy
        ↓
    LLM Parser
        ↓
 Structured JSON Rules
        ↓
 Python Rule Engine
        ↓
  Expense Claims
        ↓
Approved / Rejected / Escalated
        ↓
  Traceable Rationale
```

> The LLM does not make the final approval decision. It only converts natural language into structured rules. Python then evaluates those rules deterministically.

---

## 📋 Example Policy

```
Reject any expense without a receipt.
Auto-approve Sales expenses below $500.
Escalate Finance or Engineering expenses between $500 and $2,000 for review.
```

A non-technical user can change this directly in the application's **Business Policies** field. No Python code changes are required.

---

## ⚙️ Setup

### Requirements
- Python 3.10+
- Gemini API key
- Git

### Install

```bash
git clone https://github.com/<your-username>/policy-approval-agent.git
cd policy-approval-agent
pip install -r requirements.txt
```

If `requirements.txt` is not included:

```bash
pip install streamlit pandas python-dotenv google-genai
```

### Configure API Key

Create a `.env` file:

```
GEMINI_API_KEY=your_gemini_api_key
```

> ⚠️ Never commit `.env` or your API key to GitHub.

### Run

```bash
streamlit run app.py
```

---

## 📌 Assumptions

- The application evaluates the provided sample expense claims.
- Policies are entered as plain English, normally one policy per line.
- Supported fields are department, category, amount, and receipt availability.
- Rules are evaluated according to priority using first-match logic.
- If no rule matches a claim, the claim is **Escalated** for human review.
- Ambiguous or unsupported policies are reported instead of being automatically interpreted into potentially unsafe rules.
- The Gemini API is used for policy interpretation; the final decision is produced by deterministic Python logic.
- The deployed application requires a valid Gemini API key configured through Streamlit secrets/environment variables.

---

## 🛠️ Technology Stack

- Python
- Streamlit
- Google Gemini API
- Pandas
- JSON
- python-dotenv

---

## 🔒 Security

API keys are stored outside the source code using environment variables or Streamlit Secrets.
Do not commit `.env`, API keys, or other credentials to the public repository.

---

## 👤 Author

**Sri Lakshmi Konda**
B.Tech – Computer Science and Engineering
