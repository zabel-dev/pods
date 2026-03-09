from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.dependencies.dependencies import get_video_service
from app.services.video import VideoService
from app.db.models.user import User
from app.dependencies.dependencies import get_current_user


router = APIRouter()


@router.get("/history")
async def history(current_user: Annotated[User, Depends(get_current_user)], service: Annotated[VideoService, Depends(get_video_service)]):
    return await service.read_history(current_user.id)