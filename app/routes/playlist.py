from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.schemas.playlist import PlaylistCreate, PlaylistResponse
from app.models.user import User
from app.services.playlist_service import PlaylistService

router = APIRouter(prefix="/playlists", tags=["Playlists"])

# Создание
@router.post("/", 
    response_model=PlaylistResponse,
    summary="Create a new playlist",
    description=(
        "Создает новый плейлист, пренадлежащий авторизованному юзеру. " 
        "Если track_id указаны, то они добавляются в плейлист "
    ))
async def create_playlist(
    data: PlaylistCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await PlaylistService.create_playlist(db, data, current_user.id)


# Получить все плейлисты (свои)
@router.get("/", response_model=list[PlaylistResponse],
    summary="Get all user playlists",
    description=(
        "Возвращает список всех плейлистов, принадлежащих авторизованному юзеру. " 
    ))
async def get_playlists(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await PlaylistService.get_user_playlists(db, current_user.id)


# Получить плейлист по id
@router.get("/{playlist_id}", response_model=PlaylistResponse,
    summary="Get playlist by ID",
    description=(
        "Возвращает информацию о плейлисте, принадлежащему авторизованному юзеру. " 
        "Иначе возвращает ошибку доступа "
    ))
async def get_playlist(
    playlist_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await PlaylistService.get_playlist(db, playlist_id, current_user.id)


# Обновление
@router.put("/{playlist_id}", response_model=PlaylistResponse,
    summary="Update playlist",
    description=(
        "Обновляет название и список треков плейлиста. " 
        "Доступно только его владельцу"
    ))
async def update_playlist(
    playlist_id: int,
    data: PlaylistCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await PlaylistService.update_playlist(db, playlist_id, data, current_user.id)


# Добавить трек в плейлист
@router.post("/{playlist_id}/add-track/{track_id}")
async def add_track(
    playlist_id: int,
    track_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await PlaylistService.add_track_to_playlist(db, playlist_id, track_id, current_user.id)


# Удаление
@router.delete("/{playlist_id}", status_code=204,
    summary="Delete playlist",
    description=(
        "Удаляет плейлист, пренадлежащий авторизованному пользователю. " 
        "Доступно только его владельцу"
    ))
async def delete_playlist(
    playlist_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await PlaylistService.delete_playlist(db, playlist_id, current_user.id)
