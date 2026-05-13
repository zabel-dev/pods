from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.models.youtube.video import Video, VideoSubtitles
from app.repositories.video import VideoRepository
from app.core.exceptions import NotFoundError, ExternalServiceError
from app.utils.youtube.yt_dlp_utils.parsers_srt import clean_ansi_escape_sequences
from app.utils.youtube.client import YoutubeClient
from app.utils.youtube.yt_dlp_utils.subtitles import MOCK_SUBTITLES_PLAIN
from app.db.models.youtube.video_history import VideoHistory


class VideoService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.video_repository = VideoRepository(session)

    async def add_history(self, user_id: UUID, external_id: str) -> VideoHistory:
        return await self.video_repository.add_history_note(user_id, external_id)

    async def read_history(self, user_id: UUID | None) -> list[Video]:
        if user_id:
            return await self.video_repository.get_private_history_by_user_id(user_id)
        return await self.video_repository.get_public_history()

    async def read_video_by_external_id(self, external_id: str) -> Video | None:
        return await self.video_repository.get_video_by_external_id(external_id)

    async def read_subtitles_by_external_id(self, external_id: str) -> VideoSubtitles | None:
        return await self.video_repository.get_subtitles_by_external_id(external_id)

    def _youtube_client(self, external_id: str) -> YoutubeClient:
        return YoutubeClient(external_id)

    async def get_or_add_video(self, external_id: str, user_id: UUID | None) -> Video:
        video = await self.read_video_by_external_id(external_id)
        if video:
            await self.video_repository.add_history_note(user_id, video.id)
            return video

        client = self._youtube_client(external_id)
        try:
            meta = await client.get_metadata()
        except ValueError as e:
            raise NotFoundError(f"Video not found: {clean_ansi_escape_sequences(str(e))}")
        except Exception as e:
            raise ExternalServiceError(
                f"Failed to get video metadata: {clean_ansi_escape_sequences(str(e))}"
            )

        video = await self.video_repository.create_video(meta)
        await self.video_repository.add_history_note(user_id, video.id)
        return video

    async def get_or_add_subtitles(self, external_id: str, user_id: UUID | None ) -> VideoSubtitles:
        existing_subtitles = await self.read_subtitles_by_external_id(external_id)
        if existing_subtitles:
            plain = (existing_subtitles.subtitles or "").strip()
            if plain and plain != MOCK_SUBTITLES_PLAIN:
                return existing_subtitles

        try:
            plain, timed = await self._youtube_client(external_id).get_subtitles()
        except ValueError as e:
            raise NotFoundError(f"Subtitles not found: {clean_ansi_escape_sequences(str(e))}")
        except Exception as e:
            raise ExternalServiceError(
                f"Failed to get subtitles: {clean_ansi_escape_sequences(str(e))}"
            )

        video = await self.get_or_add_video(external_id, user_id)

        if video.subtitles_row:
            video.subtitles_row.subtitles = plain
            video.subtitles_row.subtitles_ts = timed
        else:
            video.subtitles_row = VideoSubtitles(
                video_id=video.id,
                subtitles=plain,
                subtitles_ts=timed,
            )

        return await self.video_repository.create_subtitles(video)