from app.routers.users import router as users_router
from app.routers.lessons import router as lessons_router
from app.routers.chat import router as chat_router
from app.routers.figures import router as figures_router
from app.routers.social import router as social_router

__all__ = [
    "users_router",
    "lessons_router",
    "chat_router",
    "figures_router",
    "social_router",
]
