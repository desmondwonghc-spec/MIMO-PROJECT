"""
匹配评分服务层
编排 AI 匹配评分流程
"""
import logging
from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId, errors as bson_errors

from database import get_collection
from app.ai.deepseek_client import chat_json
from app.ai.prompts.job_matching import SYSTEM_PROMPT, build_user_prompt
from app.ai.parsers.matching_parser import parse_match_result

logger = logging.getLogger(__name__)


def _oid(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except (bson_errors.InvalidId, Exception):
        raise ValueError(f"无效的ID: {id_str}")


async def match_single(job_id: str, resume_id: str) -> dict:
    """
    单个简历与岗位匹配评分
    """
    jobs_col = get_collection("jobs")
    resumes_col = get_collection("resumes")
    matches_col = get_collection("match_results")

    # 获取岗位
    job = await jobs_col.find_one({"_id": _oid(job_id)})
    if not job:
        raise ValueError(f"岗位不存在: {job_id}")

    # 获取简历
    resume = await resumes_col.find_one({"_id": _oid(resume_id)})
    if not resume:
        raise ValueError(f"简历不存在: {resume_id}")

    if not resume.get("structured_data"):
        raise ValueError(f"简历尚未解析完成，无法匹配")

    # 检查是否已有匹配结果
    existing = await matches_col.find_one({
        "job_id": job_id,
        "resume_id": resume_id,
    })
    if existing:
        # 删除旧结果，重新匹配
        await matches_col.delete_one({"_id": existing["_id"]})

    # 构建输入数据
    job_data = _extract_job_data(job)
    resume_data = resume["structured_data"]
    resume_name = resume_data.get("name", "") or resume.get("original_filename", "未知")

    # 调用 AI 评分
    user_prompt = build_user_prompt(job_data, resume_data)
    ai_response = await chat_json(SYSTEM_PROMPT, user_prompt)

    # 解析并存储结果
    result_doc = parse_match_result(
        ai_response=ai_response,
        job_id=job_id,
        resume_id=resume_id,
        resume_name=resume_name,
        model="deepseek-chat",
    )

    await matches_col.insert_one(result_doc)
    result_doc["id"] = str(result_doc.pop("_id"))
    logger.info(f"匹配完成: job={job_id} resume={resume_id} score={result_doc['overall_score']}")
    return result_doc


async def match_batch(job_id: str, resume_ids: list) -> list:
    """
    批量匹配：一个岗位 vs 多份简历
    """
    results = []
    for resume_id in resume_ids:
        try:
            result = await match_single(job_id, resume_id)
            results.append(result)
        except Exception as e:
            logger.error(f"批量匹配失败 job={job_id} resume={resume_id}: {e}")
            results.append({
                "resume_id": resume_id,
                "error": str(e),
                "overall_score": 0,
            })
    return results


async def get_match_results(
    job_id: str,
    min_score: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """获取岗位的匹配结果列表，按分数排序"""
    collection = get_collection("match_results")

    query = {"job_id": job_id}
    if min_score is not None:
        query["overall_score"] = {"$gte": min_score}

    total = await collection.count_documents(query)
    skip = (page - 1) * page_size
    cursor = collection.find(query).sort("overall_score", -1).skip(skip).limit(page_size)
    docs = await cursor.to_list(length=page_size)

    for doc in docs:
        doc["id"] = str(doc.pop("_id"))

    return {
        "items": docs,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0,
    }


async def get_match_result(match_id: str) -> Optional[dict]:
    """获取单个匹配结果"""
    collection = get_collection("match_results")
    doc = await collection.find_one({"_id": _oid(match_id)})
    if doc:
        doc["id"] = str(doc.pop("_id"))
    return doc


async def delete_match_result(match_id: str) -> bool:
    """删除匹配结果"""
    collection = get_collection("match_results")
    result = await collection.delete_one({"_id": _oid(match_id)})
    return result.deleted_count > 0


def _extract_job_data(job: dict) -> dict:
    """从岗位文档中提取用于匹配的数据"""
    salary_range = job.get("salary_range")
    return {
        "title": job.get("title", ""),
        "department": job.get("department", ""),
        "location": job.get("location", ""),
        "description": job.get("description", ""),
        "responsibilities": job.get("responsibilities", []),
        "requirements": job.get("requirements", {}),
        "salary_range": {
            "min": salary_range.get("min", 0) if salary_range else 0,
            "max": salary_range.get("max", 0) if salary_range else 0,
            "currency": salary_range.get("currency", "CNY") if salary_range else "CNY",
        },
    }
