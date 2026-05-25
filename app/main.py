from fastapi import FastAPI
from app.routes.main import router

app = FastAPI(title="Lumora AI")

app.include_router(router)
