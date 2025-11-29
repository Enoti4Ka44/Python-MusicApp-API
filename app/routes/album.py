from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.services.album_service import AlbumService
from app.schemas.album import AlbumCreate, AlbumResponse

router = APIRouter(prefix="/albums", tags=["Albums"])

#Эндпоинт создания альбома
@router.post("/", response_model=AlbumResponse,
    description=(
        "Создает новый альбом" 
    ))
async def create_album(
    album: AlbumCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    return await AlbumService.create_album(album, db, user.id)

#Эндпоинт получения всех альбомов
@router.get("/", response_model=list[AlbumResponse],
    description=(
        "Возвращает список всех альбомов " 
    ))
async def get_all_albums(db: AsyncSession = Depends(get_db)):
    return await AlbumService.get_all_albums(db)

#Эндпоинт получения альбомов юзера
@router.get("/my", response_model=list[AlbumResponse],
    summary="Get User Albums",
    description=(
        "Возвращает список альбомов пользователя " 
    ))
async def get_user_albums(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    return await AlbumService.get_user_albums(user.id, db)

#Эндпоинт получения альбома по id
@router.get("/{album_id}", response_model=AlbumResponse,
    summary="Get Album by ID",
    description=(
        "Возвращает информацию об альбоме " 
    ))
async def get_album(album_id: int, db: AsyncSession = Depends(get_db)):
    return await AlbumService.get_album(album_id, db)

#Эндпоинт удаления альбома
@router.delete("/{album_id}",
               description=(
        "Удаляет альбом. " 
        "Доступно только его владельцу"
    ))
async def delete_album(album_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    return await AlbumService.delete_album(album_id, user.id, db)
