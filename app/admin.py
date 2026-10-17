from fastapi import Request, HTTPException
from app.auth import current_user

def require_admin(request: Request):
    u = current_user(request)
    if not u or u.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return u
