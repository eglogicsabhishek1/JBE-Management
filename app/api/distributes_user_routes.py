from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud import distribute_user_crud

router = APIRouter(tags=["Distribute Users"])

@router.get("/distribute_users")
def distribute_users_route(
    db_name: str = Query(..., description="Target Database Name"),
    target_table: str = Query("job_alerts", description="Target Table Name"),
    frequency: int = Query(..., description="Frequency field"),
    parts: int = Query(..., description="Number of partitions"),
    db: Session = Depends(get_db)
):
    try:
        result = distribute_user_crud.distribute_users(db,db_name, target_table, frequency, parts)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))