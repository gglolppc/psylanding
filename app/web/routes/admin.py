from pathlib import Path
from secrets import token_hex
import shutil

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.booking import Booking
from app.models.post import Post
from app.api.deps import get_current_admin
from app.models.user import User
from fastapi import Request
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/admin", tags=["admin-pages"])
templates = Jinja2Templates(directory="app/templates")

UPLOAD_DIR = Path("app/static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def slugify(text: str) -> str:
    value = text.strip().lower()
    out = []
    prev_dash = False
    for ch in value:
        if ch.isalnum():
            out.append(ch)
            prev_dash = False
        else:
            if not prev_dash:
                out.append("-")
                prev_dash = True
    result = "".join(out).strip("-")
    return result or token_hex(4)

@router.get("", response_class=HTMLResponse)
def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):


    bookings_count = db.query(Booking).count()
    posts_count = db.query(Post).count()
    published_count = db.query(Post).filter(Post.status == "published").count()
    latest_bookings = db.query(Booking).order_by(Booking.created_at.desc()).limit(8).all()
    latest_posts = db.query(Post).order_by(Post.created_at.desc()).limit(6).all()

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "page_title": "Админка",
            "admin": admin,
            "bookings_count": bookings_count,
            "posts_count": posts_count,
            "published_count": published_count,
            "latest_bookings": latest_bookings,
            "latest_posts": latest_posts,
            "active_tab": "dashboard",
        },
    )

@router.get("/bookings", response_class=HTMLResponse)
def admin_bookings(
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    bookings = db.query(Booking).order_by(Booking.created_at.desc()).all()
    return templates.TemplateResponse(
        "admin/bookings.html",
        {
            "request": request,
            "page_title": "Записи",
            "admin": admin,
            "bookings": bookings,
            "active_tab": "bookings",
        },
    )

@router.get("/posts", response_class=HTMLResponse)
def admin_posts(
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    posts = db.query(Post).order_by(Post.created_at.desc()).all()
    return templates.TemplateResponse(
        "admin/posts.html",
        {
            "request": request,
            "page_title": "Посты",
            "admin": admin,
            "posts": posts,
            "active_tab": "posts",
        },
    )

@router.get("/posts/new", response_class=HTMLResponse)
def admin_post_new(
    request: Request,
    admin: User = Depends(get_current_admin),
):
    return templates.TemplateResponse(
        "admin/post_form.html",
        {
            "request": request,
            "page_title": "Новый пост",
            "admin": admin,
            "post": None,
            "active_tab": "posts",
            "form_action": "/admin/posts/new",
            "submit_label": "Создать пост",
        },
    )

@router.post("/posts/new")
def admin_post_create(
    request: Request,
    title: str = Form(...),
    slug: str = Form(""),
    content: str = Form(...),
    status: str = Form(...),
    cover: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    final_slug = slugify(slug or title)

    exists = db.query(Post).filter(Post.slug == final_slug).first()
    if exists:
        raise HTTPException(status_code=400, detail="Slug already exists")

    cover_img = None
    if cover and cover.filename:
        ext = Path(cover.filename).suffix.lower()
        filename = f"{token_hex(8)}{ext}"
        filepath = UPLOAD_DIR / filename
        with filepath.open("wb") as buffer:
            shutil.copyfileobj(cover.file, buffer)
        cover_img = f"/static/uploads/{filename}"

    post = Post(
        title=title.strip(),
        slug=final_slug,
        content=content,
        status=status,
        cover_img=cover_img,
    )
    db.add(post)
    db.commit()

    return RedirectResponse(url="/admin/posts", status_code=303)

@router.get("/posts/{id}/edit", response_class=HTMLResponse)
def admin_post_edit(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    post = db.get(Post, id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return templates.TemplateResponse(
        "admin/post_form.html",
        {
            "request": request,
            "page_title": f"Редактировать: {post.title}",
            "admin": admin,
            "post": post,
            "active_tab": "posts",
            "form_action": f"/admin/posts/{post.id}/edit",
            "submit_label": "Сохранить изменения",
        },
    )

@router.post("/posts/{id}/edit")
def admin_post_update(
    id: int,
    title: str = Form(...),
    slug: str = Form(...),
    content: str = Form(...),
    status: str = Form(...),
    cover: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    post = db.get(Post, id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    final_slug = slugify(slug or title)
    slug_exists = db.query(Post).filter(Post.slug == final_slug, Post.id != id).first()
    if slug_exists:
        raise HTTPException(status_code=400, detail="Slug already exists")

    post.title = title.strip()
    post.slug = final_slug
    post.content = content
    post.status = status

    if cover and cover.filename:
        ext = Path(cover.filename).suffix.lower()
        filename = f"{token_hex(8)}{ext}"
        filepath = UPLOAD_DIR / filename
        with filepath.open("wb") as buffer:
            shutil.copyfileobj(cover.file, buffer)
        post.cover_img = f"/static/uploads/{filename}"

    db.commit()
    return RedirectResponse(url="/admin/posts", status_code=303)

@router.post("/posts/{id}/delete")
def admin_post_delete(
    id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    post = db.get(Post, id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    db.delete(post)
    db.commit()
    return RedirectResponse(url="/admin/posts", status_code=303)


@router.get("/logout")
def admin_logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    return response


@router.get("/admin/logout")
def logout():

    response = RedirectResponse("/admin/login")

    response.delete_cookie("access_token")

    return response