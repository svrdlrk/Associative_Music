from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from backend.models import UserRegister, UserLogin
from backend.database import async_session, UsersOrm
from backend.auth import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from backend.logger_config import logger


router = APIRouter(prefix="/auth", tags=["Аутентификация"])

async def get_db():
    async with async_session() as session:
        yield session


@router.post("/register",status_code=status.HTTP_201_CREATED, summary="Регистрация нового пользователя")
async def register(user: UserLogin, db: AsyncSession = Depends(get_db)):
    logger.info(f"Регистрация пользователя: {user.username}/{user.email}")
    query = await db.execute(
        select(UsersOrm).where(
            or_(
                UsersOrm.email == user.email,
                UsersOrm.username == user.username
            )
        )
    )
    existing_user = query.scalar_one_or_none()
    if existing_user:
        logger.error(f"Пользователь с таким username или email уже существует: {user.username}/{user.email}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь с таким username или email уже существует")
    hashed_password = get_password_hash(user.password)
    new_user = UsersOrm(
        email=user.email,
        username=user.username,
        password=hashed_password
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    logger.info(f"Пользователь зарегистрирован: {user.username}/{user.email}")
    return {"message": "Пользователь успешно зарегистрирован"}


@router.post("/login", summary="Вход пользователя")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    logger.info(f"Попытка входа пользователя: {user.username or user.email}")
    query = await db.execute(
        select(UsersOrm).where(
            or_(
                UsersOrm.email == user.email,
                UsersOrm.username == user.username
            )
        )
    )
    db_user = query.scalar_one_or_none()

    if not db_user or not verify_password(user.password, db_user.password):
        logger.error(f"Неуспешная попытка входа: {user.username or user.email}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверные данные пользователя")

    access_token_expires = ACCESS_TOKEN_EXPIRE_MINUTES
    access_token = create_access_token(
        data={"sub": str(db_user.id)}, expires_delta=timedelta(minutes=access_token_expires)
    )
    logger.info(f"Пользователь вошел: {user.username or user.email}")
    return {"access_token": access_token, "token_type": "bearer"}