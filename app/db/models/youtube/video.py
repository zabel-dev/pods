import uuid
from datetime import datetime

from sqlalchemy import Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Text, DateTime, ForeignKey
from sqlalchemy import Text, String, Integer, DateTime, UniqueConstraint, Index, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Video(Base):
    __tablename__ = "videos"

    __table_args__ = (
        UniqueConstraint("platform", "external_id", name="uq_videos_platform_external_id"),
        Index("ix_videos_platform_external_id", "platform", "external_id"),
        Index("ix_videos_created_at", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    platform: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="youtube",
    )

    external_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    canonical_url: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )

    title: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    thumbnail_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    duration_seconds: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    default_language: Mapped[str | None] = mapped_column(
        String(16),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
 
    subtitles_row: Mapped["VideoSubtitles | None"] = relationship(
    "VideoSubtitles",
    back_populates="video",
    uselist=False,
    lazy="selectin",
    )


class VideoSubtitles(Base):
    __tablename__ = "video_subtitles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("videos.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    subtitles: Mapped[str | None] = mapped_column(
        Text, 
        nullable=True,
    )
    
    subtitles_ts: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    video: Mapped["Video"] = relationship("Video", back_populates="subtitles_row")
