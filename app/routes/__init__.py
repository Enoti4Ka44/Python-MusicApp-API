from .auth import router as auth_router
from .album import router as album_router
from .track import router as track_router
from .playlist import router as playlist_router

routers = [auth_router, playlist_router, track_router, album_router]