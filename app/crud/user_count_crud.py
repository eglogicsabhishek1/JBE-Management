from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

def get_user_count(db_name: str, table_name: str, db: Session):
    """
    Returns counts of active users grouped by frequency and next_email_date.

    Args:
        db_name: The database/schema name (e.g., 'xml_ireland')
        table_name: The table name (e.g., 'job_alerts')
        db: SQLAlchemy Session object

    Returns:
        List of dicts with keys: cnt, frequency, next_email_date
    """
    try:
        # Build the SQL query to count users grouped by frequency and next_email_date
        select_query = f"""
            SELECT count(*) cnt, frequency, next_email_date
            FROM `{db_name}`.{table_name}
            WHERE is_active = 1
            GROUP BY frequency, next_email_date;
        """

        # Execute the query and fetch all results (raw tuples)
        result = db.execute(text(select_query)).fetchall()
        # No commit needed for SELECT queries

    except Exception as e:
        # Print error for debugging and raise HTTPException for API error handling
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    # Re-execute the query to get results as mappings (dict-like rows)
    result = db.execute(text(select_query)).mappings().all()
    # Convert each row to a dictionary for easy use in API responses
    list_data = [dict(row) for row in result]
    return list_data