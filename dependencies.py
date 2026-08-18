from fastapi import Request
from Database import Database

def get_db(request: Request) -> Database:
    return request.app.state.db
