from pydantic import BaseModel, HttpUrl


class LinkRequest(BaseModel):
    url: HttpUrl = "https://www.youtube.com/watch?v=9fd5iBK6wsE"
    plain_text: bool = False  # True — только текст, False — SRT с таймкодами


class SummaryRequest(BaseModel):
    text: str


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    subtitles_text: str
    messages: list[ChatMessage]