from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.youtube.video_chat_message import VideoChatMessage


class VideoChatRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_messages(
        self,
        user_id: UUID,
        video_id: UUID,
        limit: int | None = None,
    ) -> list[VideoChatMessage]:
        stmt = (
            select(VideoChatMessage)
            .where(
                VideoChatMessage.user_id == user_id,
                VideoChatMessage.video_id == video_id,
            )
            .order_by(VideoChatMessage.created_at.desc())
        )
        if limit is not None:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())
        rows.reverse()
        return rows

    async def add_message(
        self,
        user_id: UUID,
        video_id: UUID,
        role: str,
        content: str,
    ) -> VideoChatMessage:
        message = VideoChatMessage(
            user_id=user_id,
            video_id=video_id,
            role=role,
            content=content,
        )
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)
        return message
