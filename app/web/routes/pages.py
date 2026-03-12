from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.post import Post
from app.models.booking import Booking
from pathlib import Path
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    certs_dir = Path("app/static/img/certificates")
    allowed_ext = {".jpg", ".jpeg", ".png", ".webp"}

    certificate_images = []
    if certs_dir.exists():
        certificate_images = sorted(
            [
                f"/static/img/certificates/{file.name}"
                for file in certs_dir.iterdir()
                if file.is_file() and file.suffix.lower() in allowed_ext
            ]
        )

    return templates.TemplateResponse(
        "pages/home.html",
        {
            "request": request,
            "certificate_images": certificate_images,
        },
    )


@router.get("/blog", response_class=HTMLResponse)
def blog_list(request: Request, db: Session = Depends(get_db)):
    posts = (
        db.query(Post)
        .filter(Post.status == "published")
        .order_by(Post.created_at.desc())
        .all()
    )
    return templates.TemplateResponse(
        "pages/blog_list.html",
        {
            "request": request,
            "page_title": "Блог",
            "posts": posts,
        },
    )


@router.get("/blog/{slug}", response_class=HTMLResponse)
def blog_detail(slug: str, request: Request, db: Session = Depends(get_db)):
    post = (
        db.query(Post)
        .filter(Post.slug == slug, Post.status == "published")
        .first()
    )

    if not post:
        return templates.TemplateResponse(
            "pages/404.html",
            {"request": request, "page_title": "Не найдено"},
            status_code=404,
        )

    return templates.TemplateResponse(
        "pages/blog_detail.html",
        {
            "request": request,
            "page_title": post.title,
            "post": post,
        },
    )


# @router.post("/booking")
# def booking_submit(
#     name: str = Form(...),
#     phone: str = Form(...),
#     email: str = Form(""),
#     message: str = Form(""),
#     preferred_time: str = Form(""),
#     db: Session = Depends(get_db),
# ):
#     booking = Booking(
#         name=name,
#         phone=phone,
#         email=email,
#         message=message,
#         preferred_time=preferred_time,
#     )
#     db.add(booking)
#     db.commit()
#
#     return RedirectResponse(url="/?success=1", status_code=303)