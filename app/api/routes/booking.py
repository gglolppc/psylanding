from fastapi import APIRouter, Depends, Form, BackgroundTasks

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.booking import Booking
from app.services.telegram import send_booking_notification

router = APIRouter(tags=["booking"])

@router.post("/booking")
async def create_booking(
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(None),
    preferred_time: str = Form(None),
    message: str = Form(None),
    db: Session = Depends(get_db)
):
    # 1. Пишем в базу
    booking = Booking(
        name=name,
        phone=phone,
        email=email,
        preferred_time=preferred_time,
        message=message
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    # 2. Отправляем в ТГ фоном (не тормозим юзера)
    background_tasks.add_task(send_booking_notification, booking)

    # 3. Редирект обратно на страницу с формой (чтобы выскочило "Успешно")
    return {"status": "ok"}