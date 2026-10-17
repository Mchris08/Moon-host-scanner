from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.db import SessionLocal, User
from app.auth import hash_password, verify_password, create_session_token

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request): return templates.TemplateResponse("signup.html", {"request": request})

@router.post("/signup")
def signup(request: Request, email: str = Form(...), password: str = Form(...)):
    db = SessionLocal()
    try:
        if db.query(User).filter_by(email=email.lower()).first():
            return templates.TemplateResponse("signup.html", {"request": request, "error": "Email exists"})
        u = User(email=email.lower(), password_hash=hash_password(password), is_verified=True)
        db.add(u); db.commit()
        return RedirectResponse("/login", status_code=303)
    finally: db.close()

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request): return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...)):
    db = SessionLocal()
    try: u = db.query(User).filter_by(email=email.lower()).first()
    finally: db.close()
    if not u or not verify_password(password, u.password_hash):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    resp = RedirectResponse("/dashboard", status_code=303)
    resp.set_cookie("session", create_session_token(u.id), httponly=True)
    return resp

@router.post("/logout")
def logout():
    resp = RedirectResponse("/login", status_code=303)
    resp.delete_cookie("session")
    return resp
