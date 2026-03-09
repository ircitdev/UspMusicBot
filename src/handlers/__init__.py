from aiogram import Router
from . import start, song_creation, voice, balance, playlists, admin, callbacks

def setup_routers() -> Router:
    router = Router()
    router.include_router(start.router)
    router.include_router(voice.router)
    router.include_router(song_creation.router)
    router.include_router(balance.router)
    router.include_router(playlists.router)
    router.include_router(admin.router)
    router.include_router(callbacks.router)
    return router
