from fastapi import APIRouter, Depends
from typing import Annotated

from app.schemas.requests import (
    UserLoginRequest,
    UserLoginResponse,
    UserRead,
    UserRegisterRequest,
)
from app.services.auth import UserService
from app.dependencies.dependencies import get_user_service


router = APIRouter()


@router.post("/register", response_model=UserRead)
async def register(payload: UserRegisterRequest, service: Annotated[UserService, Depends(get_user_service)]):
    return await service.create_user(payload)


@router.post("/login", response_model=UserLoginResponse)
async def login(payload: UserLoginRequest, service: Annotated[UserService, Depends(get_user_service)]):
    return await service.login(payload)


