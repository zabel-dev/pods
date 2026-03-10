from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.dependencies.dependencies import get_video_service
from app.services.video import VideoService
from app.db.models.user import User
from app.dependencies.dependencies import get_current_user_optional


router = APIRouter()


@router.get("/")
async def history(
    current_user: Annotated[User, Depends(get_current_user_optional)], 
    service: Annotated[VideoService, Depends(get_video_service)]
):
    user_id = current_user.id if current_user is not None else None
    return await service.read_history(user_id)