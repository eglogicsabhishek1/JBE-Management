## JBE-Management

JBE-Management is a FastAPI-based backend project designed to manage job applications and automate user distribution and backup operations for job alerts. The system connects to a MySQL database and provides RESTful APIs for:

- Counting active users grouped by frequency and next email date
- Creating backups of job alerts tables
- Restoring tables from backups
- Distributing users into partitions based on frequency and scheduling next email dates

### Features
- FastAPI for high-performance, easy-to-use API development
- SQLAlchemy for robust database interaction and session management
- Modular code structure with routers and CRUD logic separated
- Environment-based configuration for secure database credentials
- Automated backup and restore operations for job alerts

### Project Structure

```
JBE-Management/
├── app/
│   ├── api/
│   │   ├── user_count_routes.py
│   │   └── distributes_user_routes.py
|   |   └── restore_table_routes.py
│   ├── crud/
│   │   ├── user_count_crud.py
│   │   └── distribute_user_crud.py
|   |   └── restore_table_crud.py
│   ├── database.py
│   └── main.py
├── .env
├── requirements.txt
├── README.md
```

### How to Run
1. Install dependencies: `pip install -r requirements.txt`
2. Set up your `.env` file with MySQL credentials
3. Start the server: `python app/main.py` or `uvicorn app.main:app --reload`
4. Access the API docs at `http://127.0.0.1:8000/docs`

### API Endpoints
- `/user_count`: Get user counts and backup job alerts
- `/restore_table`: Restore a table from backup
- `/distribute_users`: Distribute users into partitions by frequency

### License
MIT
