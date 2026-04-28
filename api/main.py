from fastapi import FastAPI

from app.api.routes.files import router as files_router
from app.api.routes.health import router as health_router

app = FastAPI(title="Knowforge API")
app.include_router(health_router)
app.include_router(files_router)
