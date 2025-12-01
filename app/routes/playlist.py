from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.schemas.playlist import PlaylistCreate, PlaylistResponse, PlaylistUpdate
from app.models.user import User
from app.services.playlist_service import PlaylistService

router = APIRouter(prefix="/playlists", tags=["Playlists"])

#Эндпоинт создания плейлиста
@router.post("/", 
    response_model=PlaylistResponse,
    description=(
        "Создает новый плейлист. " 
        "Если track_id указаны, то они добавляются в плейлист "
    ))
async def create_playlist(
    data: PlaylistCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await PlaylistService.create_playlist(db, data, current_user.id)


#Эндпоинт получения всех плейлистов
@router.get("/", response_model=list[PlaylistResponse],
    summary="Get User Playlists",
    description=(
        "Возвращает список плейлистов пользователя" 
    ))
async def get_playlists(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await PlaylistService.get_user_playlists(db, current_user.id)


#Эндпоинт получения плейлиста по id
@router.get("/{playlist_id}", response_model=PlaylistResponse,
    summary="Get Playlist by ID",
    description=(
        "Возвращает информацию о плейлисте " 
    ))
async def get_playlist(
    playlist_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await PlaylistService.get_playlist(db, playlist_id, current_user.id)


#Эндпоинт редактирования плейлиста
@router.patch("/{playlist_id}", response_model=PlaylistResponse,
    summary="Update playlist",
    description=(
        "Обновляет название, описание и список треков плейлиста. " 
        "Доступно только его владельцу"
    ))
async def update_playlist(
    playlist_id: int,
    data: PlaylistUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    payload = data.model_dump(exclude_unset=True)
    return await PlaylistService.update_playlist(db, playlist_id, payload, current_user.id)


#Эндпоинт добавления трека в плейлист
@router.post("/{playlist_id}/add-track/{track_id}",
    summary="Add Track to Playlist",
    description=(
        "Добавляет трек в плейлист. "
        "Доступно только его владельцу" 
    ))
async def add_track(
    playlist_id: int,
    track_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await PlaylistService.add_track_to_playlist(db, playlist_id, track_id, current_user.id)

#Удаление трека из плейлиста
@router.delete("/{playlist_id}/remove-track/{track_id}",
    summary="Remove Track from Playlist",
    description=(
        "Удаляет трек из плейлиста. " 
        "Доступно только его владельцу"
    ))
async def remove_track(
    playlist_id: int,
    track_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await PlaylistService.remove_track_from_playlist(
        db, playlist_id, track_id, current_user.id
    )

#Удаление
@router.delete("/{playlist_id}", status_code=204,
    description=(
        "Удаляет плейлист. " 
        "Доступно только его владельцу"
    ))
async def delete_playlist(
    playlist_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await PlaylistService.delete_playlist(db, playlist_id, current_user.id)



