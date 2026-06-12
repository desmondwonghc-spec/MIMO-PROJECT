"""
预面试 API 路由
"""
from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Query

from app.services import interview_service
from app.models.interview import (
    InterviewStartRequest, InterviewAnswerRequest,
    InterviewSessionResponse,
)
from app.utils.exceptions import NotFoundError, ValidationError

router = APIRouter()


@router.post("/start", response_model=InterviewSessionResponse)
async def start_interview(req: InterviewStartRequest):
    """启动预面试会话（AI生成问题）"""
    try:
        session = await interview_service.start_session(req.job_id, req.resume_id)
    except ValueError as e:
        raise ValidationError(str(e))
    return session


@router.post("/{session_id}/answer")
async def submit_answer(session_id: str, req: InterviewAnswerRequest):
    """提交面试回答（AI评估 + 返回下一题）"""
    try:
        result = await interview_service.submit_answer(session_id, req.answer_text)
    except ValueError as e:
        raise ValidationError(str(e))
    return result


@router.post("/{session_id}/complete", response_model=InterviewSessionResponse)
async def complete_interview(session_id: str):
    """结束面试，生成总评"""
    try:
        session = await interview_service.complete_session(session_id)
    except ValueError as e:
        raise ValidationError(str(e))
    return session


@router.get("/{session_id}", response_model=InterviewSessionResponse)
async def get_session(session_id: str):
    """获取面试会话详情"""
    session = await interview_service.get_session(session_id)
    if not session:
        raise NotFoundError("面试会话", session_id)
    return session


@router.get("")
async def list_sessions(
    job_id: Optional[str] = Query(default=None),
    resume_id: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
):
    """列出面试会话"""
    sessions = await interview_service.list_sessions(
        job_id=job_id,
        resume_id=resume_id,
        status=status,
    )
    return {"items": sessions, "total": len(sessions)}
