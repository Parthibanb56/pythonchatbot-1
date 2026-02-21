from llm_sql_generator import generate_sql
from sql_guard import validate_sql
from db import run_query
from formatter import format_response

def chatbot(question):

    sql = generate_sql(question)

    if not validate_sql(sql):
        return "⚠️ Invalid query generated."

    data = run_query(sql)

    return format_response(data)