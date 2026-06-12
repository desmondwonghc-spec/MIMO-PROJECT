"""
薪资分析服务层
市场薪资调研 + 候选人薪资预估
"""
import logging
from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId, errors as bson_errors

from database import get_collection
from app.ai.deepseek_client import chat_json
from app.ai.prompts.salary_research import (
    MARKET_RESEARCH_SYSTEM_PROMPT, SALARY_ESTIMATE_SYSTEM_PROMPT,
    build_market_research_prompt, build_salary_estimate_prompt,
)

logger = logging.getLogger(__name__)


def _oid(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except (bson_errors.InvalidId, Exception):
        raise ValueError(f"无效的ID: {id_str}")


async def research_market_salary(
    job_id: Optional[str] = None,
    title: Optional[str] = None,
    location: Optional[str] = None,
    experience_years: Optional[int] = None,
    skills: Optional[list] = None,
) -> dict:
    """
    市场薪资调研
    可通过 job_id 使用已有岗位数据，或手动传入参数
    """
    # 如果传了 job_id，从数据库获取岗位信息
    if job_id:
        job = await get_collection("jobs").find_one({"_id": _oid(job_id)})
        if not job:
            raise ValueError(f"岗位不存在: {job_id}")
        title = title or job.get("title", "")
        location = location or job.get("location", "")
        req = job.get("requirements", {})
        experience_years = experience_years or req.get("min_experience_years", 0)
        skills = skills or req.get("required_skills", [])

    if not title:
        raise ValueError("请提供岗位名称")
    if not location:
        raise ValueError("请提供工作地点")

    # 调用 AI 调研
    user_prompt = build_market_research_prompt(
        title=title,
        location=location,
        experience_years=experience_years or 0,
        skills=skills or [],
    )
    ai_response = await chat_json(MARKET_RESEARCH_SYSTEM_PROMPT, user_prompt)

    now = datetime.now(timezone.utc)
    result = {
        "job_id": job_id,
        "title": title,
        "location": location,
        "average": float(ai_response.get("average", 0)),
        "p25": float(ai_response.get("p25", 0)),
        "p75": float(ai_response.get("p75", 0)),
        "source_summary": str(ai_response.get("source_summary", "")),
        "research_date": now.strftime("%Y-%m-%d"),
    }

    # 如果关联了岗位，将市场薪资写入岗位记录
    if job_id:
        await get_collection("jobs").update_one(
            {"_id": _oid(job_id)},
            {"$set": {
                "market_salary": {
                    "average": result["average"],
                    "p25": result["p25"],
                    "p75": result["p75"],
                    "research_date": now,
                    "source_summary": result["source_summary"],
                },
                "updated_at": now,
            }}
        )
        logger.info(f"市场薪资已写入岗位 {job_id}: avg={result['average']}")

    return result


async def estimate_candidate_salary(job_id: str, resume_id: str) -> dict:
    """
    候选人薪资预估
    综合市场数据 + 简历质量 + 匹配度
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
        raise ValueError("简历尚未解析完成")

    resume_data = resume["structured_data"]
    resume_name = resume_data.get("name", "") or resume.get("original_filename", "未知")

    # 获取匹配分数
    match = await matches_col.find_one({"job_id": job_id, "resume_id": resume_id})
    match_score = match.get("overall_score", 60) if match else 60

    # 获取市场薪资数据
    market = job.get("market_salary")
    if not market:
        # 自动调研
        market_result = await research_market_salary(job_id=job_id)
        market = {
            "average": market_result["average"],
            "p25": market_result["p25"],
            "p75": market_result["p75"],
        }

    # 构建输入
    job_data = {
        "title": job.get("title", ""),
        "location": job.get("location", ""),
        "salary_range": job.get("salary_range"),
        "requirements": job.get("requirements", {}),
    }

    # 调用 AI 预估
    user_prompt = build_salary_estimate_prompt(
        job_data=job_data,
        resume_data=resume_data,
        match_score=match_score,
        market_salary=market,
    )
    ai_response = await chat_json(SALARY_ESTIMATE_SYSTEM_PROMPT, user_prompt)

    result = {
        "job_id": job_id,
        "resume_id": resume_id,
        "candidate_name": ai_response.get("candidate_name", resume_name),
        "match_score": ai_response.get("match_score", match_score),
        "market_average": float(ai_response.get("market_average", market.get("average", 0))),
        "recommended_min": float(ai_response.get("recommended_min", 0)),
        "recommended_max": float(ai_response.get("recommended_max", 0)),
        "reasoning": str(ai_response.get("reasoning", "")),
    }

    logger.info(f"薪资预估完成: {resume_name} → {result['recommended_min']}-{result['recommended_max']}")
    return result
