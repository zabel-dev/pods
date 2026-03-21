from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db.models.youtube.video import Video
from app.db.models.youtube.video import VideoSubtitles
from typing import Sequence
from sqlalchemy import select, delete
from app.db.models.youtube.video_history import VideoHistory


class VideoRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_history_note(self, user_id: UUID | None, video_id: UUID) -> VideoHistory:
        if user_id:
            stmt = (
                select(VideoHistory)
                .where(
                    VideoHistory.user_id == user_id,
                    VideoHistory.video_id == video_id,
                )
            )
            note = await self.session.execute(stmt)
            history_note = note.scalar_one_or_none()
            if history_note:
                return history_note
        history_note = VideoHistory(
            user_id=user_id,
            video_id=video_id,
        )
        self.session.add(history_note)
        await self.session.commit()
        await self.session.refresh(history_note)    
        return history_note

    async def get_private_history_by_user_id(self, user_id: UUID | None) -> list[Video]:
        stmt = (
            select(Video)
            .join(VideoHistory, Video.id == VideoHistory.video_id)
            .where(VideoHistory.user_id == user_id)
            .order_by(VideoHistory.created_at.desc())
            .limit(20)
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def get_public_history(self) -> list[Video]:
        stmt = (
            select(Video)
            .join(VideoHistory, Video.id == VideoHistory.video_id)
            .where(VideoHistory.user_id.is_(None))
            .order_by(VideoHistory.created_at.desc())
            .limit(20)
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())
    
    async def get_video_by_external_id(self, external_id: str) -> Video | None:
        stmt = (
            select(Video)
            .where(
                Video.external_id == external_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_subtitles_by_external_id(self, external_id: str) -> VideoSubtitles | None:
        stmt = (
            select(VideoSubtitles)
            .join(Video, Video.id == VideoSubtitles.video_id)
            .where(
                Video.external_id == external_id,
                VideoSubtitles.subtitles.is_not(None),
                VideoSubtitles.subtitles_ts.is_not(None),
            )
            .options(selectinload(VideoSubtitles.video))
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def create_video(self, meta: dict) -> Video:
        video = Video(
            external_id=meta.get("id"),
            canonical_url=meta.get("canonical_url"),    
            title=meta.get("title"),
            thumbnail_url=meta.get("thumbnail"),
            duration_seconds=meta.get("duration"),
            default_language=meta.get("language"),
        )
        self.session.add(video)
        await self.session.commit()
        await self.session.refresh(video)    
        return video
    
    
    async def create_subtitles(self, video: Video) -> VideoSubtitles:
        self.session.add(video.subtitles_row)
        await self.session.commit()
        await self.session.refresh(video)
        return video.subtitles_row




class VideoHistoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_entry(self, user_id: UUID, video_id: UUID) -> VideoHistory:
        entry = VideoHistory(user_id=user_id, video_id=video_id)
        self.session.add(entry)
        await self.session.commit()
        await self.session.refresh(entry)
        return entry

    async def get_user_history(self, user_id: UUID, limit: int | None = None) -> Sequence[VideoHistory]:
        stmt = (
            select(VideoHistory)
            .where(VideoHistory.user_id == user_id)
            .order_by(VideoHistory.created_at.desc())
            .options(selectinload(VideoHistory.video))
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def clear_user_history(self, user_id: UUID) -> None:
        stmt = delete(VideoHistory).where(VideoHistory.user_id == user_id)
        await self.session.execute(stmt)
        await self.session.commit()