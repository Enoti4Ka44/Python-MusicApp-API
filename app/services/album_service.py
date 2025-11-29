from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from fastapi import HTTPException, status
from datetime import date

from app.models import Album, Track
from app.schemas.album import AlbumCreate, AlbumResponse

class AlbumService:

#Функция создания альбома
    @staticmethod
    async def create_album(data: AlbumCreate, db: AsyncSession, user_id: int) -> AlbumResponse:
        result = await db.execute(
            select(Album).where(Album.title == data.title, Album.owner_id == user_id)
        )
        existing_album = result.scalars().first()
        if existing_album:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have an album with this title"
            )

        new_album = Album(
            title=data.title,
            release_date=date.today(),
            owner_id=user_id
        )
        db.add(new_album)
        await db.commit()
        await db.refresh(new_album)

        return AlbumResponse(
            id=new_album.id,
            title=new_album.title,
            release_date=new_album.release_date,
            owner_id=new_album.owner_id,
            owner_name=new_album.owner.username,
            track_ids=[]
        )


#Функция получения альбома по id
    @staticmethod
    async def get_album(album_id: int, db: AsyncSession) -> AlbumResponse:
        result = await db.execute(
            select(Album)
            .options(joinedload(Album.tracks), joinedload(Album.owner))
            .where(Album.id == album_id)
        )
        album = result.scalars().first()
        if not album:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Album not found")

        return AlbumResponse(
            id=album.id,
            title=album.title,
            release_date=album.release_date,
            owner_id=album.owner_id,
            owner_name=album.owner.username,
            track_ids=[t.id for t in album.tracks]
        )
    

#Функция получения всех альбомов
    @staticmethod
    async def get_all_albums(db: AsyncSession) -> list[AlbumResponse]:
        result = await db.execute(
            select(Album)
            .options(joinedload(Album.tracks), joinedload(Album.owner))
        )
        albums = result.unique().scalars().all()

        return [
            AlbumResponse(
                id=a.id,
                title=a.title,
                release_date=a.release_date,
                owner_id=a.owner_id,
                owner_name=a.owner.username,
                track_ids=[t.id for t in a.tracks]
            )
            for a in albums
        ]


#Функция получения альбомов юзера
    @staticmethod
    async def get_user_albums(user_id: int, db: AsyncSession) -> list[AlbumResponse]:
        result = await db.execute(
            select(Album)
            .options(joinedload(Album.tracks), joinedload(Album.owner))
            .where(Album.owner_id == user_id)
        )
        albums = result.unique().scalars().all() 

        return [
            AlbumResponse(
                id=a.id,
                title=a.title,
                release_date=a.release_date,
                owner_id=a.owner_id,
                owner_name=a.owner.username,
                track_ids=[t.id for t in a.tracks]
            )
            for a in albums
        ]
    

#Функция удаления альбома
    @staticmethod
    async def delete_album(album_id: int, user_id: int, db: AsyncSession):
        result = await db.execute(select(Album).where(Album.id == album_id))
        album = result.scalars().first()
        if not album:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Album not found")
        if album.owner_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        await db.delete(album)
        await db.commit()
        return {"message": "Album deleted"}
