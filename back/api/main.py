from fastapi import FastAPI
from api.routes.documents import router as documents_router


app = FastAPI()
app.include_router(documents_router, prefix="/api")


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
