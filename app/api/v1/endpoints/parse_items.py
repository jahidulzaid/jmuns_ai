from fastapi import APIRouter, HTTPException
from app.schemas.parse_items import ParseItemsRequest, ParseItemsResponse
from app.services.parse_items_service import parse_estimate_items

router = APIRouter()


@router.post("/estimate/parse-items", response_model=ParseItemsResponse)
def parse_items(payload: ParseItemsRequest) -> ParseItemsResponse:
    try:
        return parse_estimate_items(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
