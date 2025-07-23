from datetime import date
from typing import Optional
from pydantic import BaseModel, validator

class Receipt(BaseModel):
    vendor: str
    date: date
    amount: float
    category: Optional[str] = None

    # simple sanity-check
    @validator("amount")
    def positive_amount(cls, v):
        assert v >= 0, "Amount must be non-negative"
        return v
