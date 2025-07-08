import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, ARRAY, ForeignKey


load_dotenv()
DB_LOGIN = os.getenv("DB_LOGIN")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")


engine = create_async_engine(f'postgresql+asyncpg://{DB_LOGIN}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

async_session = async_sessionmaker(engine, expire_on_commit=False)

class Model(DeclarativeBase):
    pass


class TracksOrm(Model):
    __tablename__ = 'tracks'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    artists: Mapped[list[str]] = mapped_column(ARRAY(String(255)), nullable=False)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String(255)), nullable=False)
    url: Mapped[str] = mapped_column(String(255), nullable=False)


class UsersOrm(Model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    username: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    playlists = relationship("PlaylistsOrm", back_populates="user", cascade="all, delete-orphan")


class PlaylistsOrm(Model):
    __tablename__ = 'playlists'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str]  = mapped_column(String(255), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)

    user = relationship("UsersOrm", back_populates="playlists")
    tracks = relationship("PlaylistTracksOrm", back_populates="playlist", cascade="all, delete-orphan")


class PlaylistTracksOrm(Model):
    __tablename__ = 'playlist_tracks'

    playlist_id: Mapped[int] = mapped_column(ForeignKey('playlists.id'), index=True, primary_key=True)
    track_id: Mapped[int] = mapped_column(ForeignKey('tracks.id'), index=True, primary_key=True)

    playlist = relationship("PlaylistsOrm", back_populates="tracks")
    track = relationship("TracksOrm")
