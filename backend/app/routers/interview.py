"""
预面试 API 路由（桩）
TODO: 第4周实现完整功能
"""
from fastapi import APIRouter

router = APIRouter()


@router.post("/start")
async def start_interview():
    """启动预面试会话"""
    return {"message": "TODO: 第4周实现"}


@router.post("/{session_id}/answer")
async def submit_answer(session_id: str):
    """提交面试回答"""
    return {"message": "TODO: 第4周实现"}


@router.get("/{session_id}")
async def get_session(session_id: str):
    """获取面试会话详情"""
    return {"message": "TODO: 第4周实现"}
