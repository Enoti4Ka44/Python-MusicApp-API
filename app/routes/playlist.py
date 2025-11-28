from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app.models import Playlist, PlaylistTrack, Track
from app.schemas.playlist import PlaylistCreate, PlaylistResponse
from app.auth.dependencies import get_current_user
from app.models.user import User

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
    try:
        new_playlist = Playlist(
            name=data.name,
            owner_id=current_user.id
        )
        db.add(new_playlist)
        await db.commit()
        await db.refresh(new_playlist)

        if data.track_ids:
            for track_id in data.track_ids:
                track_check = await db.execute(select(Track).where(Track.id == track_id))
                track = track_check.scalars().first()
                if not track:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Track with id {track_id} does not exist"
                    )
                playlist_track = PlaylistTrack(playlist_id=new_playlist.id, track_id=track_id)
                db.add(playlist_track)
            await db.commit()

        result = await db.execute(
            select(PlaylistTrack.track_id).where(PlaylistTrack.playlist_id == new_playlist.id)
        )
        track_ids = [t[0] for t in result.all()]

        return PlaylistResponse(
            id=new_playlist.id,
            name=new_playlist.name,
            owner_id=new_playlist.owner_id,
            track_ids=track_ids
        )

    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred")


# Получить все плейлисты (свои)
@router.get("/", response_model=List[PlaylistResponse],
    summary="Get all user playlists",
    description=(
        "Возвращает список всех плейлистов, принадлежащих авторизованному юзеру. " 
    ))
async def get_playlists(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Playlist).where(Playlist.owner_id == current_user.id))
        playlists = result.scalars().all()
        playlists_out = []

        for p in playlists:
            tracks_result = await db.execute(
                select(PlaylistTrack.track_id).where(PlaylistTrack.playlist_id == p.id)
            )
            track_ids = [t[0] for t in tracks_result.all()]
            playlists_out.append(
                PlaylistResponse(
                    id=p.id,
                    name=p.name,
                    owner_id=p.owner_id,
                    track_ids=track_ids
                )
            )

        return playlists_out

    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred")


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
    try:
        result = await db.execute(select(Playlist).where(Playlist.id == playlist_id))
        playlist = result.scalars().first()
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        if playlist.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

        tracks_result = await db.execute(
            select(PlaylistTrack.track_id).where(PlaylistTrack.playlist_id == playlist.id)
        )
        track_ids = [t[0] for t in tracks_result.all()]

        return PlaylistResponse(
            id=playlist.id,
            name=playlist.name,
            owner_id=playlist.owner_id,
            track_ids=track_ids
        )

    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred")


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
    try:
        result = await db.execute(select(Playlist).where(Playlist.id == playlist_id))
        playlist = result.scalars().first()
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        if playlist.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

        playlist.name = data.name

        await db.execute(
            select(PlaylistTrack).where(PlaylistTrack.playlist_id == playlist.id)
        )
        await db.commit()

        if data.track_ids:
            for track_id in data.track_ids:
                track_check = await db.execute(select(Track).where(Track.id == track_id))
                track = track_check.scalars().first()
                if not track:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Track with id {track_id} does not exist"
                    )
                playlist_track = PlaylistTrack(playlist_id=playlist.id, track_id=track_id)
                db.add(playlist_track)
            await db.commit()

        await db.refresh(playlist)

        tracks_result = await db.execute(
            select(PlaylistTrack.track_id).where(PlaylistTrack.playlist_id == playlist.id)
        )
        track_ids = [t[0] for t in tracks_result.all()]

        return PlaylistResponse(
            id=playlist.id,
            name=playlist.name,
            owner_id=playlist.owner_id,
            track_ids=track_ids
        )

    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred")


# Удаление
@router.delete("/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT,
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
    try:
        result = await db.execute(select(Playlist).where(Playlist.id == playlist_id))
        playlist = result.scalars().first()
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        if playlist.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

        await db.delete(playlist)
        await db.commit()
        return

    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred")
