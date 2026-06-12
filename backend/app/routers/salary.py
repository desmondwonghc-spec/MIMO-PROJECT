"""
薪资分析 API 路由（桩）
TODO: 第3周实现完整功能
"""
from fastapi import APIRouter

router = APIRouter()


@router.post("/research")
async def research_salary():
    """市场薪资调研"""
    return {"message": "TODO: 第3周实现"}


@router.post("/estimate")
async def estimate_salary():
    """候选人薪资预估"""
    return {"message": "TODO: 第3周实现"}
