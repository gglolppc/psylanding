from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class BookingCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    phone: str = Field(min_length=5, max_length=50)
    email: EmailStr
    message: str | None = Field(default=None, max_length=5000)
    preferred_time: str | None = Field(default=None, max_length=100)


class BookingResponse(BaseModel):
    id: int
    name: str
    phone: str
    email: EmailStr
    message: str | None
    preferred_time: str | None
    created_at: datetime

    model_config = {"from_attributes": True}