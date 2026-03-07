from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.video import read_history


router = APIRouter()


@router.get("/history")
async def history(db: AsyncSession = Depends(get_db)):
    return await read_history(db)