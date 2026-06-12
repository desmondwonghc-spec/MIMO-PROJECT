"""
通用 Pydantic 模型（分页、时间戳等）
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Generic, List, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class TimestampMixin(BaseModel):
    """时间戳混入"""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PaginationParams(BaseModel):
    """分页请求参数"""
    page: int = Field(default=1, ge=1, description="页码（从1开始）")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应"""
    items: List[T] = Field(description="数据列表")
    total: int = Field(description="总数量")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页数量")
    total_pages: int = Field(description="总页数")


class ErrorResponse(BaseModel):
    """错误响应"""
    detail: str = Field(description="错误描述")
    error_code: str = Field(description="错误代码")


def paginate(items: list, total: int, page: int, page_size: int) -> dict:
    """构建分页响应数据"""
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0,
    }
