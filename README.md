#  Policy-Driven Approval Agent

A Streamlit-based policy automation agent that converts **plain-English business rules** into structured rules and applies them to a batch of expense claims.

The system uses an **LLM only for policy interpretation**. Final approval decisions are made by a **deterministic Python rule engine**, ensuring that every decision is reproducible and traceable to the exact rule that matched.

## 🎯 Assignment Objective

The agent is designed to:

* Accept plain-English business rules as configuration
* Convert those rules into structured conditions
* Apply the configured rules to sample expense claims
* Produce **Approved, Rejected, or Escalated** decisions
* Provide a traceable rationale for every decision
* Allow non-technical users to add or edit policies without changing Python code
* Handle unsupported or ambiguous policies safely

---

## ✨ Key Features

* Plain-English policy configuration
* LLM-powered policy interpretation
* Structured JSON rule generation
* Deterministic rule execution
* Rule priority and first-match evaluation
* Department-based conditions
* Expense category conditions
* Amount comparisons and ranges
* Receipt-based conditions
* AND conditions
* Same-field OR conditions
* Ambiguous/unsupported policy detection
* Batch claim evaluation
* Decision statistics
* Traceable decision rationale
* CSV result export
* Streamlit user interface

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
```

### Important Design Principle

The LLM does **not** directly approve or reject expenses.

The responsibilities are separated:

```text
LLM
Natural Language
      ↓
Policy Interpretation
      ↓
Structured JSON
```

```text
Python Rule Engine
Structured Rules
      ↓
Claim Evaluation
      ↓
Final Decision
```

This makes the final decision deterministic and auditable.

---

## 📋 Example Business Policy

The application starts with example policies such as:

```text
Reject any expense without a receipt.

Auto-approve Sales expenses below $500.

Escalate Finance or Engineering expenses between $500 and $2,000 for review.
```

A non-technical user can change these directly in the **Business Policies** text box.

For example:

```text
Auto-approve Sales expenses below $1,000.
```

No Python code needs to be changed.

---

## 🔄 How the Agent Works

### 1. Enter Policy

The user enters business rules in plain English.

### 2. Interpret Policy

The LLM converts the natural-language policy into structured JSON.

Example:

```json
{
  "rules": [
    {
      "priority": 1,
      "action": "Rejected",
      "conditions": [
        {
          "field": "has_receipt",
          "operator": "equals",
          "value": false
        }
      ],
      "raw_text": "Reject any expense without a receipt."
    }
  ]
}
```

### 3. Review Structured Rules

The application displays:

* Priority
* Original Rule
* Action
* Conditions

This allows the user to verify how the policy was interpreted.

### 4. Run Approval Engine

The deterministic Python rule engine evaluates each claim against the structured rules.

### 5. Generate Decision

Each claim receives one of:

* **Approved**
* **Rejected**
* **Escalated**

### 6. Explain Decision

The application shows:

* Claim information
* Decision
* Matched rule
* Conditions evaluated
* Actual values
* Traceable rationale

---

## 🧾 Sample Expense Claims

| Claim | Department  | Category             | Amount | Receipt |
| ----- | ----------- | -------------------- | -----: | ------- |
| C001  | Sales       | Travel               |   $250 | Yes     |
| C002  | Sales       | Meals                |   $800 | Yes     |
| C003  | Finance     | Software             |   $300 | Yes     |
| C004  | Sales       | Travel               | $2,500 | Yes     |
| C005  | HR          | Office Supplies      | $3,000 | No      |
| C006  | Marketing   | Client Entertainment |   $450 | Yes     |
| C007  | Engineering | Software             | $1,500 | Yes     |
| C008  | Finance     | Travel               | $2,200 | Yes     |

---

## 🔍 Traceable Decision Example

For example, C001 can produce a rationale similar to:

```text
Rule 2 matched:
Auto-approve Sales expenses below $500.

✓ department equals Sales (actual: Sales)
✓ amount less_than $500.00 (actual: $250.00)
```

The user can therefore see **exactly why the decision was produced**.

---

## ⚙️ Supported Policy Conditions

### Departments

* Sales
* Finance
* HR
* Engineering
* Marketing

Example:

```text
Approve Sales expenses below $500.
```

### Categories

* Travel
* Software
* Meals
* Office Supplies
* Client Entertainment

Example:

```text
Reject Travel expenses over $2,000.
```

### Amount Conditions

Supported expressions include:

```text
below $500
under $500
over $2,000
above $2,000
at least $500
up to $500
between $500 and $2,000
```

### Receipt Conditions

Examples:

```text
Reject expenses without a receipt.
```

```text
Reject expenses when the receipt is missing.
```

### Same-Field OR

Example:

```text
Escalate Finance or Engineering expenses.
```

This is represented as a structured `in` condition.

---

## 🚨 Ambiguous and Unsupported Policies

The application is designed not to invent business rules.

If a policy cannot be safely interpreted, it is reported as an error rather than automatically creating an unsupported condition.

Examples of validation include:

* Invalid actions
* Unsupported fields
* Unsupported operators
* Invalid amount values
* Invalid rule conditions
* LLM/API errors
* Ambiguous policies

This helps prevent unintended approval decisions.

---

## 🛠️ Technology Stack

* **Python**
* **Streamlit**
* **Google Gemini API**
* **Pandas**
* **python-dotenv**
* **JSON**
* **Regular Expressions**

---

## 📁 Project Structure

```text
AI-Policy-Approval-Agent/
│
├── app.py
├── README.md
├── .gitignore
└── .env
```

> `.env` should remain local and must not be committed to GitHub.

---

## 🚀 Setup

### Prerequisites

Install:

* Python 3.10+
* Git
* A Gemini API key

### Clone Repository

```bash
git clone https://github.com/<your-username>/AI-Policy-Approval-Agent.git

cd AI-Policy-Approval-Agent
```

### Install Dependencies

```bash
pip install streamlit pandas python-dotenv google-genai
```

### Configure API Key

Create a `.env` file in the project directory:

```text
GEMINI_API_KEY=your_gemini_api_key
```

Do not upload this file to GitHub.

### Run Application

```bash
streamlit run app.py
```

The application will open in the browser.

---

## 🧑‍💻 How a Non-Technical User Can Change a Policy

The user does not need to modify the Python source code.

They simply edit the **Business Policies** text box.

For example:

**Existing policy:**

```text
Auto-approve Sales expenses below $500.
```

**Updated policy:**

```text
Auto-approve Sales expenses below $1,000.
```

The LLM interprets the updated policy and generates a new structured rule.

The Python rule engine then applies the new rule consistently to the claims.

---

## 📊 Results

The application provides:

* Total claims
* Approved claims
* Rejected claims
* Escalated claims
* Matched rule
* Rule priority
* Decision rationale

Results can also be downloaded as:

```text
approval_results.csv
```

---

## 🔐 Security

The Gemini API key is stored in an environment variable.

The `.env` file should be included in `.gitignore`.

Never commit API keys or other secrets to the public repository.

---

## 🎥 Demo

The demo video demonstrates:

1. Application overview
2. Plain-English policy configuration
3. LLM policy interpretation
4. Generated structured rules
5. Deterministic approval engine
6. Decision results
7. Traceable rationale
8. Editing a policy as a non-technical user
9. One design tradeoff

**Demo Video:** Add your Google Drive/OneDrive shared link here.

---

## ⚖️ Design Tradeoff

A key design decision was to use the LLM for **policy interpretation rather than final decision-making**.

This adds an extra processing step, but provides a stronger separation between natural-language understanding and business-rule execution.

The advantage is that once the policy is converted into structured rules, the same Python rule engine produces consistent and reproducible decisions.

---

## 🔮 Future Enhancements

* CSV upload for real expense claims
* Database integration
* Policy versioning
* Audit logs
* User authentication
* Role-based approval workflows
* Admin dashboard
* Receipt/PDF processing
* REST API using FastAPI
* Cloud deployment

---

## 👩‍💻 Author

**Sri Lakshmi Konda**

B.Tech – Computer Science and Engineering

**Technologies:** Python | Streamlit | Gemini API | Pandas | JSON | Rule-Based Systems
