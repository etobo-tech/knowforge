from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.chats import router as chats_router
from api.routes.documents import router as documents_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://knowforge.etobo.tech",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents_router, prefix="/api")
app.include_router(chats_router, prefix="/api")


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Hello, World!"}
