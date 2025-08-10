"""
User Count API Routes

This module contains API endpoints for retrieving user counts from job alerts
database, including functionality for backing up tables and getting user
statistics grouped by frequency and next email date.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import logging
from app.database import get_db
from app.crud.user_count_crud import get_user_count

# Configure logging
logger = logging.getLogger(__name__)

# Create router with tags for API documentation
router = APIRouter(
    tags=["User Count Management"]
)

@router.get("/count")
def get_user_count_by_database(
    db_name: str = Query(
        ..., 
        description="Name of the target database containing user data",
        example="job_management_db",
        min_length=1,
        max_length=64
    ),
    table_name: str = Query(
        ..., 
        description="Name of the target table",
        example="job_table",
        min_length=1,
        max_length=64
    ),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get user count statistics from the specified database.
    
    This endpoint retrieves user count statistics grouped by frequency and 
    next email date from the job_alerts table in the specified database.
    It also creates a backup of the table before performing the count operation.
    
    Args:
        db_name: Name of the target database to query
        include_backup: Whether to create a table backup (default: True)
        db: Database session (injected dependency)
    
    Returns:
        Dict containing:
        - status: Operation status ("success" or "error")
        - database: Name of the queried database
        - timestamp: When the operation was performed
        - user_statistics: Dictionary with user counts grouped by frequency
        - total_users: Total number of active users
        - summary: Human-readable summary of results
    
    Raises:
        HTTPException: 400 for invalid database name
        HTTPException: 404 if database or table doesn't exist
        HTTPException: 500 for database operation errors
    
    Example:
        GET user-count/count?db_name=job_db&table_name=job_table
        
        Response:
        {
            "status": "success",
            "database": "job_db",
            "timestamp": "2024-01-15T10:30:00Z",
            "backup_created": true,
            "user_statistics": {
                "frequency_1": {"count": 150, "description": "Daily emails"},
                "frequency_7": {"count": 300, "description": "Weekly emails"}
            },
            "total_users": 450,
            "summary": "Found 450 active users across 2 frequency groups"
        }
    """
    try:
        # Validate database name
        if not db_name or not db_name.strip():
            raise HTTPException(
                status_code=400,
                detail="Database name cannot be empty or contain only whitespace"
            )
        
        # Sanitize database name to prevent injection
        sanitized_db_name = db_name.strip().replace(';', '').replace('--', '')
        
        if sanitized_db_name != db_name.strip():
            raise HTTPException(
                status_code=400,
                detail="Database name contains invalid characters"
            )
        
        logger.info(f"Getting user count for database: {sanitized_db_name}")
        
        # Call the CRUD function to get user count statistics
        result = get_user_count(
            db_name=sanitized_db_name,
            table_name=table_name,
            db=db
        )
        
        logger.info(f"Successfully retrieved user count for database: {sanitized_db_name}")
        
        return {
            "status": "success",
            "database": sanitized_db_name,
            "message": f"User count retrieved successfully from database '{sanitized_db_name}'",
            "data": result
        }
        
    except ValueError as ve:
        logger.warning(f"Invalid input for database {db_name}: {ve}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input parameters: {str(ve)}"
        )
    except FileNotFoundError:
        logger.error(f"Database or table not found: {db_name}")
        raise HTTPException(
            status_code=404,
            detail=f"Database '{db_name}' or required table 'job_alerts' not found"
        )
    except Exception as e:
        logger.error(f"Error getting user count for database {db_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while retrieving user count: {str(e)}"
        )


