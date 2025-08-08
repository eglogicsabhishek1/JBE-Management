from fastapi import FastAPI
from app.api import (user_count_routes ) 
import uvicorn

app = FastAPI(
     title= "Job Management API",
     version= "1.0.0",
     description= "API for managing job  applications",)

app.include_router(user_count_routes.router)

@app.get("/",tags=["Root message"])
def read_root():
    return {"message": "Welcome to the Job Management API.Got to /docs for API documentation."}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)


