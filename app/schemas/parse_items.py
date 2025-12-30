from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class ParseContext(BaseModel):
    currency: str = Field(default="USD")
    locale: str = Field(default="en-US")
    default_taxable: Optional[bool] = Field(default=None, description="If user didn't specify tax, leave null unless you want a default.")


class ParseItemsRequest(BaseModel):
    text: str = Field(..., min_length=1)
    context: Optional[ParseContext] = None


class LineItem(BaseModel):
    description: str = Field(..., description="Main row description")
    rate: Optional[float] = Field(default=None, ge=0.0)
    quantity: Optional[int] = Field(default=None, ge=1)
    taxable: Optional[bool] = Field(default=None, description="Null if not found in text")
    markupPercent: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    # optional: a second-line note/description field if your UI supports it
    detail: Optional[str] = None


class ParseItemsResponse(BaseModel):
    items: List[LineItem]
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    notes: Optional[str] = None
