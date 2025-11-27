from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.auth.security import hash_password, verify_password
from app.auth.jwt_handler import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse)
async def register_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.email == data.email)
    result = await db.execute(query)
    existing = result.scalars().first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )

    new_user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),  
)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post("/login")
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.email == data.email)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token({"sub": str(user.id)})

    return {"access_token": access_token, "token_type": "bearer"}
