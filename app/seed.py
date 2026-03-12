from sqlalchemy.orm import Session

from app.core.database import SessionLocal, Base, engine
from app.core.security import hash_password
from app.models.user import User


def seed_admin():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    existing = db.query(User).filter(User.login == "admin").first()
    if existing:
        print("Admin already exists")
        db.close()
        return

    user = User(
        login="admin",
        password_hash=hash_password("admin123"),
        role="admin",
    )
    db.add(user)
    db.commit()
    db.close()
    print("Admin created: login=admin password=admin123")


if __name__ == "__main__":
    seed_admin()