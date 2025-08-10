from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud.restore_table_crud import restore_table

# Create router for restore table operations
router = APIRouter(tags=["Restore table"])

@router.get("/restore_table")
def restore_table_route(
    db_name: str = Query(..., description="Target Database Name"),
    target_table: str = Query("job_alerts", description="Table to store backup data"),
    backup_table: str = Query(..., description="Table from Backup data will fetch "),
    db: Session = Depends(get_db)
):
    """
    Restore a table from its backup.

    This endpoint restores the specified target table in the given database
    by copying data from the provided backup table. Useful for reverting
    changes or recovering lost data.

    Args:
        db_name: Name of the target database.
        target_table: Table to restore (default: 'job_alerts').
        backup_table: Table to restore from (backup source).
        db: SQLAlchemy session (dependency injection).

    Returns:
        JSON dict with status and message about the restore operation.

    Raises:
        HTTPException: 500 if restore fails.
    """
    try:
        # Call the restore_table CRUD function to perform the restore
        message = restore_table(db, db_name, target_table, backup_table)
        # Return success response with message
        return {"status": "success", "message": message}
    except Exception as e:
        # Return error response if restore fails
        raise HTTPException(status_code=500, detail=str(e))