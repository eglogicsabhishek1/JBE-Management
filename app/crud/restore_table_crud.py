
from sqlalchemy.orm import Session
from sqlalchemy import text

def restore_table(db: Session, db_name: str, target_table: str, backup_table: str):
    try:
        # Drop the target table if it exists in the given schema
        drop_query = f"DROP TABLE IF EXISTS `{db_name}`.`{target_table}`;"
        db.execute(text(drop_query))

        # Restore from backup table in the given schema
        restore_query = f"""
            CREATE TABLE `{db_name}`.`{target_table}` AS
            SELECT * FROM `{db_name}`.`{backup_table}`;
        """
        db.execute(text(restore_query))
        db.commit()
        return f"Restored '{target_table}' from '{backup_table}' in '{db_name}'."
    except Exception as e:
        raise Exception(f"Restore table error: {str(e)}")
