from fastapi.routing import APIRouter

from .user import router as user_router
from .flight_logs import router as flight_log_router


router = APIRouter()
router.include_router(user_router, prefix="/user", tags=["Users"])
router.include_router(flight_log_router, prefix="/flight_logs", tags=["Flight Logs"])
