"""
匹配评分 API 路由
"""
from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Query, Depends

from app.services import matching_service
from app.models.matching import (
    MatchSingleRequest, MatchBatchRequest,
    MatchResultResponse, MatchResultListResponse,
    DimensionScores, DimensionScore,
)
from app.utils.exceptions import NotFoundError, ValidationError
from app.utils.auth_deps import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


def _doc_to_response(doc: dict) -> dict:
    if "dimension_scores" in doc and isinstance(doc["dimension_scores"], dict):
        dims = doc["dimension_scores"]
        for key in dims:
            if isinstance(dims[key], dict):
                dims[key] = DimensionScore(**dims[key])
        doc["dimension_scores"] = DimensionScores(**dims)
    doc.setdefault("resume_name", "")
    doc.setdefault("strengths", [])
    doc.setdefault("weaknesses", [])
    doc.setdefault("summary", "")
    doc.setdefault("ai_model", "")
    return doc


@router.post("/single", response_model=MatchResultResponse)
async def match_single(req: MatchSingleRequest):
    try:
        result = await matching_service.match_single(req.job_id, req.resume_id)
    except ValueError as e:
        raise ValidationError(str(e))
    return _doc_to_response(result)


@router.post("/batch")
async def match_batch(req: MatchBatchRequest):
    if not req.resume_ids:
        raise ValidationError("请提供至少一个简历ID")
    results = await matching_service.match_batch(req.job_id, req.resume_ids)
    success = [r for r in results if "error" not in r]
    failed = [r for r in results if "error" in r]
    return {
        "total": len(results),
        "success_count": len(success),
        "failed_count": len(failed),
        "results": [_doc_to_response(r) if "error" not in r else r for r in results],
    }


@router.get("/results/{job_id}", response_model=MatchResultListResponse)
async def get_match_results(
    job_id: str,
    min_score: Optional[int] = Query(default=None, ge=0, le=100),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    result = await matching_service.get_match_results(
        job_id=job_id, min_score=min_score, page=page, page_size=page_size,
    )
    result["items"] = [_doc_to_response(doc) for doc in result["items"]]
    return result


@router.get("/result/{match_id}", response_model=MatchResultResponse)
async def get_match_result(match_id: str):
    doc = await matching_service.get_match_result(match_id)
    if not doc:
        raise NotFoundError("匹配结果", match_id)
    return _doc_to_response(doc)


@router.delete("/result/{match_id}", status_code=204)
async def delete_match_result(match_id: str):
    success = await matching_service.delete_match_result(match_id)
    if not success:
        raise NotFoundError("匹配结果", match_id)
