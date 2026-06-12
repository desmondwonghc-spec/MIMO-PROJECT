"""
预面试服务层
管理面试会话生命周期：启动→提问→回答→评估→总评
"""
import logging
from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId, errors as bson_errors

from database import get_collection
from app.ai.deepseek_client import chat_json
from app.ai.prompts.interview_gen import SYSTEM_PROMPT as GEN_PROMPT, build_question_gen_prompt
from app.ai.prompts.interview_eval import (
    QUESTION_EVAL_SYSTEM_PROMPT, OVERALL_EVAL_SYSTEM_PROMPT,
    build_question_eval_prompt, build_overall_eval_prompt,
)

logger = logging.getLogger(__name__)


def _oid(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except (bson_errors.InvalidId, Exception):
        raise ValueError(f"无效的ID: {id_str}")


async def start_session(job_id: str, resume_id: str) -> dict:
    """
    启动预面试会话：生成面试问题
    """
    jobs_col = get_collection("jobs")
    resumes_col = get_collection("resumes")
    sessions_col = get_collection("interview_sessions")
    matches_col = get_collection("match_results")

    # 获取岗位和简历
    job = await jobs_col.find_one({"_id": _oid(job_id)})
    if not job:
        raise ValueError(f"岗位不存在: {job_id}")

    resume = await resumes_col.find_one({"_id": _oid(resume_id)})
    if not resume:
        raise ValueError(f"简历不存在: {resume_id}")

    if not resume.get("structured_data"):
        raise ValueError("简历尚未解析完成")

    # 获取匹配结果（可选）
    match = await matches_col.find_one({"job_id": job_id, "resume_id": resume_id})
    match_data = None
    if match:
        match_data = {
            "overall_score": match.get("overall_score", 0),
            "strengths": match.get("strengths", []),
            "weaknesses": match.get("weaknesses", []),
        }

    # 构建输入
    job_data = {
        "title": job.get("title", ""),
        "location": job.get("location", ""),
        "description": job.get("description", ""),
        "requirements": job.get("requirements", {}),
        "responsibilities": job.get("responsibilities", []),
    }
    resume_data = resume["structured_data"]

    # AI 生成问题
    user_prompt = build_question_gen_prompt(job_data, resume_data, match_data)
    ai_response = await chat_json(GEN_PROMPT, user_prompt)

    questions = []
    for q in ai_response.get("questions", []):
        questions.append({
            "question_id": q.get("question_id", f"q{len(questions)+1}"),
            "category": q.get("category", "technical"),
            "question": q.get("question", ""),
            "rationale": q.get("rationale", ""),
            "difficulty": q.get("difficulty", "medium"),
        })

    now = datetime.now(timezone.utc)
    doc = {
        "job_id": job_id,
        "resume_id": resume_id,
        "status": "in_progress",
        "questions": questions,
        "conversation": [],
        "evaluations": [],
        "overall_evaluation": None,
        "current_question_index": 0,
        "created_at": now,
        "updated_at": now,
    }

    result = await sessions_col.insert_one(doc)
    session_id = str(result.inserted_id)

    # 自动添加第一条问题到对话
    if questions:
        first_q = questions[0]
        await sessions_col.update_one(
            {"_id": result.inserted_id},
            {"$push": {"conversation": {
                "role": "ai",
                "content": first_q["question"],
                "question_id": first_q["question_id"],
                "timestamp": now,
            }}}
        )

    doc["_id"] = session_id
    logger.info(f"面试会话已启动: {session_id}, {len(questions)}个问题")
    return doc


async def submit_answer(session_id: str, answer_text: str) -> dict:
    """
    提交候选人的回答，AI评估，返回下一个问题
    """
    sessions_col = get_collection("interview_sessions")
    session = await sessions_col.find_one({"_id": _oid(session_id)})
    if not session:
        raise ValueError(f"面试会话不存在: {session_id}")

    if session.get("status") != "in_progress":
        raise ValueError("面试会话已结束")

    questions = session.get("questions", [])
    current_idx = session.get("current_question_index", 0)

    if current_idx >= len(questions):
        raise ValueError("所有问题已回答完毕")

    current_q = questions[current_idx]
    now = datetime.now(timezone.utc)

    # 添加候选人回答到对话
    await sessions_col.update_one(
        {"_id": _oid(session_id)},
        {"$push": {"conversation": {
            "role": "candidate",
            "content": answer_text,
            "question_id": current_q["question_id"],
            "timestamp": now,
        }}}
    )

    # AI 评估该回答
    eval_prompt = build_question_eval_prompt(
        question=current_q["question"],
        answer=answer_text,
    )
    eval_response = await chat_json(QUESTION_EVAL_SYSTEM_PROMPT, eval_prompt)

    evaluation = {
        "question_id": current_q["question_id"],
        "score": max(1, min(10, int(eval_response.get("score", 5)))),
        "feedback": str(eval_response.get("feedback", "")),
        "strengths": [str(s) for s in eval_response.get("strengths", [])],
        "areas_to_probe": [str(a) for a in eval_response.get("areas_to_probe", [])],
    }

    await sessions_col.update_one(
        {"_id": _oid(session_id)},
        {"$push": {"evaluations": evaluation}}
    )

    # 移到下一个问题
    next_idx = current_idx + 1
    next_question = None

    if next_idx < len(questions):
        next_q = questions[next_idx]
        next_question = next_q
        await sessions_col.update_one(
            {"_id": _oid(session_id)},
            {
                "$set": {"current_question_index": next_idx, "updated_at": now},
                "$push": {"conversation": {
                    "role": "ai",
                    "content": next_q["question"],
                    "question_id": next_q["question_id"],
                    "timestamp": now,
                }},
            }
        )

    # 获取更新后的会话
    updated = await sessions_col.find_one({"_id": _oid(session_id)})

    return {
        "evaluation": evaluation,
        "next_question": next_question,
        "is_last": next_idx >= len(questions),
        "progress": f"{next_idx}/{len(questions)}",
        "session": _format_session(updated),
    }


async def complete_session(session_id: str) -> dict:
    """
    结束面试，生成总评
    """
    sessions_col = get_collection("interview_sessions")
    session = await sessions_col.find_one({"_id": _oid(session_id)})
    if not session:
        raise ValueError(f"面试会话不存在: {session_id}")

    conversation = session.get("conversation", [])
    evaluations = session.get("evaluations", [])

    if not evaluations:
        raise ValueError("没有回答记录，无法生成总评")

    # AI 总评
    job = await get_collection("jobs").find_one({"_id": _oid(session["job_id"])})
    job_context = f"{job.get('title', '')} - {job.get('description', '')[:200]}" if job else ""

    overall_prompt = build_overall_eval_prompt(conversation, evaluations, job_context)
    overall_response = await chat_json(OVERALL_EVAL_SYSTEM_PROMPT, overall_prompt)

    overall = {
        "total_score": max(0, min(100, int(overall_response.get("total_score", 50)))),
        "technical_score": max(0, min(100, int(overall_response.get("technical_score", 50)))),
        "communication_score": max(0, min(100, int(overall_response.get("communication_score", 50)))),
        "cultural_fit_score": max(0, min(100, int(overall_response.get("cultural_fit_score", 50)))),
        "summary": str(overall_response.get("summary", "")),
        "recommendation": overall_response.get("recommendation", "needs_further_evaluation"),
        "key_concerns": [str(c) for c in overall_response.get("key_concerns", [])],
        "highlights": [str(h) for h in overall_response.get("highlights", [])],
    }

    now = datetime.now(timezone.utc)
    await sessions_col.update_one(
        {"_id": _oid(session_id)},
        {"$set": {
            "status": "completed",
            "overall_evaluation": overall,
            "updated_at": now,
        }}
    )

    updated = await sessions_col.find_one({"_id": _oid(session_id)})
    logger.info(f"面试会话已结束: {session_id}, 总分={overall['total_score']}")
    return _format_session(updated)


async def get_session(session_id: str) -> Optional[dict]:
    """获取面试会话详情"""
    session = await get_collection("interview_sessions").find_one({"_id": _oid(session_id)})
    if session:
        return _format_session(session)
    return None


async def list_sessions(
    job_id: Optional[str] = None,
    resume_id: Optional[str] = None,
    status: Optional[str] = None,
) -> list:
    """列出面试会话"""
    query = {}
    if job_id:
        query["job_id"] = job_id
    if resume_id:
        query["resume_id"] = resume_id
    if status:
        query["status"] = status

    cursor = get_collection("interview_sessions").find(query).sort("created_at", -1).limit(50)
    docs = await cursor.to_list(length=50)
    return [_format_session(d) for d in docs]


def _format_session(doc: dict) -> dict:
    """格式化会话文档"""
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    # 移除内部字段
    doc.pop("current_question_index", None)
    return doc
