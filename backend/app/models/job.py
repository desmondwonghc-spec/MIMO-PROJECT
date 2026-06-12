"""
岗位相关 Pydantic 模型
"""
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class EmploymentType(str, Enum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"


class JobStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"


class EducationLevel(str, Enum):
    HIGH_SCHOOL = "high-school"
    ASSOCIATE = "associate"
    BACHELOR = "bachelor"
    MASTER = "master"
    PHD = "phd"


class SalaryRange(BaseModel):
    min: float = Field(description="最低月薪（元）")
    max: float = Field(description="最高月薪（元）")
    currency: str = Field(default="CNY", description="货币")


class MarketSalary(BaseModel):
    average: float = Field(description="市场平均月薪")
    p25: float = Field(description="25分位月薪")
    p75: float = Field(description="75分位月薪")
    research_date: datetime = Field(description="调研日期")
    source_summary: str = Field(default="", description="数据来源说明")


class JobRequirements(BaseModel):
    education: Optional[EducationLevel] = Field(default=None, description="学历要求")
    min_experience_years: int = Field(default=0, ge=0, description="最低工作年限")
    required_skills: list = Field(default_factory=list, description="必备技能")
    preferred_skills: list = Field(default_factory=list, description="加分技能")
    languages: list = Field(default_factory=list, description="语言要求")
    other: str = Field(default="", description="其他要求")


class JobCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="岗位名称")
    department: str = Field(default="", description="所属部门")
    location: str = Field(..., min_length=1, description="工作地点")
    employment_type: EmploymentType = Field(default=EmploymentType.FULL_TIME)
    description: str = Field(..., min_length=1, description="岗位描述")
    responsibilities: list = Field(default_factory=list, description="岗位职责")
    requirements: JobRequirements = Field(default_factory=JobRequirements)
    salary_range: Optional[SalaryRange] = Field(default=None, description="薪资范围")
    status: JobStatus = Field(default=JobStatus.ACTIVE)
    tags: list = Field(default_factory=list, description="标签")


class JobUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=200)
    department: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[EmploymentType] = None
    description: Optional[str] = None
    responsibilities: Optional[list] = None
    requirements: Optional[JobRequirements] = None
    salary_range: Optional[SalaryRange] = None
    status: Optional[JobStatus] = None
    tags: Optional[list] = None


class JobResponse(BaseModel):
    id: str = Field(description="岗位ID")
    title: str
    department: str
    location: str
    employment_type: EmploymentType
    description: str
    responsibilities: list
    requirements: JobRequirements
    salary_range: Optional[SalaryRange] = None
    market_salary: Optional[MarketSalary] = None
    status: JobStatus
    tags: list
    application_count: int = Field(default=0, description="投递数量")
    created_at: datetime
    updated_at: datetime


class JobListResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int
