from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy import update

from app.db.models.video.youtube import Video
from app.utils.youtube.yt_dlp_utils.metadata import get_video_metadata
from app.utils.youtube.yt_dlp_utils.subtitles import get_subtitles


async def read_history(db: AsyncSession) -> list[Video]:
    stmt = select(Video)
    result = await db.execute(stmt)
    return result.scalars().all()


async def read_video_by_url(db: AsyncSession, source_url: str) -> Video:
    stmt = select(Video).where(Video.source_url == source_url)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def add_video(db: AsyncSession, source_url: str) -> Video:
    meta = await get_video_metadata(source_url)
    video = Video(
        source_url=source_url,
        title=meta.get("title"),
        thumbnail_url=meta.get("thumbnail"),
    )
    db.add(video)
    await db.commit()
    await db.refresh(video)    
    return video


async def add_subtitles(db: AsyncSession, source_url: str) -> Video:
    subtitles, subtitles_ts = await get_subtitles(source_url)
    video = (
        update(Video)
        .where(Video.source_url == source_url)
        .values(
            subtitles=subtitles,
            subtitles_ts=subtitles_ts
        )
        .returning(Video)
    )
    print(video)
    result = await db.execute(video)
    await db.commit()
    return result.scalar_one_or_none()


async def get_or_add_video_by_url(db: AsyncSession, source_url: str) -> Video:
    video = await read_video_by_url(db, source_url)
    if video is None:
        video = await add_video(db, source_url)
    if video.subtitles is None:
        subtitles = await add_subtitles(db, source_url)
    return video