import os
from app.db import SessionLocal, User
from app.auth import hash_password

def ensure_admin():
    email = os.environ.get("ADMIN_EMAIL", "").strip().lower()
    pw = os.environ.get("ADMIN_PASSWORD", "")
    if not email or not pw: return
    db = SessionLocal()
    try:
        if not db.query(User).filter_by(email=email).first():
            db.add(User(email=email, password_hash=hash_password(pw), role="admin", is_verified=True))
            db.commit()
    finally: db.close()
