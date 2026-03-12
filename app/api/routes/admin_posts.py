from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.core.database import get_db
from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostCreate, PostResponse, PostUpdate, PostListResponse

router = APIRouter(prefix="/api/admin/posts", tags=["admin-posts"])


@router.get("", response_model=list[PostListResponse])
def get_admin_posts(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    posts = db.query(Post).order_by(Post.created_at.desc()).all()
    return posts


@router.get("/id/{id}", response_model=PostResponse)
def get_admin_post_by_id(
    id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    post = db.get(Post, id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    payload: PostCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    existing = db.query(Post).filter(Post.slug == payload.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Slug already exists")

    post = Post(
        slug=payload.slug,
        title=payload.title,
        content=payload.content,
        cover_img=payload.cover_img,
        status=payload.status,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.put("/{id}", response_model=PostResponse)
def update_post(
    id: int,
    payload: PostUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    post = db.get(Post, id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if payload.slug is not None and payload.slug != post.slug:
        slug_exists = db.query(Post).filter(Post.slug == payload.slug).first()
        if slug_exists:
            raise HTTPException(status_code=400, detail="Slug already exists")
        post.slug = payload.slug

    if payload.title is not None:
        post.title = payload.title
    if payload.content is not None:
        post.content = payload.content
    if payload.cover_img is not None:
        post.cover_img = payload.cover_img
    if payload.status is not None:
        post.status = payload.status

    db.commit()
    db.refresh(post)
    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    post = db.get(Post, id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    db.delete(post)
    db.commit()
    return None