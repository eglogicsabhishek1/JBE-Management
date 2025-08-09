"""
main.py - Entry point for the Job Management API using FastAPI.

This module initializes the FastAPI app, includes API routers, and defines the root endpoint.
"""

from fastapi import FastAPI
from app.api import user_count_routes
import uvicorn

# Create FastAPI application with metadata
app = FastAPI(
    title="Job Management API",
    version="1.0.0",
    description="API for managing job applications",
)

# Include the user count router for user-related endpoints
app.include_router(user_count_routes.router)

@app.get("/", tags=["Root message"])
def read_root():
    """
    Root endpoint for API.
    Returns a welcome message and directs users to API documentation.
    """
    return {"message": "Welcome to the Job Management API. Go to /docs for API documentation."}

if __name__ == "__main__":
    # Run the FastAPI app using Uvicorn server
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)