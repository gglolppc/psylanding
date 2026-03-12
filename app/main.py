from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes.booking import router as booking_router
from app.api.routes.blog import router as blog_router
from app.api.routes.admin_posts import router as admin_posts_router
from app.api.routes.admin_booking import router as admin_booking_router
from app.api.routes.auth import router as auth_router
from app.web.routes.pages import router as pages_router
from app.web.routes.admin import router as admin_pages_router
from app.web.routes.admin_auth import router as admin_login


app = FastAPI(title="Psychologist Site")



app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(pages_router)
app.include_router(admin_pages_router)

app.include_router(auth_router)
app.include_router(booking_router)
app.include_router(blog_router)
app.include_router(admin_posts_router)
app.include_router(admin_booking_router)
app.include_router(admin_login)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/hello")
def hello():
    return {"message": "Hello from FastAPI"}