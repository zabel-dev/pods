from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, select
from sqlalchemy.orm import selectinload

from app.db.models.youtube.video import Video, VideoSubtitles
from app.utils.youtube.yt_dlp_utils.metadata import get_video_metadata
from app.utils.youtube.yt_dlp_utils.subtitles import get_subtitles
from app.core.exceptions import NotFoundError, ExternalServiceError
from app.utils.youtube.yt_dlp_utils.parsers import _clean_error_message
from app.repositories.auth import UserRepository
from app.core.security import hash_password
from app.core.exceptions import UserAlreadyExistsError, InvalidCredentialsError
from app.db.models.user import User
from app.schemas.requests import UserRegisterRequest
from sqlalchemy.exc import IntegrityError
from app.schemas.requests import UserLoginRequest, UserLoginResponse
from app.core.security import verify_password, create_access_token


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)

    async def create_user(self, payload: UserRegisterRequest) -> User:
        if await self.users.get_by_email(payload.email):
            raise UserAlreadyExistsError("Email already exists")
        user = User(
            email=payload.email,
            hashed_password=hash_password(payload.password),
            is_active=True,
        )
        try:
            await self.users.add(user)
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            raise UserAlreadyExistsError("User already exists") from exc
        await self.session.refresh(user)
        return user
    

    async def login(self, payload: UserLoginRequest) -> UserLoginResponse:
        user = await self.users.get_by_email(payload.email)
        if not user:
            raise InvalidCredentialsError("Invalid email or password")

        if not verify_password(payload.password, user.hashed_password):
            raise InvalidCredentialsError("Invalid email or password")

        access_token = create_access_token(subject=str(user.id))

        return UserLoginResponse(
            access_token=access_token,
            token_type="bearer",
        )