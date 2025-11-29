from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.auth.dependencies import get_current_user

from app.schemas.track import TrackCreate, TrackResponse
from app.services.track_service import TrackService

router = APIRouter(prefix="/tracks", tags=["Tracks"])

#Эндпоинт создания трека
@router.post("/", response_model=TrackResponse,
    description=(
        "Создает трек. "
        "Если album_id указан, то трек добавляется в указанный альбом " 
    ))
async def create_track(
    track: TrackCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    return await TrackService.create_track(track, db, user.id)

#Эндпоинт получения всех треков
@router.get("/", response_model=list[TrackResponse],
    description=(
        "Возвращает список всех треков " 
    ))
async def get_all_tracks(db: AsyncSession = Depends(get_db)):
    return await TrackService.get_all_tracks(db)

#Эндпоинт получения треков юзера
@router.get("/my", response_model=list[TrackResponse],
    summary="Get User Tracks",
    description=(
        "Возвращает список треков пользователя "  
    ))
async def get_my_tracks(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    return await TrackService.get_user_tracks(db, user.id)

#Эндпоинт получения трека по id
@router.get("/{track_id}", response_model=TrackResponse,
    summary="Get Track by ID",
    description=(
        "Возвращает информацию о треке " 
    ))
async def get_track_by_id(
    track_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await TrackService.get_track_by_id(track_id, db)

#Эндпоинт удаления трека
@router.delete("/{track_id}",
    description=(
        "Удаляет трек. " 
        "Доступно только его владельцу"
    ))
async def delete_track(
    track_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    return await TrackService.delete_track(track_id, db, user.id)
