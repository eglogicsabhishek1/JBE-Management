
# Import necessary modules from FastAPI and SQLAlchemy
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
# Import database session and CRUD function
from app.database import get_db
from app.crud.user_count_crud import get_user_count


# Create an API router with the tag 'User Count'
router = APIRouter(tags=["User Count"])


@router.get("/user_count")
def user_count(
    db_name: str = Query(..., description="Target database name"),
    db: Session = Depends(get_db)
):
    """
    GET /user_count endpoint.
    Returns the number of users in the specified target database.
    Parameters:
        db_name (str): Name of the target database (query parameter).
        db (Session): SQLAlchemy database session (dependency).
    Returns:
        JSON response with status and user count result.
    """
    try:
        # Call the CRUD function to get user count
        result = get_user_count(db_name, db)
        return {"status": "success", "result": result}
    except Exception as e:
        # Raise HTTP 500 error if any exception occurs
        raise HTTPException(status_code=500, detail=str(e))



    