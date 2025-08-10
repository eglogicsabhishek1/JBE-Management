from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text


def create_backup_table(db: Session, db_name: str, source_table: str, backup_table: str, frequency: int = None, parts: int = None):
    """
    Create a backup table by copying all data from source_table to backup_table in the given database.
    If frequency and parts are provided, also distribute users and include that info in the response.
    """
    try:
        sql = f"""
            CREATE TABLE `{db_name}`.`{backup_table}` AS
            SELECT * FROM `{db_name}`.`{source_table}`;
        """
        db.execute(text(sql))
        db.commit()
        result = {
            "backup": True,
            "backup_table": backup_table,
            "source_table": source_table,
            "status": "created"
        }
        # If distribution params are provided, add distributed user data
        if frequency is not None and parts is not None:
            distribution = distribute_users(db, db_name, backup_table, frequency, parts)
            result["distribution"] = distribution
        return result
    except Exception as e:
        raise Exception(f"Failed to create backup table: {str(e)}")
    
def distribute_users(db: Session, db_name: str, target_table: str, frequency: int, parts: int):
    """
    Distribute users into partitions and update their next_email_date.
    Returns a dict with distribution info and backup=False.
    """
    select_query = f"""
        SELECT user_id, frequency, next_email_date
        FROM `{db_name}`.{target_table}
        WHERE is_active = 1 AND frequency = :frequency
        ORDER BY next_email_date ASC
    """
    users = db.execute(text(select_query), {"frequency": frequency}).mappings().all()
    total_users = len(users)
    if total_users == 0:
        return {
            "message": "No users found",
            "total_users": 0,
            "part_sizes": []
        }

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