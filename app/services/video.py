from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.youtube.video import Video, VideoSubtitles
from app.repositories.video import VideoRepository
from uuid import UUID
from app.utils.youtube.yt_dlp_utils.metadata import get_video_metadata
from app.utils.youtube.yt_dlp_utils.parsers import _clean_error_message
from app.core.exceptions import NotFoundError, ExternalServiceError
from app.utils.youtube.yt_dlp_utils.subtitles import get_subtitles



class VideoService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.video_repository = VideoRepository(session)


    async def read_history(self, user_id: UUID) -> list[Video]:
        return await self.video_repository.get_by_user_id(user_id)


    async def read_video_by_external_id(self, external_id: str) -> Video:
        return await self.video_repository.get_video_by_external_id(external_id)


    async def read_subtitles_by_external_id(self, external_id: str) -> VideoSubtitles | None:
        return await self.video_repository.get_subtitles_by_external_id(external_id)


    async def add_video(self, external_id: str) -> Video:
        try:
            meta = await get_video_metadata(external_id)
        except ValueError as e:
            raise NotFoundError(f"Video not found: {_clean_error_message(str(e))}")
        except Exception as e:
            raise ExternalServiceError(f"Failed to get video metadata: {_clean_error_message(str(e))}")
        return await self.video_repository.create_video(meta)


    async def add_subtitles(self, external_id: str) -> VideoSubtitles:
        try:
            subtitles, subtitles_ts = await get_subtitles(external_id)
        except ValueError as e:
            raise NotFoundError(f"Subtitles not found: {_clean_error_message(str(e))}")
        except Exception as e:
            raise ExternalServiceError(f"Failed to get subtitles: {_clean_error_message(str(e))}")
        video = await self.read_video_by_external_id(external_id)
        if not video:
            video = await self.add_video(external_id)
        if video.subtitles_row:
            video.subtitles_row.subtitles = subtitles
            video.subtitles_row.subtitles_ts = subtitles_ts
        else:
            video.subtitles_row = VideoSubtitles(
                video_id=video.id,
                subtitles=subtitles,
                subtitles_ts=subtitles_ts,
            )
        return await self.video_repository.create_subtitles(video)


    async def get_or_add_video(self, external_id: str) -> Video:
        video = await self.read_video_by_external_id(external_id)
        if video:
            return video
        return await self.add_video(external_id)


    async def get_or_add_subtitles(self, external_id: str) -> VideoSubtitles:
        subtitles = await self.read_subtitles_by_external_id(external_id)
        if subtitles:
            return subtitles
        return await self.add_subtitles(external_id)

