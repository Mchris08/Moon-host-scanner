from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.auth import require_user
from app.db import SessionLocal, ScanJob

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return RedirectResponse("/dashboard" if request.cookies.get("session") else "/login")

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, user=Depends(require_user)):
    db = SessionLocal()
    try: jobs = db.query(ScanJob).order_by(ScanJob.created_at.desc()).limit(5).all()
    finally: db.close()
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "jobs": jobs})
