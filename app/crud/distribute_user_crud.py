from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text

def distribute_users(db: Session, db_name:str,target_table: str, frequency: int, parts: int):
    # Create backup table
    timestamp = datetime.now().strftime("%H%M%S_%d%m%y")
    backup_table_name = f"job_alerts_backup_{timestamp}"
    backup_query = f"""
       CREATE TABLE `{db_name}`.`{backup_table_name}` AS 
       SELECT * FROM `{db_name}`.{target_table};
    """
    db.execute(text(backup_query))

    # Get users with specified frequency
    select_query = f"""
        SELECT user_id, frequency, next_email_date
        FROM `{db_name}`.{target_table}
        WHERE is_active = 1 AND frequency = :frequency
        ORDER BY next_email_date ASC
    """
    users = db.execute(text(select_query), {"frequency": frequency}).mappings().all()
    total_users = len(users)
    if total_users == 0:
        return {"message": "No users found"}

    users = sorted(users, key=lambda x: x["next_email_date"])
    start_date = users[0]["next_email_date"]

    base_size = total_users // parts
    extra = total_users % parts
    partitions = []
    idx = 0
    for i in range(parts):
        part_size = base_size + (1 if i < extra else 0)
        partitions.append(users[idx: idx + part_size])
        idx += part_size

    # Update next_email_date for each partition
    for i, partition in enumerate(partitions):
        new_date = start_date + timedelta(days=i * frequency)
        user_ids = [str(user["user_id"]) for user in partition]
        if user_ids:
            placeholders = ','.join(user_ids)
            update_query = f"""
                  UPDATE `{db_name}`.{target_table}
                SET next_email_date = :new_date
                WHERE user_id IN ({placeholders})
            """
            db.execute(text(update_query), {"new_date": new_date})
    db.commit()
    return {
        "message": f"Users distributed into {parts} parts with frequency={frequency} starting from {start_date}",
        "total_users": total_users,
        "start_date": str(start_date),
        "part_sizes": [len(p) for p in partitions]
    }