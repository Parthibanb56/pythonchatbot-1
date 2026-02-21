import ollama
from config import LLM_MODEL

SCHEMA = """
Table: policy_request_audit
Columns:
req_submitted_date,request_status,request_completed_date,srid,tat,policy_no,insured_name,requestor_name,maker_name,checker_name,approver_name,new_region,sap_product,gis_product,lob,flo_core
"""

def generate_sql(question):

    prompt = f"""
    Convert the user question into a SAFE MySQL SELECT query.

    {SCHEMA}

    Rules:
    - Only SELECT queries
    - Use LIMIT 50
    - Do not modify data

    Question: {question}
    """

    response = ollama.chat(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    return response['message']['content']