from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.services.album_service import AlbumService
from app.schemas.album import AlbumCreate, AlbumResponse

router = APIRouter(prefix="/albums", tags=["Albums"])

@router.post("/", response_model=AlbumResponse)
async def create_album(
    album: AlbumCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    return await AlbumService.create_album(album, db, user.id)

@router.get("/all", response_model=list[AlbumResponse])
async def get_all_albums(db: AsyncSession = Depends(get_db)):
    return await AlbumService.get_all_albums(db)


@router.get("/my", response_model=list[AlbumResponse])
async def get_user_albums(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    return await AlbumService.get_user_albums(user.id, db)

@router.get("/{album_id}", response_model=AlbumResponse)
async def get_album(album_id: int, db: AsyncSession = Depends(get_db)):
    return await AlbumService.get_album(album_id, db)

@router.delete("/{album_id}")
async def delete_album(album_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    return await AlbumService.delete_album(album_id, user.id, db)
