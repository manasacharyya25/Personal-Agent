from fastapi import Depends, HTTPException, Header, Request
from Database import Database
from config.settings import Settings, get_settings

def get_db(request: Request) -> Database:
    return request.app.state.db


def verify_api_key(x_api_key: str = Header(None), settings : Settings = Depends(get_settings)):
    if x_api_key != settings.API_AUTH_KEY:
        raise HTTPException(
            status_code=401,
            detail = "Unauthorized"
        )