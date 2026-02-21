import ollama
import re
from config import LLM_MODEL

SCHEMA = """
Table: policy_request_audit

Columns:
- req_submitted_date (date)
- request_status (varchar)
- request_completed_date (date)
- srid (varchar)
- tat (int)
- policy_no (varchar)
- insured_name (varchar)
- requestor_name (varchar)
- maker_name (varchar)
- checker_name (varchar)
- approver_name (varchar)
- new_region (varchar)
- sap_product (varchar)
- gis_product (varchar)
- lob (varchar)
- flo_core (varchar)
"""

def clean_sql(text: str) -> str:
    """
    Extract SQL from LLM response and clean formatting.
    """

    # remove markdown
    text = re.sub(r"```sql|```", "", text, flags=re.IGNORECASE).strip()

    # remove explanations before SELECT
    select_index = text.lower().find("select")
    if select_index != -1:
        text = text[select_index:]

    # remove trailing semicolons & spaces
    text = text.strip().rstrip(";")

    return text


def generate_sql(question: str) -> str | None:
    """
    Generate SAFE SELECT SQL from user question.
    """

    prompt = f"""
You are an expert MySQL query generator.

Convert the user question into a SAFE SQL query.

IMPORTANT RULES:
- RETURN ONLY SQL
- NO explanations
- NO markdown
- ONLY SELECT statements
- NEVER modify data
- ALWAYS use LIMIT 50 unless using COUNT
- Use exact column names only
- Use LIKE for text search
- If asking totals → use COUNT(*)

Database Schema:
{SCHEMA}

Examples:

User: how many pending cases
SQL:
SELECT COUNT(*) AS total_pending
FROM policy_request_audit
WHERE request_status = 'Pending';

User: status of SRID 002
SQL:
SELECT request_status
FROM policy_request_audit
WHERE srid = '002'
LIMIT 50;

User: show cases under SAP
SQL:
SELECT *
FROM policy_request_audit
WHERE sap_product IS NOT NULL
LIMIT 50;

User: how many cases under SAP core
SQL:
SELECT COUNT(*) AS total_sap_core
FROM policy_request_audit
WHERE sap_product LIKE '%core%';

User: how many SAP cases under flo core
SQL:
SELECT COUNT(*) AS total_sap_flo_core
FROM policy_request_audit
WHERE flo_core LIKE '%core%' AND sap_product IS NOT NULL;

User: how many GIS case
SQL:
SELECT COUNT(*) AS total_gis_cases
FROM policy_request_audit
WHERE gis_product IS NOT NULL;

User: how many maker cases under parthiban
SQL:
SELECT COUNT(*) AS total_maker_cases_under_parthiban
FROM policy_request_audit
WHERE maker_name LIKE '%parthiban%';

User Question:
{question}

SQL:
"""

    try:
        response = ollama.chat(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0}
        )

        raw_output = response["message"]["content"]

        sql = clean_sql(raw_output)

        # safety validation
        if not sql.lower().startswith("select"):
            return None

        forbidden = ["update", "delete", "insert", "drop", "alter", "truncate"]
        if any(word in sql.lower() for word in forbidden):
            return None

        return sql

    except Exception as e:
        print("LLM SQL generation error:", e)
        return None