"""Auth routes — login, current user."""
from fastapi import APIRouter, Depends, HTTPException
from auth import create_token, require_auth, get_current_user
from models import LoginRequest, _store, verify_pw

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/login")
def login(body: LoginRequest):
    u = next((x for x in _store["users"] if x["username"] == body.username and verify_pw(x["password"], body.password)), None)
    if not u:
        raise HTTPException(401, "用户名或密码错误")
    token = create_token(u)
    return {"token": token, "token_type": "bearer", "user": {"id": u["id"], "username": u["username"], "role": u["role"], "name": u["name"]}}

@router.get("/me")
def me(user = Depends(require_auth)):
    return {"id": user["id"], "username": user["username"], "role": user["role"], "name": user["name"]}
