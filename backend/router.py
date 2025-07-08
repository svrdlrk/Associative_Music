import os
from typing import List

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.database import async_session, TracksOrm, PlaylistsOrm, PlaylistTracksOrm, UsersOrm
from backend.models import  Track, TrackAdd, Playlist, PlaylistCreate, PlaylistWithTracks
from backend.auth import decode_access_token
from backend.logger_config import logger

router = APIRouter(tags=["Треки и Плейлисты"])
bearer_scheme = HTTPBearer()
load_dotenv()
ADMIN_LIST = os.getenv("ADMIN_LIST", "")
admin_list = [email.strip() for email in ADMIN_LIST.split(",") if email.strip()]

async def get_db():
    async with async_session() as session:
        yield session

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
                           db: AsyncSession = Depends(get_db)):
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        logger.warning("Недействительный токен при попытке авторизации")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недействительный токен")
    user_id = int(payload["sub"])
    user = await db.get(UsersOrm, user_id)
    if not user:
        logger.warning(f"Пользователь с id={user_id} не найден при попытке авторизации")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    logger.debug(f"Пользователь {user.username} (id={user.id}) успешно авторизован")
    return user


async def validate_playlist_owner(playlist_id: int, user: UsersOrm, db: AsyncSession) -> PlaylistsOrm:
    playlist = await db.get(PlaylistsOrm, playlist_id)
    if not playlist:
        logger.warning(f"Плейлист id={playlist_id} не найден при валидации владельца (user_id={user.id})")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Такого плейлиста не существует")
    if playlist.user_id != user.id:
        logger.warning(f"Пользователь id={user.id} пытался получить доступ к чужому плейлисту id={playlist_id}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Вы не являетесь создателем этого плейлиста")
    logger.debug(f"Пользователь id={user.id} успешно прошёл валидацию владельца для плейлиста id={playlist_id}")
    return playlist


@router.get("/tracks", response_model=List[Track], summary= "Получить все треки",
            description="Возвращает список всех треков из базы данных")
async def get_tracks(limit: int = Query(10, le=100),
                     offset: int = Query(0),
                     db: AsyncSession = Depends(get_db)):
    logger.info(f"Запрос списка треков с лимитом={limit} и смещением={offset}")
    result = await db.execute(select(TracksOrm).order_by(TracksOrm.id).limit(limit).offset(offset))
    tracks = result.scalars().all()
    logger.info(f"Возвращено треков: {len(tracks)}")
    return [Track.model_validate(t) for t in tracks]


@router.post("/tracks", response_model=Track, summary="Добавить новый трек в Базу Данных(админ-функция)",
             description="Добавляет трек в базу данных и возвращает его данные")
async def add_track(track: TrackAdd,
                    db: AsyncSession = Depends(get_db),
                    user: UsersOrm = Depends(get_current_user)):
    logger.info(f"Пользователь {user.email} пытается добавить новый трек: {track.title}")
    if user.email not in admin_list:
        logger.warning(f"Пользователь {user.email} не является администратором и попытался добавить трек")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только администратор может добавлять треки")
    new_track = TracksOrm(**track.model_dump())
    db.add(new_track)
    await db.commit()
    await db.refresh(new_track)
    logger.info(f"Новый трек добавлен: id={new_track.id}, title={new_track.title}")
    return Track.model_validate(new_track)


@router.post("/playlists", response_model= Playlist, summary="Создать плейлист",
             description="Создает плейлист")
async def create_playlist(
        playlist: PlaylistCreate,
        user: UsersOrm = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    logger.info(f"Пользователь id={user.id} создаёт плейлист: {playlist.name}")
    if not user:
        logger.error("Пользователь не найден при создании плейлиста")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    new_playlist = PlaylistsOrm(name=playlist.name, user_id=user.id)
    db.add(new_playlist)
    await db.commit()
    await db.refresh(new_playlist)
    logger.info(f"Плейлист создан: id={new_playlist.id}, name={new_playlist.name}, user_id={user.id}")
    return Playlist.model_validate(new_playlist)

@router.get("/playlists", response_model=List[Playlist], summary="Получить все плейлисты пользователя",
            description="Возвращает список всех плейлистов пользователя из базы данных")
async def get_playlist( user: UsersOrm = Depends(get_current_user),
                        db: AsyncSession = Depends(get_db)):
    logger.info(f"Пользователь id={user.id} запрашивает список своих плейлистов")
    result = await db.execute(select(PlaylistsOrm).where(PlaylistsOrm.user_id == user.id).order_by(PlaylistsOrm.id))
    playlist = result.scalars().all()
    logger.info(f"Найдено плейлистов: {len(playlist)} для пользователя id={user.id}")
    return [Playlist.model_validate(p) for p in playlist]


@router.get("/playlists/{playlist_id}/tracks", response_model=PlaylistWithTracks, summary="Открыть плейлист",
            description="Отображает все треки в плейлисте пользователя")
async def get_playlist_tracks(playlist_id: int,
                              db: AsyncSession = Depends(get_db),
                              user: UsersOrm = Depends(get_current_user)):
    logger.info(f"Пользователь id={user.id} запрашивает треки плейлиста id={playlist_id}")
    playlist = await validate_playlist_owner(playlist_id, user, db)

    result = await db.execute(select(TracksOrm)
                              .join(PlaylistTracksOrm, TracksOrm.id == PlaylistTracksOrm.track_id)
                              .where(PlaylistTracksOrm.playlist_id == playlist_id))
    tracks = result.scalars().all()
    logger.info(f"В плейлисте id={playlist_id} найдено треков: {len(tracks)}")
    return PlaylistWithTracks.model_validate({
        "id": playlist.id,
        "name": playlist.name,
        "user_id": playlist.user_id,
        "tracks": tracks
    })

@router.post("/playlists/{playlist_id}/tracks/{track_id}", summary="Добавить трек в плейлист",
             description="Добавляет выбранный трек в указанный плейлист пользователя")
async def add_to_playlist(playlist_id: int,
                          track_id: int,
                          user: UsersOrm = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
    logger.info(f"Пользователь id={user.id} пытается добавить трек id={track_id} в плейлист id={playlist_id}")
    playlist = await validate_playlist_owner(playlist_id, user, db)
    track = await db.get(TracksOrm, track_id)

    if not track:
        logger.warning(f"Попытка добавить несуществующий трек id={track_id} в плейлист id={playlist_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Такой трек не найден")


    existing = await db.execute(select(PlaylistTracksOrm)
                                .where(PlaylistTracksOrm.playlist_id == playlist.id,
                                       PlaylistTracksOrm.track_id == track_id))
    if existing.scalar_one_or_none():
        logger.warning(f"Попытка добавить уже существующий трек id={track_id} в плейлист id={playlist_id}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Трек уже находится в плейлисте")

    association = PlaylistTracksOrm(playlist_id=playlist.id, track_id=track.id)
    db.add(association)
    await db.commit()
    await db.refresh(association)
    logger.info(f"Трек id={track_id} добавлен в плейлист id={playlist_id} пользователем id={user.id}")
    return {"message": "Трек добавлен"}


@router.delete("/playlists/{playlist_id}", summary="Удалить плейлист",
               description="Удаляет плейлист, если пользователь является его создателем")
async def delete_playlist(
    playlist_id: int,
    user: UsersOrm = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"Пользователь id={user.id} пытается удалить плейлист id={playlist_id}")
    playlist = await validate_playlist_owner(playlist_id, user, db)

    await db.delete(playlist)
    await db.commit()
    logger.info(f"Плейлист id={playlist_id} удалён пользователем id={user.id}")
    return {"message": f"Плейлист с ID {playlist_id} удалён"}


@router.delete("/playlists/{playlist_id}/tracks/{track_id}", summary="Удалить трек из плейлиста",
               description="Удаляет указанный трек из плейлиста")
async def delete_from_playlist(playlist_id: int,
                               track_id: int,
                               user: UsersOrm = Depends(get_current_user),
                               db: AsyncSession = Depends(get_db)):
    logger.info(f"Пользователь id={user.id} пытается удалить трек id={track_id} из плейлиста id={playlist_id}")
    playlist = await validate_playlist_owner(playlist_id, user, db)

    result = await db.execute(select(PlaylistTracksOrm)
                              .where(PlaylistTracksOrm.playlist_id == playlist_id,
                                     PlaylistTracksOrm.track_id == track_id))
    association = result.scalar_one_or_none()

    if not association:
        logger.warning(f"Трек id={track_id} в плейлисте id={playlist_id} не найден при попытке удаления")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Трек в плейлисте не найден")

    await db.delete(association)
    await db.commit()
    logger.info(f"Трек id={track_id} удалён из плейлиста id={playlist_id} пользователем id={user.id}")
    return {"message": f"Трек удален"}
