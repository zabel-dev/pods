from typing import Annotated

from fastapi import APIRouter, Depends

from app.schemas.requests import VideoRead, VideoRequest, VideoSubtitlesRead
from app.services.video import VideoService
from app.dependencies.dependencies import get_video_service


router = APIRouter()


@router.post("/video-info", response_model=VideoRead)
async def video_info(payload: VideoRequest, service: Annotated[VideoService, Depends(get_video_service)]):
    video = await service.get_or_add_video(payload.external_id)
    return video


@router.post("/subtitles", response_model=VideoSubtitlesRead)
async def subtitles(payload: VideoRequest, service: Annotated[VideoService, Depends(get_video_service)]):
    subtitles = await service.get_or_add_subtitles(payload.external_id)
    return subtitles
