"""
匹配评分解析器
验证和转换 AI 返回的匹配结果
"""
from app.models.matching import (
    MatchResultResponse, DimensionScores, DimensionScore,
    MatchRecommendation,
)


def parse_match_result(ai_response: dict, job_id: str, resume_id: str, resume_name: str, model: str) -> dict:
    """
    将 AI 返回的匹配结果解析为存储格式
    :return: MongoDB 文档字典
    """
    from datetime import datetime, timezone

    # 解析维度分数
    dims = ai_response.get("dimension_scores", {})
    dimension_scores = {}
    for key in ["skills_match", "experience_match", "education_match", "location_match", "salary_match"]:
        dim = dims.get(key, {})
        dimension_scores[key] = {
            "score": _clamp_score(dim.get("score", 0)),
            "reasoning": str(dim.get("reasoning", "")),
        }

    # 计算加权总分（如果AI没给或不合理）
    weights = {
        "skills_match": 0.30,
        "experience_match": 0.25,
        "education_match": 0.15,
        "location_match": 0.10,
        "salary_match": 0.20,
    }
    calculated_score = sum(
        dimension_scores[k]["score"] * w for k, w in weights.items()
    )
    calculated_score = round(calculated_score)

    # 使用AI给出的分数和计算分数中更合理的那个
    ai_score = _clamp_score(ai_response.get("overall_score", 0))
    overall_score = ai_score if abs(ai_score - calculated_score) < 15 else calculated_score

    # 确定推荐等级
    recommendation = _get_recommendation(overall_score)
    ai_rec = ai_response.get("recommendation", "")
    if ai_rec in [r.value for r in MatchRecommendation]:
        recommendation = ai_rec

    return {
        "job_id": job_id,
        "resume_id": resume_id,
        "resume_name": resume_name,
        "overall_score": overall_score,
        "dimension_scores": dimension_scores,
        "strengths": [str(s) for s in ai_response.get("strengths", [])],
        "weaknesses": [str(w) for w in ai_response.get("weaknesses", [])],
        "recommendation": recommendation,
        "summary": str(ai_response.get("summary", "")),
        "ai_model": model,
        "created_at": datetime.now(timezone.utc),
    }


def _clamp_score(score) -> int:
    """将分数限制在 0-100 范围内"""
    try:
        s = int(float(score))
        return max(0, min(100, s))
    except (ValueError, TypeError):
        return 0


def _get_recommendation(score: int) -> str:
    """根据总分确定推荐等级"""
    if score >= 85:
        return MatchRecommendation.STRONG_MATCH.value
    elif score >= 70:
        return MatchRecommendation.GOOD_MATCH.value
    elif score >= 55:
        return MatchRecommendation.PARTIAL_MATCH.value
    elif score >= 40:
        return MatchRecommendation.WEAK_MATCH.value
    else:
        return MatchRecommendation.NO_MATCH.value
