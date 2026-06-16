"""
预面试 API 路由
"""
from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Query, Depends
from fastapi.responses import Response

from app.services import interview_service
from app.models.interview import (
    InterviewStartRequest, InterviewAnswerRequest,
    InterviewSessionResponse,
)
from app.utils.exceptions import NotFoundError, ValidationError
from app.utils.auth_deps import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("/start", response_model=InterviewSessionResponse)
async def start_interview(req: InterviewStartRequest):
    try:
        session = await interview_service.start_session(req.job_id, req.resume_id)
    except ValueError as e:
        raise ValidationError(str(e))
    return session


@router.post("/{session_id}/answer")
async def submit_answer(session_id: str, req: InterviewAnswerRequest):
    try:
        result = await interview_service.submit_answer(session_id, req.answer_text)
    except ValueError as e:
        raise ValidationError(str(e))
    return result


@router.post("/{session_id}/complete", response_model=InterviewSessionResponse)
async def complete_interview(session_id: str):
    try:
        session = await interview_service.complete_session(session_id)
    except ValueError as e:
        raise ValidationError(str(e))
    return session


@router.get("/{session_id}", response_model=InterviewSessionResponse)
async def get_session(session_id: str):
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
    sessions = await interview_service.list_sessions(
        job_id=job_id, resume_id=resume_id, status=status,
    )
    return {"items": sessions, "total": len(sessions)}


@router.get("/{session_id}/export")
async def export_questions_pdf(session_id: str):
    from bson import ObjectId, errors as bson_errors
    from database import get_collection
    from app.file_handlers.pdf_export import generate_interview_pdf

    try:
        oid = ObjectId(session_id)
    except (bson_errors.InvalidId, Exception):
        raise ValidationError(f"无效的会话ID: {session_id}")

    session = await get_collection("interview_sessions").find_one({"_id": oid})
    if not session:
        raise NotFoundError("面试会话", session_id)

    session["id"] = str(session.pop("_id"))
    pdf_bytes = generate_interview_pdf(session)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="interview_{session_id[:8]}.pdf"'
        },
    )
