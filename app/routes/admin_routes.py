from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.admin import require_admin
from app.db import SessionLocal, HostSubmission

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="app/templates")

@router.get("/queue", response_class=HTMLResponse)
def queue(request: Request, admin=Depends(require_admin)):
    db = SessionLocal()
    try: hosts = db.query(HostSubmission).filter_by(status="pending").all()
    finally: db.close()
    return templates.TemplateResponse("admin_queue.html", {"request": request, "hosts": hosts, "admin": admin})
