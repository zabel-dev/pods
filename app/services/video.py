from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, select
from sqlalchemy.orm import selectinload

from app.db.models.youtube.video import Video, VideoSubtitles
from app.utils.youtube.yt_dlp_utils.metadata import get_video_metadata
from app.utils.youtube.yt_dlp_utils.subtitles import get_subtitles
from app.core.exceptions import NotFoundError, ExternalServiceError
from app.utils.youtube.yt_dlp_utils.parsers import _clean_error_message


async def read_history(db: AsyncSession) -> list[Video]:
    stmt = select(Video)
    result = await db.execute(stmt)
    return result.scalars().all()


async def read_video_by_external_id(db: AsyncSession, external_id: str) -> Video:
    stmt = select(Video).where(Video.external_id == external_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def read_subtitles_by_external_id(db: AsyncSession, external_id: str) -> VideoSubtitles | None:
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
    result = await db.execute(stmt)
    return result.unique().scalar_one_or_none()


async def add_video(db: AsyncSession, external_id: str) -> Video:
    try:
        meta = await get_video_metadata(external_id)
    except ValueError as e:
        raise NotFoundError(f"Video not found: {_clean_error_message(str(e))}")
    except Exception as e:
        raise ExternalServiceError(f"Failed to get video metadata: {_clean_error_message(str(e))}")
    video = Video(
        external_id=meta.get("id"),
        canonical_url=meta.get("canonical_url"),    
        title=meta.get("title"),
        thumbnail_url=meta.get("thumbnail"),
        duration_seconds=meta.get("duration"),
        default_language=meta.get("language"),
    )
    db.add(video)
    await db.commit()
    await db.refresh(video)    
    return video


async def add_subtitles(db: AsyncSession, external_id: str) -> VideoSubtitles:
    try:
        subtitles, subtitles_ts = await get_subtitles(external_id)
    except ValueError as e:
        raise NotFoundError(f"Subtitles not found: {_clean_error_message(str(e))}")
    except Exception as e:
        raise ExternalServiceError(f"Failed to get subtitles: {_clean_error_message(str(e))}")
    video = await read_video_by_external_id(db, external_id)
    if not video:
        video = await add_video(db, external_id)
    if video.subtitles_row:
        video.subtitles_row.subtitles = subtitles
        video.subtitles_row.subtitles_ts = subtitles_ts
    else:
        video.subtitles_row = VideoSubtitles(
            video_id=video.id,
            subtitles=subtitles,
            subtitles_ts=subtitles_ts,
        )
        db.add(video.subtitles_row)
    await db.commit()
    await db.refresh(video)
    return video.subtitles_row


async def get_or_add_video(db: AsyncSession, external_id: str) -> Video:
    video = await read_video_by_external_id(db, external_id)
    if video:
        return video
    return await add_video(db, external_id)


async def get_or_add_subtitles(db: AsyncSession, external_id: str) -> VideoSubtitles:
    subtitles = await read_subtitles_by_external_id(db, external_id)
    if subtitles:
        return subtitles
    return await add_subtitles(db, external_id)

