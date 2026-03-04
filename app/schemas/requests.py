from pydantic import BaseModel, HttpUrl
from uuid import UUID
from datetime import datetime


class LinkRequest(BaseModel):
    url: HttpUrl = "https://www.youtube.com/watch?v=9fd5iBK6wsE"
    plain_text: bool = False  # True — только текст, False — SRT с таймкодами


class SummaryRequest(BaseModel):
    text: str = "Это видео про собак. Я люблю собак. Да!"


class ChatMessage(BaseModel):
    role: str = "user"
    content: str = "О чём это видео?"


class ChatRequest(BaseModel):
    subtitles_text: str = "Это видео про собак. Я люблю собак. Да!"
    messages: list[ChatMessage]


class VideoCreate(BaseModel):
    source_url: HttpUrl = "https://www.youtube.com/watch?v=9fd5iBK6wsE"


class VideoRead(BaseModel):
    id: UUID
    source_url: str
    title: str | None
    thumbnail_url: str | None
    subtitles: str | None
    subtitles_ts: str | None
    created_at: datetime

    class Config:
        from_attributes = True