"""
User Distribution API Routes

This module contains API endpoints for distributing users into partitions
based on frequency settings for job alert management.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.database import get_db
from app.crud import distribute_user_crud

# Create router with tags for API documentation
router = APIRouter(
    tags=["User Distribution"], 
    prefix="/api/v1"
)

@router.get("/distribute_users")
def distribute_users_by_frequency(
    db_name: str = Query(
        ..., 
        description="Name of the target database to operate on",
        example="job_management_db"
    ),
    target_table: str = Query(
        "job_alerts", 
        description="Name of the table containing user data to distribute",
        example="job_alerts"
    ),
    frequency: int = Query(
        ..., 
        description="Frequency value to filter users (e.g., 1=daily, 7=weekly)",
        example=7,
        ge=1,
        le=365
    ),
    parts: int = Query(
        ..., 
        description="Number of partitions to divide users into for load balancing",
        example=4,
        ge=1,
        le=100
    ),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Distribute users into partitions based on frequency settings.
    
    This endpoint distributes users from the specified table into multiple partitions
    to enable load balancing for email sending operations. Users are filtered by
    frequency and then evenly distributed across the specified number of partitions.
    
    Args:
        db_name: The target database name
        target_table: The table containing user data (default: "job_alerts")
        frequency: Frequency filter for users (1-365 days)
        parts: Number of partitions to create (1-100)
        db: Database session (injected dependency)
    
    Returns:
        Dict containing:
        - success: Boolean indicating operation success
        - message: Description of the operation result
        - partitions_created: Number of partitions created
        - users_distributed: Total number of users distributed
        - distribution_details: Details about each partition
    
    Raises:
        HTTPException: 500 if database operation fails
        HTTPException: 400 for invalid input parameters
    
    Example:
        GET /api/v1/distribute_users?db_name=mydb&frequency=7&parts=4
    """
    try:
        # Validate input parameters
        if not db_name.strip():
            raise HTTPException(
                status_code=400, 
                detail="Database name cannot be empty"
            )
        
        if not target_table.strip():
            raise HTTPException(
                status_code=400, 
                detail="Table name cannot be empty"
            )
        
        # Call the CRUD function to perform user distribution
        result = distribute_user_crud.distribute_users(
            db=db,
            db_name=db_name.strip(),
            target_table=target_table.strip(),
            frequency=frequency,
            parts=parts
        )
        
        return {
            "success": True,
            "message": f"Successfully distributed users with frequency {frequency} into {parts} partitions",
            "data": result
        }
        
    except ValueError as ve:
        # Handle validation errors from CRUD layer
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid input parameters: {str(ve)}"
        )
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred while distributing users: {str(e)}"
        )