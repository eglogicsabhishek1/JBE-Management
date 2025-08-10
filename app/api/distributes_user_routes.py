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
    tags=["User Distribution"]
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
    backup: bool = Query(
        False,
        description="If true, copy data from source_table to backup_table instead of distributing users"
    ),
    source_table: str = Query(
        None,
        description="Source table to copy from (required if backup is true)",
        example="job_alerts"
    ),
    backup_table: str = Query(
        None,
        description="Backup table to copy to (required if backup is true)",
        example="job_alerts_backup"
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
        GET distribute_users?db_name=mydb&table_name=table_name&frequency=7&parts=4
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

        if backup:
            # Backup mode: require source_table and backup_table
            if not source_table or not source_table.strip():
                raise HTTPException(
                    status_code=400,
                    detail="source_table is required when backup is true"
                )
            if not backup_table or not backup_table.strip():
                raise HTTPException(
                    status_code=400,
                    detail="backup_table is required when backup is true"
                )
            # Call CRUD to copy data from source_table to backup_table AND distribute users
            backup_result = distribute_user_crud.create_backup_table(
                db=db,
                db_name=db_name.strip(),
                source_table=source_table.strip(),
                backup_table=backup_table.strip(),
                frequency=frequency,
                parts=parts
            )
            return backup_result
        else:
            # Normal distribution mode
            result = distribute_user_crud.distribute_users(
                db=db,
                db_name=db_name.strip(),
                target_table=target_table.strip(),
                frequency=frequency,
                parts=parts
            )
            return result
    except ValueError as ve:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid input parameters: {str(ve)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred while distributing users: {str(e)}"
        )