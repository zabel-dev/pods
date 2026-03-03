from fastapi import FastAPI
from app.api import routers

from pathlib import Path
from app.core.config import settings


app = FastAPI()

app.include_router(routers.router, prefix="/api/youtube")

