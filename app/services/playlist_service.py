from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from fastapi import HTTPException

from app.models import Playlist, PlaylistTrack, Track
from app.schemas.playlist import PlaylistCreate, PlaylistResponse


class PlaylistService:

    @staticmethod
    async def get_playlist_by_id(db: AsyncSession, playlist_id: int) -> Playlist:
        result = await db.execute(select(Playlist).where(Playlist.id == playlist_id))
        playlist = result.scalars().first()

        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

        return playlist


    @staticmethod
    def check_access(playlist: Playlist, user_id: int):
        if playlist.owner_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")


    @staticmethod
    async def get_track_ids(db: AsyncSession, playlist_id: int) -> list[int]:
        result = await db.execute(
            select(PlaylistTrack.track_id)
            .where(PlaylistTrack.playlist_id == playlist_id)
        )
        return [r[0] for r in result.all()]


    @staticmethod
    async def validate_tracks_exist(db: AsyncSession, track_ids: list[int]):
        for track_id in track_ids:
            result = await db.execute(select(Track).where(Track.id == track_id))
            if not result.scalars().first():
                raise HTTPException(
                    status_code=400,
                    detail=f"Track with id {track_id} does not exist"
                )


    @staticmethod
    async def create_playlist(db: AsyncSession, data: PlaylistCreate, user_id: int):
        new_pl = Playlist(
            name=data.name,
            owner_id=user_id
        )
        db.add(new_pl)
        await db.commit()
        await db.refresh(new_pl)

        if data.track_ids:
            await PlaylistService.validate_tracks_exist(db, data.track_ids)
            for t_id in data.track_ids:
                db.add(PlaylistTrack(playlist_id=new_pl.id, track_id=t_id))
            await db.commit()

        track_ids = await PlaylistService.get_track_ids(db, new_pl.id)

        return PlaylistResponse(
            id=new_pl.id,
            name=new_pl.name,
            owner_id=new_pl.owner_id,
            track_ids=track_ids
        )


    @staticmethod
    async def get_user_playlists(db: AsyncSession, user_id: int):
        result = await db.execute(
            select(Playlist).where(Playlist.owner_id == user_id)
        )
        playlists = result.scalars().all()

        response = []
        for p in playlists:
            tracks = await PlaylistService.get_track_ids(db, p.id)
            response.append(
                PlaylistResponse(
                    id=p.id,
                    name=p.name,
                    owner_id=p.owner_id,
                    track_ids=tracks
                )
            )
        return response


    @staticmethod
    async def get_playlist(db: AsyncSession, playlist_id: int, user_id: int):
        playlist = await PlaylistService.get_playlist_by_id(db, playlist_id)
        PlaylistService.check_access(playlist, user_id)

        track_ids = await PlaylistService.get_track_ids(db, playlist.id)

        return PlaylistResponse(
            id=playlist.id,
            name=playlist.name,
            owner_id=playlist.owner_id,
            track_ids=track_ids
        )


    @staticmethod
    async def update_playlist(db: AsyncSession, playlist_id: int, data: PlaylistCreate, user_id: int):
        playlist = await PlaylistService.get_playlist_by_id(db, playlist_id)
        PlaylistService.check_access(playlist, user_id)

        playlist.name = data.name

        await db.execute(
            delete(PlaylistTrack).where(PlaylistTrack.playlist_id == playlist_id)
        )

        if data.track_ids:
            await PlaylistService.validate_tracks_exist(db, data.track_ids)
            for t_id in data.track_ids:
                db.add(PlaylistTrack(playlist_id=playlist_id, track_id=t_id))

        await db.commit()
        await db.refresh(playlist)

        track_ids = await PlaylistService.get_track_ids(db, playlist.id)

        return PlaylistResponse(
            id=playlist.id,
            name=playlist.name,
            owner_id=playlist.owner_id,
            track_ids=track_ids
        )


    @staticmethod
    async def delete_playlist(db: AsyncSession, playlist_id: int, user_id: int):
        playlist = await PlaylistService.get_playlist_by_id(db, playlist_id)
        PlaylistService.check_access(playlist, user_id)

        await db.delete(playlist)
        await db.commit()
