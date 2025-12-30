from fastapi import APIRouter
from app.api.v1.endpoints.parse_items import router as parse_items_router

router = APIRouter()
router.include_router(parse_items_router, tags=["Estimate Parsing"])
