from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.common.config import settings
from app.api.auth.admin_tokens import issue_token

router = APIRouter(prefix="/v1/admin/auth", tags=["admin-auth"])


class LoginIn(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)


class LoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=LoginOut)
async def login(payload: LoginIn) -> LoginOut:
    if payload.username != settings.admin_username or payload.password != settings.admin_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = issue_token(settings.admin_token_secret, sub=payload.username, role="admin")
    return LoginOut(access_token=token)
