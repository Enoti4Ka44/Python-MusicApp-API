from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models import Track, Album
from app.schemas.track import TrackCreate


class TrackService:

    @staticmethod
    async def create_track(data: TrackCreate, db: AsyncSession, user_id: int):
        result = await db.execute(select(Album).where(Album.id == data.album_id))
        album = result.scalars().first()
        if not album:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Album not found"
            )

        new_track = Track(
            title=data.title,
            duration=data.duration,
            album_id=data.album_id,
        )

        db.add(new_track)
        await db.commit()
        await db.refresh(new_track)
        return new_track


    @staticmethod
    async def get_all_tracks(db: AsyncSession):
        result = await db.execute(select(Track))
        return result.scalars().all()


    @staticmethod
    async def get_user_tracks(db: AsyncSession, user_id: int):
        query = (
            select(Track)
            .join(Track.album)
            .join(Album.artist)
            .where(Album.artist_id == user_id)
        )
        result = await db.execute(query)
        return result.scalars().all()


    @staticmethod
    async def get_track(track_id: int, db: AsyncSession):
        result = await db.execute(select(Track).where(Track.id == track_id))
        track = result.scalars().first()

        if not track:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Track not found"
            )

        return track


    @staticmethod
    async def delete_track(track_id: int, db: AsyncSession, user_id: int):
        track = await TrackService.get_track(track_id, db)

        if track.album.artist_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can delete only your own tracks"
            )

        await db.delete(track)
        await db.commit()
        return {"message": "Track deleted"}
