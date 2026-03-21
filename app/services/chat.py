from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationError
from app.repositories.video_chat import VideoChatRepository
from app.utils.grok.grok_utils import chat_with_grok


class ChatService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.chat_repo = VideoChatRepository(session)

    async def get_history(self, user_id: UUID, video_id: UUID) -> list[dict]:
        """Для GET /api/.../chat/history — только чтение из БД."""
        rows = await self.chat_repo.list_messages(user_id, video_id)
        return [{"role": r.role, "content": r.content} for r in rows]

    async def send_message(
        self,
        user_id: UUID,
        video_id: UUID,
        subtitles_text: str,
        user_content: str,
        *,
        max_history_messages: int = 50,
    ) -> str:
        """
        Один «ход»: сохранить сообщение пользователя, вызвать Grok, сохранить ответ.
        Возвращает текст ответа ассистента.
        """
        # 1) История из БД (ограничить последними N парами при необходимости)
        history = await self.chat_repo.list_messages(user_id, video_id, limit=max_history_messages)

        messages_for_grok = [
            {"role": m.role, "content": m.content}
            for m in history
            if m.role in ("user", "assistant") and (m.content or "").strip()
        ]

        # 2) Текущее сообщение пользователя (можно сначала записать в БД, потом вызывать Grok)
        user_content = (user_content or "").strip()
        if not user_content:
            raise ValidationError("Empty message")

        await self.chat_repo.add_message(user_id, video_id, "user", user_content)
        messages_for_grok.append({"role": "user", "content": user_content})

        # 3) Grok (без БД внутри)
        assistant_text = await chat_with_grok(subtitles_text or "", messages_for_grok)

        # 4) Сохранить ответ
        await self.chat_repo.add_message(user_id, video_id, "assistant", assistant_text)

        return assistant_text