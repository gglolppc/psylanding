from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.post import Post
from app.schemas.post import PostListResponse, PostResponse

router = APIRouter(prefix="/api/posts", tags=["blog"])


@router.get("", response_model=list[PostListResponse])
def get_posts(db: Session = Depends(get_db)):
    posts = (
        db.query(Post)
        .filter(Post.status == "published")
        .order_by(Post.created_at.desc())
        .all()
    )
    return posts


@router.get("/{slug}", response_model=PostResponse)
def get_post_by_slug(slug: str, db: Session = Depends(get_db)):
    post = (
        db.query(Post)
        .filter(Post.slug == slug, Post.status == "published")
        .first()
    )
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post