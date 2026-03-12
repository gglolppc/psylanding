from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class PostBase(BaseModel):
    slug: str = Field(min_length=3, max_length=255)
    title: str = Field(min_length=3, max_length=255)
    content: str = Field(min_length=10)
    cover_img: str | None = Field(default=None, max_length=500)
    status: str = Field(default="draft")

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        allowed = {"draft", "published"}
        if value not in allowed:
            raise ValueError("status must be 'draft' or 'published'")
        return value


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    slug: str | None = Field(default=None, min_length=3, max_length=255)
    title: str | None = Field(default=None, min_length=3, max_length=255)
    content: str | None = Field(default=None, min_length=10)
    cover_img: str | None = Field(default=None, max_length=500)
    status: str | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        if value is None:
            return value
        allowed = {"draft", "published"}
        if value not in allowed:
            raise ValueError("status must be 'draft' or 'published'")
        return value


class PostResponse(BaseModel):
    id: int
    slug: str
    title: str
    content: str
    cover_img: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PostListResponse(BaseModel):
    id: int
    slug: str
    title: str
    cover_img: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}