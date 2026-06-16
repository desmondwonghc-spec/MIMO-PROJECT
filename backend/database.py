"""
MongoDB 数据库连接管理
使用 Motor 异步驱动
"""
from __future__ import annotations
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from config import settings

# 全局客户端和数据库实例
_client: AsyncIOMotorClient | None = None
_database: AsyncIOMotorDatabase | None = None


async def connect_db() -> None:
    """连接 MongoDB，创建必要的索引"""
    global _client, _database
    _client = AsyncIOMotorClient(settings.mongodb_url)
    _database = _client[settings.mongodb_db_name]

    # 创建索引
    await _create_indexes()


async def close_db() -> None:
    """关闭 MongoDB 连接"""
    global _client, _database
    if _client:
        _client.close()
        _client = None
        _database = None


def get_db() -> AsyncIOMotorDatabase:
    """获取数据库实例"""
    if _database is None:
        raise RuntimeError("数据库未连接，请先调用 connect_db()")
    return _database


def get_collection(name: str):
    """获取指定集合"""
    return get_db()[name]


async def _create_indexes() -> None:
    """创建所有集合的索引"""
    db = get_db()

    # jobs 集合索引
    await db.jobs.create_index([("status", 1), ("created_at", -1)])

    # resumes 集合索引
    await db.resumes.create_index([("parsing_status", 1)])
    await db.resumes.create_index([("structured_data.name", 1)])
    await db.resumes.create_index([("created_at", -1)])

    # match_results 集合索引
    await db.match_results.create_index([("job_id", 1), ("overall_score", -1)])
    await db.match_results.create_index(
        [("job_id", 1), ("resume_id", 1)], unique=True
    )

    # interview_sessions 集合索引
    await db.interview_sessions.create_index([("job_id", 1), ("resume_id", 1)])
    await db.interview_sessions.create_index([("status", 1)])

    # candidates 集合索引
    await db.candidates.create_index([("job_id", 1), ("status", 1)])
    await db.candidates.create_index([("resume_id", 1)])

    # app_settings 集合索引
    await db.app_settings.create_index([("key", 1)], unique=True)

    # users 集合索引
    await db.users.create_index([("username", 1)], unique=True)
    await db.users.create_index([("role", 1)])
