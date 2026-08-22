import json
import re
from typing import Any
import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ENVIRONMENT CONFIGURATION
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Use the model available to your Gemini API key
GEMINI_MODEL = "gemini-3.6-flash"

# STREAMLIT CONFIGURATION
st.set_page_config(
    page_title="AI Policy Approval Agent",
    page_icon="🤖",
    layout="wide",
)

# GEMINI CLIENT
if GEMINI_API_KEY:
    try:
        client = genai.Client(
            api_key=GEMINI_API_KEY
        )
        GEMINI_AVAILABLE = True
    except Exception:
        client = None
        GEMINI_AVAILABLE = False
else:
    client = None
    GEMINI_AVAILABLE = False

# SAMPLE EXPENSE CLAIMS
def generate_sample_claims() -> pd.DataFrame:
    claims = [
        {
            "claim_id": "C001",
            "employee": "Employee 1",
            "department": "Sales",
            "category": "Travel",
            "amount": 250.00,
            "has_receipt": True,
        },
        {
            "claim_id": "C002",
            "employee": "Employee 2",
            "department": "Sales",
            "category": "Meals",
            "amount": 800.00,
            "has_receipt": True,
        },
        {
            "claim_id": "C003",
            "employee": "Employee 3",
            "department": "Finance",
            "category": "Software",
            "amount": 300.00,
            "has_receipt": True,
        },
        {
            "claim_id": "C004",
            "employee": "Employee 4",
            "department": "Sales",
            "category": "Travel",
            "amount": 2500.00,
            "has_receipt": True,
        },
        {
            "claim_id": "C005",
            "employee": "Employee 5",
            "department": "HR",
            "category": "Office Supplies",
            "amount": 3000.00,
            "has_receipt": False,
        },
        {
            "claim_id": "C006",
            "employee": "Employee 6",
            "department": "Marketing",
            "category": "Client Entertainment",
            "amount": 450.00,
            "has_receipt": True,
        },
        {
            "claim_id": "C007",
            "employee": "Employee 7",
            "department": "Engineering",
            "category": "Software",
            "amount": 1500.00,
            "has_receipt": True,
        },
        {
            "claim_id": "C008",
            "employee": "Employee 8",
            "department": "Finance",
            "category": "Travel",
            "amount": 2200.00,
            "has_receipt": True,
        },
    ]
    return pd.DataFrame(claims)

# GEMINI SYSTEM PROMPT
SYSTEM_PROMPT = """
You are a business policy parser.

Convert plain-English expense approval policies
into structured JSON.

You ONLY interpret policies.
You MUST NOT execute them.

Return ONLY valid JSON.

Required JSON structure:

{
  "rules": [
    {
      "priority": 1,
      "action": "Approved | Rejected | Escalated",
      "conditions": [
        {
          "field": "department | amount | category | has_receipt",
          "operator": "equals | in | less_than | less_than_or_equal | greater_than | greater_than_or_equal",
          "value": "value"
        }
      ],
      "raw_text": "original policy"
    }
  ],
  "errors": []
}


ACTION RULES

"approve", "auto-approve" -> Approved

"reject", "deny" -> Rejected

"escalate", "send for review", "manual review" -> Escalated


AMOUNT RULES

"under $500"
-> less_than 500

"below $500"
-> less_than 500

"over $2000"
-> greater_than 2000

"above $2000"
-> greater_than 2000

"at least $500"
-> greater_than_or_equal 500

"up to $500"
-> less_than_or_equal 500


BETWEEN

"between $500 and $2000"

must become:

greater_than_or_equal 500

AND

less_than_or_equal 2000


RECEIPTS

"with a receipt"
-> has_receipt equals true

"without a receipt"
-> has_receipt equals false

"receipt is missing"
-> has_receipt equals false


DEPARTMENTS

Sales
Finance
HR
Engineering
Marketing


CATEGORIES

Travel
Software
Meals
Office Supplies
Client Entertainment


SAME-FIELD OR

"Finance or Engineering expenses"

must become:

{
  "field": "department",
  "operator": "in",
  "value": ["Finance", "Engineering"]
}


"Travel or Meals"

must become:

{
  "field": "category",
  "operator": "in",
  "value": ["Travel", "Meals"]
}


DIFFERENT FIELDS

Different fields are combined using AND.

Example:

"Approve Sales expenses below $500"

becomes:

department equals Sales

AND

amount less_than 500


IMPORTANT

Do not invent conditions.

If a policy is ambiguous or unsupported,
add an error entry instead of inventing information.
"""

# GEMINI PARSER - ALL POLICIES IN ONE REQUEST
def parse_policy_with_gemini(
    policy_text: str
) -> dict[str, Any]:
    if not GEMINI_AVAILABLE:
        return {
            "rules": [],
            "errors": [
                {
                    "priority": 0,
                    "rule": "",
                    "issue": "Gemini API is not configured."
                }
            ]
        }

    try:
        # Create Gemini chat
        chat = client.chats.create(
            model=GEMINI_MODEL,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0,
                response_mime_type="application/json",
            ),
        )

        # ONE API CALL FOR ALL POLICIES
        response = chat.send_message(
            policy_text
        )

        content = response.text.strip()

        # Remove markdown fences if present
        content = re.sub(
            r"^```json\s*",
            "",
            content,
            flags=re.IGNORECASE,
        )

        content = re.sub(
            r"\s*```$",
            "",
            content,
            flags=re.IGNORECASE,
        )

        # Remove thinking blocks if returned
        content = re.sub(
            r"<think>.*?</think>",
            "",
            content,
            flags=re.DOTALL | re.IGNORECASE,
        ).strip()

        parsed = json.loads(content)

        if not isinstance(parsed, dict):
            raise ValueError(
                "Gemini returned an invalid JSON object."
            )

        return parsed

    except Exception as exc:
        return {
            "rules": [],
            "errors": [
                {
                    "priority": 0,
                    "rule": "",
                    "issue": f"Gemini API error: {exc}",
                }
            ],
        }

# NORMALIZE RULES
def normalize_rules(
    llm_output: dict[str, Any]
) -> tuple[list[dict], list[dict]]:
    rules = []
    errors = []

    valid_actions = {
        "Approved",
        "Rejected",
        "Escalated",
    }

    for index, rule in enumerate(
        llm_output.get("rules", []),
        start=1,
    ):
        action = rule.get("action")

        if action not in valid_actions:
            errors.append(
                {
                    "priority": index,
                    "rule": rule.get(
                        "raw_text",
                        ""
                    ),
                    "issue": (
                        f"Invalid action: {action}"
                    ),
                }
            )
            continue

        conditions = rule.get(
            "conditions",
            []
        )

        if not isinstance(
            conditions,
            list
        ):
            errors.append(
                {
                    "priority": index,
                    "rule": rule.get(
                        "raw_text",
                        ""
                    ),
                    "issue": (
                        "Conditions must be a list."
                    ),
                }
            )
            continue

        rules.append(
            {
                "priority": index,
                "action": action,
                "conditions": conditions,
                "raw_text": rule.get(
                    "raw_text",
                    ""
                ),
            }
        )

    # Gemini-generated errors
    for error in llm_output.get(
        "errors",
        []
    ):
        errors.append(error)

    return rules, errors

# PARSE COMPLETE POLICY
def parse_policy(
    policy_text: str
) -> tuple[list[dict], list[dict]]:
    result = parse_policy_with_gemini(
        policy_text
    )
    return normalize_rules(result)

# STRING NORMALIZATION
def normalize_string(
    value: Any
) -> str:
    return str(value).strip().lower()

# CONDITION EVALUATION
def evaluate_condition(
    claim: pd.Series,
    condition: dict[str, Any],
) -> tuple[bool, str]:
    field = condition.get("field")
    operator = condition.get("operator")
    expected = condition.get("value")

    valid_fields = {
        "department",
        "amount",
        "category",
        "has_receipt",
    }

    if field not in valid_fields:
        return (
            False,
            f"Unsupported field: {field}",
        )

    actual = claim[field]

    is_string_field = field in {
        "department",
        "category",
    }

    # AMOUNT
    if field == "amount":
        try:
            expected = float(expected)
        except (
            TypeError,
            ValueError,
        ):
            return (
                False,
                f"Invalid amount value: {expected}",
            )

    # RECEIPT
    if field == "has_receipt":
        if isinstance(expected, str):
            expected = (
                expected.lower()
                in {
                    "true",
                    "yes",
                    "required",
                    "present",
                }
            )

        expected = bool(expected)

    # IN
    if operator == "in":
        if not isinstance(
            expected,
            (
                list,
                tuple,
                set,
            ),
        ):
            return (
                False,
                "'in' requires a list.",
            )

        if is_string_field:
            matched = (
                normalize_string(actual)
                in {
                    normalize_string(v)
                    for v in expected
                }
            )
        else:
            matched = actual in expected

        explanation = (
            f"{field} in "
            f"[{', '.join(map(str, expected))}] "
            f"(actual: {actual})"
        )

        return matched, explanation

    # EQUALS FOR STRINGS
    if (
        operator == "equals"
        and is_string_field
    ):
        matched = (
            normalize_string(actual)
            == normalize_string(expected)
        )
    else:
        comparisons = {
            "equals":
                actual == expected,
            "less_than":
                actual < expected,
            "less_than_or_equal":
                actual <= expected,
            "greater_than":
                actual > expected,
            "greater_than_or_equal":
                actual >= expected,
        }

        if operator not in comparisons:
            return (
                False,
                f"Unsupported operator: {operator}",
            )

        matched = comparisons[operator]

    # EXPLANATION
    if field == "amount":
        actual_display = (
            f"${actual:,.2f}"
        )

        expected_display = (
            f"${expected:,.2f}"
        )
    else:
        actual_display = str(actual)
        expected_display = str(expected)

    explanation = (
        f"{field} {operator} "
        f"{expected_display} "
        f"(actual: {actual_display})"
    )

    return matched, explanation

# RULE EVALUATION
def evaluate_rule(
    claim: pd.Series,
    rule: dict,
) -> tuple[bool, list[str]]:
    conditions = rule.get(
        "conditions",
        []
    )

    explanations = []

    for condition in conditions:
        matched, explanation = (
            evaluate_condition(
                claim,
                condition
            )
        )

        explanations.append(
            explanation
        )

        if not matched:
            return (
                False,
                explanations
            )

    return True, explanations

# CLAIM EVALUATION
def evaluate_claim(
    claim: pd.Series,
    rules: list[dict]
) -> dict:
    for rule in rules:
        matched, explanations = (
            evaluate_rule(
                claim,
                rule
            )
        )

        if matched:
            rationale = (
                f"Rule {rule['priority']} matched:\n"
                f"{rule['raw_text']}\n\n"
                +
                "\n".join(
                    f"✓ {item}"
                    for item in explanations
                )
            )

            # IMPORTANT:
            # Convert priority to STRING
            # so Arrow doesn't mix int and "-"
            return {
                "decision": rule["action"],
                "matched_rule": rule["raw_text"],
                "rule_priority": str(
                    rule["priority"]
                ),
                "rationale": rationale,
            }

    return {
        "decision": "Escalated",
        "matched_rule": "No matching rule",
        "rule_priority": "-",
        "rationale": (
            "No configured policy matched "
            "this claim. The claim was "
            "escalated for human review."
        ),
    }

# BATCH EVALUATION
def evaluate_batch(
    claims: pd.DataFrame,
    rules: list[dict]
) -> pd.DataFrame:
    results = []

    for _, claim in claims.iterrows():
        outcome = evaluate_claim(
            claim,
            rules
        )

        results.append(
            {
                **claim.to_dict(),
                **outcome,
            }
        )

    df = pd.DataFrame(results)

    # Make sure Arrow sees consistent types
    df["rule_priority"] = (
        df["rule_priority"]
        .astype(str)
    )

    df["decision"] = (
        df["decision"]
        .astype(str)
    )

    df["matched_rule"] = (
        df["matched_rule"]
        .astype(str)
    )

    df["rationale"] = (
        df["rationale"]
        .astype(str)
    )

    return df

# RULE TABLE
def create_rule_table(
    rules: list[dict]
) -> pd.DataFrame:
    rows = []

    for rule in rules:
        conditions = []

        for condition in rule.get(
            "conditions",
            []
        ):
            value = condition.get(
                "value"
            )

            if isinstance(
                value,
                (
                    list,
                    tuple,
                    set,
                ),
            ):
                value = ", ".join(
                    str(v)
                    for v in value
                )

            conditions.append(
                f"{condition.get('field')} "
                f"{condition.get('operator')} "
                f"{value}"
            )

        rows.append(
            {
                "Priority": str(
                    rule["priority"]
                ),
                "Original Rule":
                    rule["raw_text"],
                "Action":
                    rule["action"],
                "Conditions":
                    " AND ".join(
                        conditions
                    ),
            }
        )

    return pd.DataFrame(rows)

# APPLICATION HEADER
st.title(
    "Policy Approval Agent"
)

st.write(
    """
    Convert plain-English business policies
    into structured rules using Gemini,
    then execute those rules deterministically
    against expense claims.
    """
)

# ARCHITECTURE
with st.expander(
    "🏗️ How this AI Agent works"
):
    st.markdown(
        """
        **1. User Policy**

        Plain-English business rule

        ↓

        **2. Gemini Cloud AI**

        Interprets the English policy

        ↓

        **3. Structured JSON Rule**

        Action + conditions

        ↓

        **4. Deterministic Rule Engine**

        Applies rules to expense claims

        ↓

        **5. Decision + Traceable Rationale**

        Approved / Rejected / Escalated
        """
    )

# BUSINESS POLICY
st.header(
    "1. Business Policy Configuration"
)

st.info(
    """
    Enter expense policies in plain English.
    Each policy should normally be placed
    on a separate line.
    """
)

default_policy = """Reject any expense without a receipt.
Auto-approve Sales expenses below $500.
Escalate Finance or Engineering expenses between $500 and $2,000 for review."""

policy_text = st.text_area(
    "Business Policies",
    value=default_policy,
    height=180,
)

# PARSE BUTTON
if st.button(
    "🧠 Interpret Policies with Gemini AI",
    type="primary",
):
    if not policy_text.strip():
        st.error(
            "Please enter at least one policy."
        )
    elif not GEMINI_AVAILABLE:
        st.error(
            "Gemini API is not configured. "
            "Check your .env file."
        )
    else:
        with st.spinner(
            "with st.spinner(
    "⏳ Please wait while the AI interprets the policies. This may take a few seconds...",
):"
        ):
            parsed_rules, parse_errors = (
                parse_policy(
                    policy_text
                )
            )

        st.session_state[
            "rules"
        ] = parsed_rules

        st.session_state[
            "parse_errors"
        ] = parse_errors

        st.session_state.pop(
            "results",
            None
        )

# STRUCTURED RULES
if "rules" in st.session_state:
    rules = st.session_state[
        "rules"
    ]

    parse_errors = (
        st.session_state.get(
            "parse_errors",
            []
        )
    )

    st.header(
        "2. AI-Generated Structured Rules"
    )

    if rules:
        st.success(
            f"{len(rules)} structured "
            f"rule(s) created."
        )

        rule_table = (
            create_rule_table(
                rules
            )
        )

        st.dataframe(
            rule_table,
            width="stretch",
            hide_index=True,
        )

    if parse_errors:
        st.warning(
            f"{len(parse_errors)} "
            "policy/policies need review."
        )

        for error in parse_errors:
            st.error(
                f"Policy {error.get('priority', '-')}: "
                f"{error.get('rule', '')}\n\n"
                f"Reason: {error.get('issue', 'Unknown error')}"
            )

# SAMPLE CLAIMS
st.header(
    "3. Sample Expense Claims"
)

claims_df = generate_sample_claims()

st.dataframe(
    claims_df,
    width="stretch",
    hide_index=True,
)

# APPROVAL ENGINE
st.header(
    "4. Approval Engine"
)

if st.button(
    "▶ Run Approval Engine",
    type="primary",
):
    rules = st.session_state.get(
        "rules",
        []
    )

    if not rules:
        st.error(
            "No valid structured rules "
            "are available. "
            "Interpret the policies first."
        )
    else:
        with st.spinner(
            "Applying deterministic rules..."
        ):
            results_df = evaluate_batch(
                claims_df,
                rules
            )

        st.session_state[
            "results"
        ] = results_df

# RESULTS
if "results" in st.session_state:
    results_df = st.session_state[
        "results"
    ]

    st.header(
        "5. Decision Results"
    )

    approved = int(
        (
            results_df["decision"]
            == "Approved"
        ).sum()
    )

    rejected = int(
        (
            results_df["decision"]
            == "Rejected"
        ).sum()
    )

    escalated = int(
        (
            results_df["decision"]
            == "Escalated"
        ).sum()
    )

    col1, col2, col3, col4 = (
        st.columns(4)
    )

    col1.metric(
        "Total Claims",
        len(results_df)
    )

    col2.metric(
        "Approved",
        approved
    )

    col3.metric(
        "Rejected",
        rejected
    )

    col4.metric(
        "Escalated",
        escalated
    )

    display_columns = [
        "claim_id",
        "employee",
        "department",
        "category",
        "amount",
        "has_receipt",
        "decision",
        "rule_priority",
        "matched_rule",
    ]

    st.dataframe(
        results_df[
            display_columns
        ],
        width="stretch",
        hide_index=True,
    )

    # EXPLAIN DECISION
    st.header(
        "6. Explain a Decision"
    )

    selected_claim = st.selectbox(
        "Select a claim",
        results_df[
            "claim_id"
        ].tolist()
    )

    selected_row = (
        results_df[
            results_df["claim_id"]
            == selected_claim
        ].iloc[0]
    )

    st.subheader(
        f"Claim {selected_row['claim_id']}"
    )

    col1, col2, col3, col4 = (
        st.columns(4)
    )

    col1.write(
        f"**Department:** "
        f"{selected_row['department']}"
    )

    col2.write(
        f"**Category:** "
        f"{selected_row['category']}"
    )

    col3.write(
        f"**Amount:** "
        f"${selected_row['amount']:,.2f}"
    )

    col4.write(
        f"**Receipt:** "
        f"{'Yes' if selected_row['has_receipt'] else 'No'}"
    )

    decision = selected_row[
        "decision"
    ]

    if decision == "Approved":
        st.success(
            f"Decision: {decision}"
        )
    elif decision == "Rejected":
        st.error(
            f"Decision: {decision}"
        )
    else:
        st.warning(
            f"Decision: {decision}"
        )

    st.write(
        f"**Matched Rule:** "
        f"{selected_row['matched_rule']}"
    )

    st.write(
        "**Traceable Rationale:**"
    )

    st.code(
        selected_row["rationale"]
    )

# NON-TECHNICAL USER GUIDE
with st.expander(
    "ℹ️ How can a non-technical user "
    "add or edit a policy?"
):
    st.markdown(
        """
        The user does **not** modify Python code.

        They simply enter a policy in the
        **Business Policies** text box.

        Example:

        **Old policy**

        `Auto-approve Sales expenses below $500.`

        **New policy**

        `Auto-approve Sales expenses below $1,000.`

        Gemini interprets the sentence and
        converts it into a structured rule.

        The deterministic rule engine then
        applies that rule consistently to
        all claims.
        """
    )

# EXPORT RESULTS
if "results" in st.session_state:
    st.header(
        "7. Export Results"
    )

    csv_data = (
        st.session_state["results"]
        .to_csv(index=False)
        .encode("utf-8")
    )

    st.download_button(
        label="⬇ Download Results CSV",
        data=csv_data,
        file_name="approval_results.csv",
        mime="text/csv",
    )
