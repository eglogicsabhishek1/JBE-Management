from fastapi import  Query
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.orm import Session

def get_user_count(db_name:str,db: Session):
    try:
        select_query = f"""
            SELECT count(*) cnt, frequency, next_email_date
            FROM `{db_name}`.job_alerts
            WHERE is_active = 1
            GROUP BY frequency, next_email_date;
        """
        result = db.execute(text(select_query)).fetchall()
        db.commit()
    except Exception as e:
        print(f"Error: {e}")  # Add this line
        raise HTTPException(status_code=500, detail=str(e))
    result = db.execute(text(select_query)).mappings().all()
    list_data = [dict(row) for row in result]
    return list_data