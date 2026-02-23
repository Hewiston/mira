import os
import asyncio

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware  # <-- ДОБАВЬ

from app.common.config import settings
from app.common.logging import setup_logging
from app.api.routers.users import router as users_router
from app.api.routers.generate import router as generate_router
from app.api.routers.admin.auth import router as admin_auth_router
from app.api.routers.admin.users import router as admin_users_router
from app.api.routers.admin.jobs import router as admin_jobs_router
from app.api.routers.admin.payments import router as admin_payments_router
from app.api.services.bootstrap import create_tables

setup_logging()

app = FastAPI(title="GenieHub API", version="0.1.0", debug=True)

app.add_middleware(  # <-- ДОБАВЬ
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(os.path.join(settings.media_dir, "generated"), exist_ok=True)
app.mount("/media", StaticFiles(directory=settings.media_dir), name="media")

app.include_router(users_router)
app.include_router(generate_router)
app.include_router(admin_auth_router)
app.include_router(admin_users_router)
app.include_router(admin_jobs_router)
app.include_router(admin_payments_router)