from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from fastapi import HTTPException, status

from app.models import Playlist, PlaylistTrack, Track
from app.schemas.playlist import PlaylistCreate, PlaylistResponse


class PlaylistService:

#Функция получения плейлиста по id
    @staticmethod
    async def get_playlist_by_id(db: AsyncSession, playlist_id: int) -> Playlist:
        result = await db.execute(select(Playlist).where(Playlist.id == playlist_id))
        playlist = result.scalars().first()

        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

        return playlist

#Функция проверки доступа
    @staticmethod
    def check_access(playlist: Playlist, user_id: int):
        if playlist.owner_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

#Функция проверки трека на существование
    @staticmethod
    async def validate_tracks_exist(db: AsyncSession, track_ids: list[int]):
        if not track_ids:
            return

        for track_id in track_ids:
            result = await db.execute(select(Track).where(Track.id == track_id))
            if not result.scalars().first():
                raise HTTPException(
                    status_code=400,
                    detail=f"Track with id {track_id} does not exist"
                )
            
#Функция получения трека по id
    @staticmethod
    async def get_track_ids(db: AsyncSession, playlist_id: int) -> list[int]:
        result = await db.execute(
            select(PlaylistTrack.track_id).where(PlaylistTrack.playlist_id == playlist_id)
        )
        return [row[0] for row in result.all()]


#Функция создания плейлиста
    @staticmethod
    async def create_playlist(db: AsyncSession, data: PlaylistCreate, user_id: int) -> PlaylistResponse:
        result = await db.execute(
            select(Playlist).where(
                Playlist.name == data.name,
                Playlist.owner_id == user_id
            )
        )

        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have a playlist with this title"
            )

        playlist = Playlist(
            name=data.name,
            description=data.description,
            owner_id=user_id
        )
        db.add(playlist)
        await db.commit()
        await db.refresh(playlist)

        if data.track_ids:
            await PlaylistService.validate_tracks_exist(db, data.track_ids)
            for t_id in data.track_ids:
                db.add(PlaylistTrack(playlist_id=playlist.id, track_id=t_id))
            await db.commit()

        track_ids = await PlaylistService.get_track_ids(db, playlist.id)
        return PlaylistResponse(
            id=playlist.id,
            name=playlist.name,
            description=playlist.description,
            owner_id=playlist.owner_id,
            track_ids=track_ids
        )


#Функция получения плейлистов юзера
    @staticmethod
    async def get_user_playlists(db: AsyncSession, user_id: int):
        result = await db.execute(
            select(Playlist).where(Playlist.owner_id == user_id)
        )
        playlists = result.scalars().all()

        response = []
        for playlist in playlists:
            tracks = await PlaylistService.get_track_ids(db, playlist.id)
            response.append(
                PlaylistResponse(
                    id=playlist.id,
                    name=playlist.name,
                    description=playlist.description,
                    owner_id=playlist.owner_id,
                    track_ids=tracks
                )
            )
        return response


#Функция получения плейлиста
    @staticmethod
    async def get_playlist(db: AsyncSession, playlist_id: int, user_id: int):

        playlist = await PlaylistService.get_playlist_by_id(db, playlist_id)
        PlaylistService.check_access(playlist, user_id)

        track_ids = await PlaylistService.get_track_ids(db, playlist.id)

        return PlaylistResponse(
            id=playlist.id,
            name=playlist.name,
            description=playlist.description,
            owner_id=playlist.owner_id,
            track_ids=track_ids
        )


#Функция редактирования плейлиста
    @staticmethod
    async def update_playlist(db: AsyncSession, playlist_id: int, data: dict, user_id: int):

        playlist = await PlaylistService.get_playlist_by_id(db, playlist_id)
        PlaylistService.check_access(playlist, user_id)

        if "name" in data and data["name"] != playlist.name:
            result = await db.execute(
                select(Playlist).where(
                    Playlist.name == data["name"],
                    Playlist.owner_id == user_id,
                    Playlist.id != playlist_id
                )
            )

            if result.scalars().first():
                raise HTTPException(
                    status_code=400,
                    detail="You already have a playlist with this name"
                )

            playlist.name = data["name"]

        if "description" in data:
            playlist.description = data["description"]

        if "track_ids" in data:
            track_ids = data["track_ids"]
            await db.execute(
                delete(PlaylistTrack).where(PlaylistTrack.playlist_id == playlist_id)
            )

            if track_ids:
                await PlaylistService.validate_tracks_exist(db, track_ids)
                for track_id in track_ids:
                    db.add(PlaylistTrack(
                        playlist_id=playlist_id,
                        track_id=track_id
                    ))

        await db.commit()
        await db.refresh(playlist)

        track_ids = await PlaylistService.get_track_ids(db, playlist.id)

        return PlaylistResponse(
            id=playlist.id,
            name=playlist.name,
            description=playlist.description,
            owner_id=playlist.owner_id,
            track_ids=track_ids
        )


#Функция удаления плейлиста
    @staticmethod
    async def delete_playlist(db: AsyncSession, playlist_id: int, user_id: int):
        playlist = await PlaylistService.get_playlist_by_id(db, playlist_id)
        PlaylistService.check_access(playlist, user_id)

        await db.delete(playlist)
        await db.commit()

        return {"message": "Playlist deleted"}


#Функция добавления трека в плейлист
    @staticmethod
    async def add_track_to_playlist(db: AsyncSession, playlist_id: int, track_id: int, user_id: int):

        playlist = await PlaylistService.get_playlist_by_id(db, playlist_id)
        PlaylistService.check_access(playlist, user_id)

        result = await db.execute(select(Track).where(Track.id == track_id))
        track = result.scalars().first()

        if not track:
            raise HTTPException(status_code=404, detail="Track not found")

        result = await db.execute(
            select(PlaylistTrack).where(
                PlaylistTrack.playlist_id == playlist_id,
                PlaylistTrack.track_id == track_id
            )
        )
        if result.scalars().first():
            raise HTTPException(status_code=400, detail="Track already in playlist")

        new_link = PlaylistTrack(
            playlist_id=playlist_id,
            track_id=track_id
        )
        db.add(new_link)
        await db.commit()

        track_ids = await PlaylistService.get_track_ids(db, playlist_id)

        return {
            "playlist_id": playlist_id,
            "track_ids": track_ids
        }

#Функция удаления трека из плейлиста
    @staticmethod
    async def remove_track_from_playlist(db: AsyncSession, playlist_id: int, track_id: int, user_id: int):

        playlist = await PlaylistService.get_playlist_by_id(db, playlist_id)
        PlaylistService.check_access(playlist, user_id)

        result = await db.execute(
            select(PlaylistTrack).where(
                PlaylistTrack.playlist_id == playlist_id,
                PlaylistTrack.track_id == track_id
            )
        )
        link = result.scalars().first()

        if not link:
            raise HTTPException(status_code=404, detail="Track not in playlist")

        await db.delete(link)
        await db.commit()

        track_ids = await PlaylistService.get_track_ids(db, playlist_id)

        return {
            "playlist_id": playlist_id,
            "track_ids": track_ids
        }
