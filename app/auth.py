import os
from passlib.context import CryptContext
from itsdangerous import URLSafeTimedSerializer
from fastapi import Request, HTTPException
from app.db import SessionLocal, User

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
serializer = URLSafeTimedSerializer(SECRET_KEY, salt="session")

def hash_password(p): return pwd_ctx.hash(p)
def verify_password(p, h): return pwd_ctx.verify(p, h)
def create_session_token(uid): return serializer.dumps({"uid": uid})

def read_session_token(token):
    try: return serializer.loads(token, max_age=60*60*24*7)["uid"]
    except: return None

def current_user(request: Request):
    token = request.cookies.get("session")
    if not token: return None
    uid = read_session_token(token)
    if not uid: return None
    db = SessionLocal()
    try:
        u = db.query(User).get(uid)
        return u if u and u.is_active else None
    finally: db.close()

def require_user(request: Request):
    u = current_user(request)
    if not u: raise HTTPException(status_code=303, headers={"Location": "/login"})
    return u
