import uvicorn
from starlette.staticfiles import StaticFiles

from api.core import router as core_router
from api.v1 import router as v1_router
from core.settings import settings
from fastapi import FastAPI
from schema import init_relationships
from starlette.middleware.cors import CORSMiddleware
from utils import get_log
from utils.populate import all_data

app = FastAPI(
    title=settings.PROJECT_NAME, root_path=settings.HOST_PREFIX, openapi_url=f"{settings.API_V1_PREFIX}/openapi.json"
)

# Mount static files
app.mount("/static/profile/thumbnails", StaticFiles(directory="../ProfileImages"), name="profiles")

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:

    allowed_cors_origins = [str(origin).rstrip('/') for origin in settings.BACKEND_CORS_ORIGINS]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(core_router)
app.include_router(v1_router)


init_relationships()

if __name__ == "__main__":
    if settings.INTERNAL_DEV_MODE:
        all_data(drop_db=False)

    log = get_log(name="developer.portal.api", logging_level=settings.LOGGING_LEVEL)
    # Disabling this, because we want to trap exceptions at this level and have them logged.
    # pylint: disable=broad-except
    try:
        uvicorn.run(
            "portal:app",
            host=settings.SERVER_HOST,
            port=settings.SERVER_PORT,
            reload=True,
            access_log=False,
            forwarded_allow_ips='*', # What is this for, you may ask? Well, if you have an API endpoint that is like
            proxy_headers=True       # '/api/something' but you call '/api/something/' (note slash), then uvicorn will
                                     # helpfully issue a 307 redirect to what you want. However, when the app is
                                     # behind a reverse proxy as our staging and prod apps are, then you get this
                                     # behaviour where any https calls get redirected to http calls, which breaks the
                                     # rule where api calls must be https from and https page (like prod) leading to
                                     # the entire request getting blocked and causing immense sadness and confusion.
                                     # these settings fix that problem by telling uvicorn to "trust" the request
                                     # and to accept proxy headers somehow? See uvicorn docs and also about running
                                     # behind nginx as we do.
        )
    except Exception as e:
        log.critical(e)
