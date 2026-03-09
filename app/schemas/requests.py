from pydantic import UUID3, BaseModel, HttpUrl, Field, field_validator
from uuid import UUID
from datetime import datetime
from app.utils.youtube.yt_dlp_utils.url_parser import extract_youtube_video_id
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
import re

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


class VideoRequest(BaseModel):
    source_url: str = Field("https://www.youtube.com/watch?v=9fd5iBK6wsE", min_length=1)
    @field_validator("source_url")
    @classmethod
    def validate_source_url(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("source_url must not be empty")
        if extract_youtube_video_id(value) is None:
            raise ValueError("Invalid YouTube video URL")
        return value
    @property
    def external_id(self) -> str:
        external_id = extract_youtube_video_id(self.source_url)
        if external_id is None:
            raise ValueError("Invalid YouTube video URL")
        return external_id


class VideoRead(BaseModel):
    id: UUID
    canonical_url: HttpUrl | None = None
    title: str | None
    thumbnail_url: str | None
    created_at: datetime
    class Config:
        from_attributes = True


class VideoSubtitlesRead(BaseModel):
    video_id: UUID
    subtitles: str | None
    subtitles_ts: str | None
    class Config:
        from_attributes = True


class UserRegisterRequest(BaseModel):
    email: str = Field("user@example.com", min_length=8, max_length=255)
    password: str = Field("password", min_length=8, max_length=255)
    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("email must not be empty")
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", value):
            raise ValueError("Invalid email address")
        return value
    class Config:
        from_attributes = True


class UserLoginRequest(BaseModel):
    email: str = Field("user@example.com", min_length=8, max_length=255)
    password: str = Field("password", min_length=8, max_length=255)
    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("email must not be empty")
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", value):
            raise ValueError("Invalid email address")
        return value


class UserLoginResponse(BaseModel):
    access_token: str
    # refresh_token: str
    class Config:
        from_attributes = True


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    is_active: bool

