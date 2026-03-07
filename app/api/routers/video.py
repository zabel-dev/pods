from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.requests import VideoRead, VideoSubtitlesRead, VideoRequest
from app.services.video import get_or_add_video, get_or_add_subtitles


router = APIRouter()


@router.post("/video-info", response_model=VideoRead)
async def video_info(body: VideoRequest, db: AsyncSession = Depends(get_db)):
    video = await get_or_add_video(db, body.external_id)
    return video


@router.post("/subtitles", response_model=VideoSubtitlesRead)
async def subtitles(body: VideoRequest, db: AsyncSession = Depends(get_db)):
    subtitles = await get_or_add_subtitles(db, body.external_id)
    return subtitles
