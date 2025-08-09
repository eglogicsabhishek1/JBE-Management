"""
JBE Management API - Main Application Entry Point

This is the main FastAPI application that handles job application management
and user distribution for email alert systems. It provides RESTful APIs for
counting users, creating backups, restoring data, and distributing users
into partitions for load balancing.

Author: JBE Management Team
Version: 1.0.0
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
from typing import Dict, Any

# Import API route modules
from app.api import (
    user_count_routes,
    distributes_user_routes
)
from app.database import create_tables

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    
    This function handles initialization tasks when the application starts
    and cleanup tasks when it shuts down.
    """
    # Startup events
    logger.info("Starting JBE Management API...")
    try:
        # Create database tables if they don't exist
        create_tables()
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    yield  # Application runs here
    
    # Shutdown events
    logger.info("Shutting down JBE Management API...")

# Create FastAPI application instance with comprehensive configuration
app = FastAPI(
    title="JBE Management API",
    version="1.0.0",
    description="""
    ## JBE Management API
    
    A comprehensive API for managing job applications and automating user distribution 
    for job alert email systems.
    
    ### Key Features:
    - **User Count Management**: Get active user counts grouped by frequency
    - **Backup Operations**: Create and restore backups of job alerts tables
    - **User Distribution**: Distribute users into partitions for load balancing
    - **Database Management**: Cross-database operations with MySQL support
    
    ### API Documentation:
    - **Interactive API Docs**: Available at `/docs`
    - **ReDoc Documentation**: Available at `/redoc`
    
    ### Authentication:
    Currently using database-level authentication. API key authentication 
    may be implemented in future versions.
    """,
    contact={
        "name": "JBE Management Team",
        "email": "support@jbemanagement.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan
)

# Configure CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure specific origins in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include API routers with their respective prefixes
app.include_router(
    user_count_routes.router,
    prefix="/api/v1",
    tags=["User Count Management"]
)

app.include_router(
    distributes_user_routes.router,
    tags=["User Distribution"]
)

@app.get("/", tags=["Health Check"])
def read_root() -> Dict[str, Any]:
    """
    Root endpoint providing API information and health status.
    
    This endpoint serves as a health check and provides basic information
    about the API, including links to documentation.
    
    Returns:
        Dict containing welcome message, API status, and documentation links
    """
    return {
        "message": "Welcome to the JBE Management API",
        "status": "operational",
        "version": "1.0.0",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "user_count": "/api/v1/user_count",
            "distribute_users": "/api/v1/distribute_users",
            "restore_table": "/api/v1/restore_table"
        },
        "description": "API for managing job applications and user distribution for email alerts"
    }

@app.get("/health", tags=["Health Check"])
def health_check() -> Dict[str, str]:
    """
    Health check endpoint for monitoring and load balancer probes.
    
    Returns:
        Dict with health status information
    """
    return {
        "status": "healthy",
        "service": "JBE Management API",
        "version": "1.0.0"
    }

# Application entry point for direct execution
if __name__ == "__main__":
    logger.info("Starting JBE Management API server...")
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info",
        access_log=True,
        reload_dirs=["app"]  # Watch only the app directory for changes
    )

