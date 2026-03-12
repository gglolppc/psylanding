from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_admin(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:

    token = None

    # 1 header (API)
    if credentials:
        token = credentials.credentials

    # 2 cookie (Jinja admin)
    if not token:
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401)

    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401)

    user_id = payload.get("sub")
    user = db.get(User, int(user_id))

    if not user or user.role != "admin":
        raise HTTPException(status_code=403)

    return user