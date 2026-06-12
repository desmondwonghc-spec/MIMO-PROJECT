"""
薪资分析相关 Pydantic 模型
"""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class SalaryResearchRequest(BaseModel):
    job_id: Optional[str] = Field(default=None, description="岗位ID")
    title: Optional[str] = Field(default=None, description="岗位名称")
    location: Optional[str] = Field(default=None, description="工作地点")
    experience_years: Optional[int] = Field(default=None, description="经验要求")
    skills: Optional[list] = Field(default=None, description="关键技能")


class SalaryEstimateRequest(BaseModel):
    job_id: str = Field(description="岗位ID")
    resume_id: str = Field(description="简历ID")


class SalaryResearchResponse(BaseModel):
    job_id: Optional[str] = None
    title: str = Field(description="岗位名称")
    location: str = Field(description="工作地点")
    average: float = Field(description="市场平均月薪（元）")
    p25: float = Field(description="25分位月薪")
    p75: float = Field(description="75分位月薪")
    source_summary: str = Field(description="数据来源说明")
    research_date: str = Field(description="调研日期")


class SalaryEstimateResponse(BaseModel):
    job_id: str
    resume_id: str
    candidate_name: str = Field(description="候选人姓名")
    match_score: int = Field(description="匹配分数")
    market_average: float = Field(description="市场平均薪资")
    recommended_min: float = Field(description="建议最低薪资")
    recommended_max: float = Field(description="建议最高薪资")
    reasoning: str = Field(description="预估理由")
