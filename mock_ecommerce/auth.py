"""JWT Authentication module."""
import os, jwt
from datetime import datetime, timedelta
from fastapi import Header, Depends, HTTPException
from models import _store

JWT_SECRET = os.environ.get("JWT_SECRET", "ecommerce-secret-key-2026-prod")
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 8

def create_token(user: dict) -> str:
    return jwt.encode({
        "sub": user["id"], "role": user["role"], "name": user["name"],
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    }, JWT_SECRET, algorithm=JWT_ALGORITHM)

def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        payload = jwt.decode(authorization[7:], JWT_SECRET, algorithms=[JWT_ALGORITHM])
        u = next((x for x in _store["users"] if x["id"] == payload["sub"]), None)
        return u
    except Exception:
        return None

def require_auth(user = Depends(get_current_user)):
    if not user: raise HTTPException(401, "请先登录")
    return user

def require_admin(user = Depends(get_current_user)):
    if not user: raise HTTPException(401, "请先登录")
    if user["role"] != "admin": raise HTTPException(403, "仅管理员可操作")
    return user

def require_operator(user = Depends(get_current_user)):
    if not user: raise HTTPException(401, "请先登录")
    if user["role"] not in ("admin", "operator"): raise HTTPException(403, "无操作权限")
    return user
