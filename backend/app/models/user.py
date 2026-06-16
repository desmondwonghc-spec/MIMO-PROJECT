"""
用户相关 Pydantic 模型
"""
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class UserCreate(BaseModel):
    """注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    role: UserRole = Field(default=UserRole.USER, description="角色")


class UserLogin(BaseModel):
    """登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserResponse(BaseModel):
    """用户信息响应"""
    id: str
    username: str
    role: UserRole
    created_at: datetime


class TokenResponse(BaseModel):
    """登录成功响应"""
    access_token: str = Field(description="JWT Token")
    token_type: str = Field(default="bearer")
    user: UserResponse
