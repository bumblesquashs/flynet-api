from fastapi.routing import APIRouter

from .user import router as user_router
from .flight_logs import router as flight_log_router
from .airports import router as airport_router
from .aircraft import router as aircraft_router
from .airlines import router as airline_router
from .user_settings import router as user_profile_router
from .admin import router as admin_router

router = APIRouter()
router.include_router(user_router, prefix="/user", tags=["Users"])
router.include_router(flight_log_router, prefix="/flight_logs", tags=["Flight Logs"])
router.include_router(airport_router, prefix="/airport", tags=["Airports"])
router.include_router(aircraft_router, prefix="/aircraft", tags=["Aircraft"])
router.include_router(airline_router, prefix="/airline", tags=["Airlines"])
router.include_router(user_profile_router, prefix="/user_settings", tags=["User Settings"])
router.include_router(admin_router, prefix="/admin", tags=["Admin Endpoints"])

