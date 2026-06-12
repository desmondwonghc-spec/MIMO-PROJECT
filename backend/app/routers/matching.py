"""
匹配评分 API 路由（桩）
TODO: 第3周实现完整功能
"""
from fastapi import APIRouter

router = APIRouter()


@router.post("/single")
async def match_single():
    """单个简历匹配"""
    return {"message": "TODO: 第3周实现"}


@router.post("/batch")
async def match_batch():
    """批量匹配"""
    return {"message": "TODO: 第3周实现"}


@router.get("/results/{job_id}")
async def get_match_results(job_id: str):
    """获取岗位的匹配结果列表"""
    return {"items": [], "total": 0}
