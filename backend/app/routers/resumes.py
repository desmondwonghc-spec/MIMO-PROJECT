"""
简历管理 API 路由（桩）
TODO: 第2周实现完整功能
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def list_resumes():
    """获取简历列表"""
    return {"items": [], "total": 0, "page": 1, "page_size": 20, "total_pages": 0}


@router.post("/upload")
async def upload_resume():
    """上传简历文件"""
    return {"message": "TODO: 第2周实现"}


@router.get("/{resume_id}")
async def get_resume(resume_id: str):
    """获取简历详情"""
    return {"message": "TODO: 第2周实现"}
