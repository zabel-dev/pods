from fastapi import FastAPI, HTTPException
from app.api.routers import  video, history, ai

from app.core.exceptions import AppException
from app.api.handlers.exceptions import app_exception_handler, http_exception_handler

app = FastAPI()


app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

app.include_router(video.router, prefix="/api/routers/video")
app.include_router(history.router, prefix="/api/routers/history")
app.include_router(ai.router, prefix="/api/routers/ai")
