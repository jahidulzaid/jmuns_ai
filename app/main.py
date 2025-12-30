from fastapi import FastAPI
from app.api.v1 import api_router

app = FastAPI(title="Rapidbid Estimate Parser", version="1.0.0")

app.include_router(api_router.router, prefix="/api/v1")
