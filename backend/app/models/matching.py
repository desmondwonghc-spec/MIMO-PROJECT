"""
匹配结果相关 Pydantic 模型
"""
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class MatchRecommendation(str, Enum):
    STRONG_MATCH = "strong_match"
    GOOD_MATCH = "good_match"
    PARTIAL_MATCH = "partial_match"
    WEAK_MATCH = "weak_match"
    NO_MATCH = "no_match"


class DimensionScore(BaseModel):
    score: int = Field(ge=0, le=100, description="分数 0-100")
    reasoning: str = Field(default="", description="评分理由")


class DimensionScores(BaseModel):
    skills_match: DimensionScore = Field(description="技能匹配")
    experience_match: DimensionScore = Field(description="经验匹配")
    education_match: DimensionScore = Field(description="学历匹配")
    location_match: DimensionScore = Field(description="地点匹配")
    salary_match: DimensionScore = Field(description="薪资匹配")


class MatchSingleRequest(BaseModel):
    job_id: str = Field(description="岗位ID")
    resume_id: str = Field(description="简历ID")


class MatchBatchRequest(BaseModel):
    job_id: str = Field(description="岗位ID")
    resume_ids: list = Field(description="简历ID列表")


class MatchResultResponse(BaseModel):
    id: str = Field(description="匹配结果ID")
    job_id: str
    resume_id: str
    resume_name: str = Field(default="", description="候选人姓名")
    overall_score: int = Field(ge=0, le=100, description="总分")
    dimension_scores: DimensionScores
    strengths: list = Field(default_factory=list, description="优势")
    weaknesses: list = Field(default_factory=list, description="不足")
    recommendation: MatchRecommendation
    summary: str = Field(default="", description="综合评价")
    ai_model: str = Field(default="", description="使用的AI模型")
    created_at: datetime


class MatchResultListResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int
