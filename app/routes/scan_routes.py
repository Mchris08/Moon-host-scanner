from fastapi import APIRouter, Request, Depends, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.auth import require_user
from app.db import SessionLocal, ScanJob, HostSubmission
from app.scanner import run_bulk_scan
import json

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

# --- NEW: The Scan Trigger ---
@router.post("/scan/run")
async def trigger_scan(request: Request, background_tasks: BackgroundTasks, user=Depends(require_user)):
    db = SessionLocal()
    job = ScanJob(region="zim", status="running")
    db.add(job); db.commit(); db.refresh(job)
    job_id = job.id
    db.close()

    # Run the scanner in the background so the browser doesn't freeze
    background_tasks.add_task(execute_scan, job_id)
    return RedirectResponse("/dashboard", status_code=303)

async def execute_scan(job_id: int):
    # 1. Run the engine
    working_hosts = await run_bulk_scan()
    
    # 2. Save results to DB
    db = SessionLocal()
    try:
        # Update job status
        job = db.query(ScanJob).get(job_id)
        job.status = "done"
        job.summary_json = json.dumps({"found": len(working_hosts)})
        
        # Send hosts to Admin Queue
        for host in working_hosts:
            exists = db.query(HostSubmission).filter_by(host=host["host"], port=host["port"]).first()
            if not exists:
                db.add(HostSubmission(
                    host=host["host"], port=host["port"],
                    score=host["score"], grade=host["grade"],
                    tunnel_ready=host["tunnel_ready"],
                    is_zimbabwe=True, status="pending"
                ))
        db.commit()
    finally:
        db.close()
