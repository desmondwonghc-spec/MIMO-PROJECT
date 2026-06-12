"""
简历相关 Pydantic 模型
"""
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ResumeSource(str, Enum):
    BOSS = "boss"
    UPLOAD = "upload"
    REFERRAL = "referral"
    OTHER = "other"


class ParsingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Education(BaseModel):
    degree: str = Field(default="", description="学位")
    institution: str = Field(default="", description="学校")
    major: str = Field(default="", description="专业")
    start_year: Optional[int] = None
    end_year: Optional[int] = None


class WorkExperience(BaseModel):
    company: str = Field(default="", description="公司")
    title: str = Field(default="", description="职位")
    start_date: str = Field(default="", description="开始时间 (YYYY-MM)")
    end_date: str = Field(default="", description="结束时间 (YYYY-MM 或 'present')")
    duration_months: int = Field(default=0, description="时长（月）")
    highlights: list = Field(default_factory=list, description="工作亮点")


class LanguageProficiency(BaseModel):
    language: str
    level: str = Field(description="水平: native/fluent/intermediate/basic")


class ExpectedSalary(BaseModel):
    amount: float
    currency: str = Field(default="CNY")


class ResumeStructuredData(BaseModel):
    name: str = Field(default="", description="姓名")
    email: str = Field(default="", description="邮箱")
    phone: str = Field(default="", description="电话")
    age: Optional[int] = None
    gender: str = Field(default="", description="性别")
    current_location: str = Field(default="", description="当前所在地")
    summary: str = Field(default="", description="个人简介")
    education: list = Field(default_factory=list)
    work_experience: list = Field(default_factory=list)
    total_experience_years: float = Field(default=0, description="总工作年限")
    skills: list = Field(default_factory=list, description="技能列表")
    certifications: list = Field(default_factory=list, description="证书")
    languages: list = Field(default_factory=list)
    expected_salary: Optional[ExpectedSalary] = None


class ResumeResponse(BaseModel):
    id: str = Field(description="简历ID")
    original_filename: str = Field(description="原始文件名")
    file_type: str = Field(description="文件类型: pdf/docx")
    file_size: int = Field(description="文件大小（字节）")
    source: ResumeSource = Field(default=ResumeSource.UPLOAD)
    structured_data: Optional[ResumeStructuredData] = None
    parsing_status: ParsingStatus
    parsing_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ResumeListResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int
