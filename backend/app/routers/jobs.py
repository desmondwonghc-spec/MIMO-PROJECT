"""
岗位管理 API 路由
"""
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Query
from bson import ObjectId

from database import get_collection
from app.models.job import (
    JobCreate, JobUpdate, JobResponse, JobListResponse,
    JobStatus, JobRequirements, SalaryRange, MarketSalary,
)
from app.models.common import paginate
from app.utils.exceptions import NotFoundError, ValidationError

router = APIRouter()


def _doc_to_response(doc: dict) -> dict:
    """将 MongoDB 文档转换为响应格式"""
    doc["id"] = str(doc.pop("_id"))
    # 确保嵌套对象存在
    if "requirements" in doc and isinstance(doc["requirements"], dict):
        doc["requirements"] = JobRequirements(**doc["requirements"])
    if "salary_range" in doc and isinstance(doc["salary_range"], dict):
        doc["salary_range"] = SalaryRange(**doc["salary_range"])
    if "market_salary" in doc and isinstance(doc["market_salary"], dict):
        doc["market_salary"] = MarketSalary(**doc["market_salary"])
    return doc


@router.get("", response_model=JobListResponse)
async def list_jobs(
    status: Optional[str] = Query(default=None, description="状态筛选"),
    search: Optional[str] = Query(default=None, description="搜索关键词"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    sort_by: str = Query(default="created_at", description="排序字段"),
):
    """获取岗位列表"""
    collection = get_collection("jobs")

    # 构建查询条件
    query = {}
    if status:
        query["status"] = status
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"department": {"$regex": search, "$options": "i"}},
        ]

    # 查询总数
    total = await collection.count_documents(query)

    # 分页查询
    sort_direction = -1 if sort_by.startswith("-") else 1
    sort_field = sort_by.lstrip("-")
    skip = (page - 1) * page_size
    cursor = collection.find(query).sort(sort_field, sort_direction).skip(skip).limit(page_size)
    docs = await cursor.to_list(length=page_size)

    items = [_doc_to_response(doc) for doc in docs]
    return paginate(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=JobResponse, status_code=201)
async def create_job(job: JobCreate):
    """创建新岗位"""
    collection = get_collection("jobs")

    now = datetime.now(timezone.utc)
    doc = job.model_dump()
    doc.update({
        "created_at": now,
        "updated_at": now,
        "application_count": 0,
    })

    # 处理枚举值
    doc["employment_type"] = doc["employment_type"].value if hasattr(doc["employment_type"], "value") else doc["employment_type"]
    doc["status"] = doc["status"].value if hasattr(doc["status"], "value") else doc["status"]
    if doc.get("requirements"):
        req = doc["requirements"]
        if hasattr(req, "education") and req.get("education") and hasattr(req["education"], "value"):
            req["education"] = req["education"].value

    result = await collection.insert_one(doc)
    doc["_id"] = result.inserted_id

    return _doc_to_response(doc)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    """获取单个岗位详情"""
    collection = get_collection("jobs")
    doc = await collection.find_one({"_id": ObjectId(job_id)})
    if not doc:
        raise NotFoundError("岗位", job_id)
    return _doc_to_response(doc)


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(job_id: str, job: JobUpdate):
    """更新岗位"""
    collection = get_collection("jobs")

    # 检查是否存在
    existing = await collection.find_one({"_id": ObjectId(job_id)})
    if not existing:
        raise NotFoundError("岗位", job_id)

    # 只更新非空字段
    update_data = job.model_dump(exclude_unset=True, exclude_none=True)
    if not update_data:
        raise ValidationError("没有要更新的字段")

    update_data["updated_at"] = datetime.now(timezone.utc)

    # 处理枚举
    for key in ["employment_type", "status"]:
        if key in update_data and hasattr(update_data[key], "value"):
            update_data[key] = update_data[key].value

    await collection.update_one(
        {"_id": ObjectId(job_id)},
        {"$set": update_data}
    )

    doc = await collection.find_one({"_id": ObjectId(job_id)})
    return _doc_to_response(doc)


@router.delete("/{job_id}", status_code=204)
async def delete_job(job_id: str):
    """删除岗位"""
    collection = get_collection("jobs")
    result = await collection.delete_one({"_id": ObjectId(job_id)})
    if result.deleted_count == 0:
        raise NotFoundError("岗位", job_id)
