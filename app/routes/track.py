from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.auth.dependencies import get_current_user

from app.schemas.track import TrackCreate, TrackResponse
from app.services.track_service import TrackService

router = APIRouter(prefix="/tracks", tags=["Tracks"])

# Создание трека
@router.post("/", response_model=TrackResponse)
async def create_track(
    track: TrackCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    return await TrackService.create_track(track, db, user.id)

# Получение всех существующих треков
@router.get("/all", response_model=list[TrackResponse])
async def get_all_tracks(db: AsyncSession = Depends(get_db)):
    return await TrackService.get_all_tracks(db)

# Получение добавленных юзером треков
@router.get("/my", response_model=list[TrackResponse])
async def get_my_tracks(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    return await TrackService.get_user_tracks(db, user.id)

# Получение информации о треке по id
@router.get("/{track_id}", response_model=TrackResponse)
async def get_track_by_id(
    track_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await TrackService.get_track_by_id(track_id, db)

# Удаление трека
@router.delete("/{track_id}")
async def delete_track(
    track_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    return await TrackService.delete_track(track_id, db, user.id)
