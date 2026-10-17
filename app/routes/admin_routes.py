from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.admin import require_admin
from app.db import SessionLocal, HostSubmission
from datetime import datetime

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="app/templates")

@router.get("/queue", response_class=HTMLResponse)
def queue(request: Request, admin=Depends(require_admin)):
    db = SessionLocal()
    try: hosts = db.query(HostSubmission).filter_by(status="pending").all()
    finally: db.close()
    return templates.TemplateResponse("admin_queue.html", {"request": request, "hosts": hosts, "admin": admin})

@router.post("/queue/approve/{host_id}")
def approve(host_id: int, admin=Depends(require_admin)):
    db = SessionLocal()
    try:
        host = db.query(HostSubmission).get(host_id)
        if host:
            host.status = "approved"
            host.reviewed_by = admin.id
            db.commit()
    finally: db.close()
    return RedirectResponse("/admin/queue", status_code=303)

@router.post("/queue/reject/{host_id}")
def reject(host_id: int, admin=Depends(require_admin)):
    db = SessionLocal()
    try:
        host = db.query(HostSubmission).get(host_id)
        if host:
            host.status = "rejected"
            host.reviewed_by = admin.id
            db.commit()
    finally: db.close()
    return RedirectResponse("/admin/queue", status_code=303)
