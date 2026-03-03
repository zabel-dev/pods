from pydantic import BaseModel, HttpUrl


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