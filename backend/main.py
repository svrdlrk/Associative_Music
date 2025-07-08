from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from backend.router import router as tracks_router
from backend.auth_router import router as auth_router


app = FastAPI(title="Associative Playlist API",
              description="API для управления плейлистами и треками",
              contact={
        "name": "Kirill Sviridov",
        "email": "svrdlrk@gmail.com",},
              )
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.include_router(auth_router)
app.include_router(tracks_router)
