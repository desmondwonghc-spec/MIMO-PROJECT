"""
认证服务层
用户注册、登录、JWT Token 管理
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from bson import ObjectId, errors as bson_errors
import bcrypt
import jwt

from database import get_collection
from config import settings

logger = logging.getLogger(__name__)

# JWT 配置
JWT_SECRET = "hr-screening-system-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 72  # Token 有效期 72 小时


def _hash_password(password: str) -> str:
    """密码加密"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(password: str, hashed: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def _create_token(user_id: str, username: str, role: str) -> str:
    """创建 JWT Token"""
    payload = {
        "sub": user_id,
        "username": username,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """解析 JWT Token"""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token 已过期，请重新登录")
    except jwt.InvalidTokenError:
        raise ValueError("无效的 Token")


async def register(username: str, password: str, role: str = "user") -> dict:
    """注册新用户"""
    users_col = get_collection("users")

    # 检查用户名是否已存在
    existing = await users_col.find_one({"username": username})
    if existing:
        raise ValueError("用户名已存在")

    now = datetime.now(timezone.utc)
    doc = {
        "username": username,
        "password_hash": _hash_password(password),
        "role": role,
        "created_at": now,
        "updated_at": now,
    }

    result = await users_col.insert_one(doc)
    user_id = str(result.inserted_id)

    # 创建 Token
    token = _create_token(user_id, username, role)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "username": username,
            "role": role,
            "created_at": now,
        },
    }


async def login(username: str, password: str) -> dict:
    """用户登录"""
    users_col = get_collection("users")

    user = await users_col.find_one({"username": username})
    if not user:
        raise ValueError("用户名或密码错误")

    if not _verify_password(password, user["password_hash"]):
        raise ValueError("用户名或密码错误")

    user_id = str(user["_id"])
    role = user.get("role", "user")

    # 创建 Token
    token = _create_token(user_id, username, role)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "username": username,
            "role": role,
            "created_at": user.get("created_at", datetime.now(timezone.utc)),
        },
    }


async def get_user_by_id(user_id: str) -> Optional[dict]:
    """根据ID获取用户"""
    try:
        user = await get_collection("users").find_one({"_id": ObjectId(user_id)})
        if user:
            return {
                "id": str(user["_id"]),
                "username": user["username"],
                "role": user.get("role", "user"),
                "created_at": user.get("created_at"),
            }
    except Exception:
        pass
    return None


async def ensure_admin_exists():
    """确保至少有一个管理员账号"""
    users_col = get_collection("users")
    admin = await users_col.find_one({"role": "admin"})
    if not admin:
        await register("admin", "admin123", "admin")
        logger.info("已创建默认管理员账号: admin / admin123")
