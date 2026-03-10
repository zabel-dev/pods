import yt_dlp
from fastapi.concurrency import run_in_threadpool
from functools import partial
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.youtube.yt_dlp_utils.metadata import fetch_raw_video_metadata
from app.utils.youtube.yt_dlp_utils.subtitles import fetch_subtitles



class YoutubeClient:
    def __init__(self, external_id: str):
        self.external_id = external_id

    async def get_metadata(self) -> dict:
        return await fetch_raw_video_metadata(self.external_id)

    async def get_subtitles(self) -> str:
        return await fetch_subtitles(self.external_id)