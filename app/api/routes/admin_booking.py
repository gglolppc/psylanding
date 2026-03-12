from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.core.database import get_db
from app.models.booking import Booking
from app.models.user import User
from app.schemas.booking import BookingResponse

router = APIRouter(prefix="/api/admin/booking", tags=["admin-booking"])


@router.get("", response_model=list[BookingResponse])
def get_admin_bookings(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    bookings = db.query(Booking).order_by(Booking.created_at.desc()).all()
    return bookings