from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models import Track, Album, User
from app.schemas.track import TrackCreate, TrackResponse
from sqlalchemy.orm import joinedload


class TrackService:

    @staticmethod
    async def create_track(data: TrackCreate, db: AsyncSession, user_id: int):
        if data.album_id is not None:
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
            owner_id=user_id
        )

        db.add(new_track)
        await db.commit()
        await db.refresh(new_track)

        await db.refresh(new_track.owner)  # чтобы owner.username точно был загружен

        return TrackResponse(
            id=new_track.id,
            title=new_track.title,
            duration=new_track.duration,
            album_id=new_track.album_id,
            owner_id=new_track.owner_id,
            owner_name=new_track.owner.username
        )

    @staticmethod
    async def get_all_tracks(db: AsyncSession):
        result = await db.execute(
            select(Track).options(joinedload(Track.owner))
        )
        tracks = result.scalars().all()

        responses = [
            TrackResponse(
                id=t.id,
                title=t.title,
                duration=t.duration,
                album_id=t.album_id,
                owner_id=t.owner_id,
                owner_name=t.owner.username
            )
            for t in tracks
        ]
        return responses

    @staticmethod
    async def get_user_tracks(db: AsyncSession, user_id: int):
        result = await db.execute(select(Track).where(Track.owner_id == user_id))
        tracks = result.scalars().all()

        responses = []
        for t in tracks:
            await db.refresh(t.owner)
            responses.append(
                TrackResponse(
                    id=t.id,
                    title=t.title,
                    duration=t.duration,
                    album_id=t.album_id,
                    owner_id=t.owner_id,
                    owner_name=t.owner.username
                )
            )
        return responses

    @staticmethod
    async def get_track(track_id: int, db: AsyncSession):
        result = await db.execute(
            select(Track)
            .options(joinedload(Track.owner))
            .where(Track.id == track_id)
        )
        track = result.scalars().first()

        if not track:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Track not found"
            )

        return TrackResponse(
            id=track.id,
            title=track.title,
            duration=track.duration,
            album_id=track.album_id,
            owner_id=track.owner_id,
            owner_name=track.owner.username
        )

    @staticmethod
    async def delete_track(track_id: int, db: AsyncSession, user_id: int):
        track_response = await TrackService.get_track(track_id, db)

        if track_response.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can delete only your own tracks"
            )

        # Получаем объект Track для удаления
        result = await db.execute(select(Track).where(Track.id == track_id))
        track = result.scalars().first()

        await db.delete(track)
        await db.commit()

        return {"message": "Track deleted"}
