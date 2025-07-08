from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


class UserRegister(BaseModel):
    email: str = Field(..., examples=["example@email.com"])
    username: str = Field(..., examples=["username"])
    password: str = Field(..., examples=["password"])


class UserLogin(BaseModel):
    email: Optional[str] = Field(..., examples=["example@email.com"])
    username: Optional[str] = Field(..., examples=["username"])
    password: str = Field(..., examples=["password"])

    @model_validator(mode='after')
    def validate_login(cls, values):
        email, username = values.email, values.username
        if not email and not username:
            raise ValueError("Необходимо указать либо username, либо email")
        return values

class TrackAdd(BaseModel):
    title: str = Field(..., examples=["Song Title"])
    artists: List[str] = Field(..., examples=[["Song Artist"]])
    tags: List[str] = Field(..., examples=[["rock", "pop", "hip-hop"]])
    url: str = Field(..., examples=["Song Url"])


class Track(TrackAdd):
    id: int = Field(..., examples=[0])

    model_config = {
        "from_attributes": True
    }


class PlaylistCreate(BaseModel):
    name: str = Field(..., max_length=100, examples=["Playlist Name"])


class Playlist(PlaylistCreate):
    id: int = Field(..., examples=[0])
    user_id: int = Field(..., examples=[1])

    model_config = {
        "from_attributes": True
    }


class PlaylistWithTracks(Playlist):
    tracks: List[Track] = Field(..., examples=[[{
        "id": 0,
        "title": "Song Title",
        "artists": ["Song Artist"],
        "tags": ["rock", "pop", "hip-hop"],
        "url": "Song Url"
    }]])

