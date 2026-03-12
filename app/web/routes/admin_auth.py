from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/admin/login")
def admin_login_page(request: Request):
    return templates.TemplateResponse(
        "admin/login.html",
        {"request": request},
    )


@router.post("/admin/login")
def admin_login(
    request: Request,
    login: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):

    user = db.query(User).filter(User.login == login).first()

    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            "admin/login.html",
            {"request": request, "error": "Invalid login"},
        )

    if user.role != "admin":
        return templates.TemplateResponse(
            "admin/login.html",
            {"request": request, "error": "Access denied"},
        )

    token = create_access_token(
        {"sub": str(user.id), "role": user.role}
    )

    response = RedirectResponse("/admin", status_code=303)

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
    )

    return response