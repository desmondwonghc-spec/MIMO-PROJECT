"""
认证 API 路由
"""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.services import auth_service
from app.models.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.utils.exceptions import ValidationError

router = APIRouter()
security = HTTPBearer(auto_error=False)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    依赖注入：从请求头获取并验证当前用户
    用法：user = Depends(get_current_user)
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录，请先登录",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = auth_service.decode_token(credentials.credentials)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await auth_service.get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
        )

    return user


@router.post("/register", response_model=TokenResponse)
async def register(req: UserCreate):
    """注册新用户"""
    try:
        result = await auth_service.register(req.username, req.password, req.role.value)
    except ValueError as e:
        raise ValidationError(str(e))
    return result


@router.post("/login", response_model=TokenResponse)
async def login(req: UserLogin):
    """用户登录"""
    try:
        result = await auth_service.login(req.username, req.password)
    except ValueError as e:
        raise ValidationError(str(e))
    return result


@router.get("/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    return user


@router.get("/users")
async def list_users(user: dict = Depends(get_current_user)):
    """列出所有用户（仅管理员）"""
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可查看用户列表")

    from database import get_collection
    cursor = get_collection("users").find({}).sort("created_at", -1)
    docs = await cursor.to_list(length=100)

    users = []
    for doc in docs:
        users.append({
            "id": str(doc["_id"]),
            "username": doc["username"],
            "role": doc.get("role", "user"),
            "created_at": doc.get("created_at"),
        })

    return {"items": users, "total": len(users)}
