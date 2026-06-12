"""
候选人流程追踪相关 Pydantic 模型
"""
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class CandidateStatus(str, Enum):
    APPLIED = "applied"
    SCREENING = "screening"
    INTERVIEW = "interview"
    OFFER = "offer"
    HIRED = "hired"
    REJECTED = "rejected"


class StatusChange(BaseModel):
    from_status: Optional[str] = Field(default=None, alias="from")
    to: str
    changed_at: datetime = Field(default_factory=lambda: datetime.utcnow())
    note: str = Field(default="")

    class Config:
        populate_by_name = True


class PipelineStatusUpdate(BaseModel):
    status: CandidateStatus
    note: str = Field(default="", description="备注")


class CandidateResponse(BaseModel):
    id: str
    job_id: str
    resume_id: str
    match_result_id: Optional[str] = None
    interview_session_id: Optional[str] = None
    name: str = Field(description="候选人姓名")
    status: CandidateStatus
    status_history: List[StatusChange] = Field(default_factory=list)
    notes: str = Field(default="")
    created_at: datetime
    updated_at: datetime


class PipelineColumn(BaseModel):
    status: CandidateStatus
    label: str = Field(description="状态显示名称")
    candidates: List[CandidateResponse] = Field(default_factory=list)
    count: int = Field(default=0)


class PipelineResponse(BaseModel):
    job_id: str
    job_title: str
    columns: List[PipelineColumn]
    total_candidates: int
