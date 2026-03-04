import uuid
from datetime import datetime

from sqlalchemy import Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Text, DateTime, ForeignKey

from app.db.base import Base


class Video(Base):
    __tablename__ = "video"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    source_url: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False,
        index=True
    )

    title: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    thumbnail_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    subtitles: Mapped[str | None] = mapped_column(
        Text, 
        nullable=True
    )

    subtitles_ts: Mapped[str | None] = mapped_column(
        Text, 
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )


