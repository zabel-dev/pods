from typing import Annotated

from fastapi import APIRouter, Depends

from app.schemas.requests import VideoRead, VideoRequest, VideoSubtitlesRead
from app.services.video import VideoService
from app.dependencies.dependencies import get_video_service
from app.db.models.user import User
from app.dependencies.dependencies import get_current_user
from app.dependencies.dependencies import get_current_user_optional


router = APIRouter()


@router.post("/video-info", response_model=VideoRead)
async def video_info(
    payload: VideoRequest, 
    current_user: Annotated[User | None, Depends(get_current_user_optional)], 
    service: Annotated[VideoService, Depends(get_video_service)]
):
    user_id = current_user.id if current_user is not None else None
    video = await service.get_or_add_video(payload.external_id, user_id)
    return video


@router.post("/subtitles", response_model=VideoSubtitlesRead)
async def subtitles(
    payload: VideoRequest, 
    current_user: Annotated[User | None, Depends(get_current_user_optional)], 
    service: Annotated[VideoService, Depends(get_video_service)]
):
    user_id = current_user.id if current_user is not None else None
    subtitles = await service.get_or_add_subtitles(payload.external_id, user_id)
    return subtitles
