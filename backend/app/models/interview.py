"""
预面试会话相关 Pydantic 模型
"""
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class InterviewStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class QuestionCategory(str, Enum):
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SITUATIONAL = "situational"
    GAP_FOLLOWUP = "gap_followup"


class QuestionDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class InterviewRecommendation(str, Enum):
    STRONGLY_RECOMMEND = "strongly_recommend"
    RECOMMEND_INTERVIEW = "recommend_interview"
    NEEDS_FURTHER_EVALUATION = "needs_further_evaluation"
    NOT_RECOMMENDED = "not_recommended"


class InterviewQuestion(BaseModel):
    question_id: str = Field(description="问题ID")
    category: QuestionCategory
    question: str = Field(description="问题内容")
    rationale: str = Field(default="", description="出题理由")
    difficulty: QuestionDifficulty = Field(default=QuestionDifficulty.MEDIUM)


class ConversationTurn(BaseModel):
    role: str = Field(description="角色: ai/candidate")
    content: str = Field(description="内容")
    question_id: str = Field(default="", description="关联问题ID")
    timestamp: datetime = Field(default_factory=lambda: datetime.utcnow())


class QuestionEvaluation(BaseModel):
    question_id: str
    score: int = Field(ge=1, le=10, description="分数 1-10")
    feedback: str = Field(default="", description="反馈")
    strengths: list = Field(default_factory=list)
    areas_to_probe: list = Field(default_factory=list)


class OverallEvaluation(BaseModel):
    total_score: int = Field(ge=0, le=100)
    technical_score: int = Field(ge=0, le=100)
    communication_score: int = Field(ge=0, le=100)
    cultural_fit_score: int = Field(ge=0, le=100)
    summary: str = Field(default="")
    recommendation: InterviewRecommendation
    key_concerns: list = Field(default_factory=list)
    highlights: list = Field(default_factory=list)


class InterviewStartRequest(BaseModel):
    job_id: str
    resume_id: str


class InterviewAnswerRequest(BaseModel):
    answer_text: str = Field(min_length=1, description="候选人的回答")


class InterviewSessionResponse(BaseModel):
    id: str
    job_id: str
    resume_id: str
    status: InterviewStatus
    questions: list = Field(default_factory=list)
    conversation: list = Field(default_factory=list)
    evaluations: list = Field(default_factory=list)
    overall_evaluation: Optional[OverallEvaluation] = None
    created_at: datetime
    updated_at: datetime
