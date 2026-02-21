from db import run_query

def get_status_summary():
    return run_query("""
        SELECT request_status, COUNT(*) total
        FROM insurance.policy_request_audit
        GROUP BY request_status
    """)

def get_monthly_trend():
    return run_query("""
        SELECT MONTH(req_submitted_date) month, COUNT(*) total
        FROM insurance.policy_request_audit
        GROUP BY MONTH(req_submitted_date)
    """)

def get_overdue_cases():
    return run_query("""
        SELECT COUNT(*) total
        FROM insurance.policy_request_audit
        WHERE request_status='Pending'
        AND req_submitted_date < CURDATE() - INTERVAL 7 DAY
    """)