"""
薪资分析 API 路由
"""
from __future__ import annotations
from fastapi import APIRouter

from app.services import salary_service
from app.models.salary import (
    SalaryResearchRequest, SalaryEstimateRequest,
    SalaryResearchResponse, SalaryEstimateResponse,
)
from app.utils.exceptions import ValidationError

router = APIRouter()


@router.post("/research", response_model=SalaryResearchResponse)
async def research_salary(req: SalaryResearchRequest):
    """市场薪资调研"""
    if not req.job_id and not req.title:
        raise ValidationError("请提供岗位ID或岗位名称")
    if not req.job_id and not req.location:
        raise ValidationError("请提供工作地点（手动输入时必填）")

    try:
        result = await salary_service.research_market_salary(
            job_id=req.job_id,
            title=req.title,
            location=req.location,
            experience_years=req.experience_years,
            skills=req.skills,
        )
    except ValueError as e:
        raise ValidationError(str(e))

    return result


@router.post("/estimate", response_model=SalaryEstimateResponse)
async def estimate_salary(req: SalaryEstimateRequest):
    """候选人薪资预估"""
    try:
        result = await salary_service.estimate_candidate_salary(
            job_id=req.job_id,
            resume_id=req.resume_id,
        )
    except ValueError as e:
        raise ValidationError(str(e))

    return result
