from fastapi import APIRouter, Depends,HTTPException,Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud.user_count_crud import get_user_count

router = APIRouter(tags=["User Count"])

@router.get("/user_count")
def user_count(
    db_name: str= Query(..., description= "Target database name"),db: Session = Depends(get_db)
):
    try:
        result = get_user_count(db_name, db)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))



