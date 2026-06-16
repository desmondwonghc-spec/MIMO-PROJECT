"""
简历管理 API 路由
"""
from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, Query, Depends
from fastapi.responses import FileResponse

from app.services import resume_service
from app.models.resume import ResumeResponse, ResumeListResponse, ResumeStructuredData
from app.models.common import paginate
from app.utils.exceptions import NotFoundError, ValidationError
from app.file_handlers.file_storage import get_resume_file_path
from app.utils.auth_deps import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


def _doc_to_response(doc: dict) -> dict:
    """将 MongoDB 文档转换为响应格式"""
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    elif "id" not in doc:
        doc["id"] = ""

    if doc.get("structured_data") and isinstance(doc["structured_data"], dict):
        try:
            doc["structured_data"] = ResumeStructuredData(**doc["structured_data"])
        except Exception:
            doc["structured_data"] = None

    doc.setdefault("parsing_error", None)
    doc.setdefault("source", "upload")
    return doc


@router.get("", response_model=ResumeListResponse)
async def list_resumes(
    status: Optional[str] = Query(default=None, description="解析状态筛选"),
    search: Optional[str] = Query(default=None, description="搜索关键词"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    """获取简历列表"""
    result = await resume_service.list_resumes(
        status=status, search=search, page=page, page_size=page_size,
    )
    result["items"] = [_doc_to_response(doc) for doc in result["items"]]
    return result


@router.post("/upload", response_model=ResumeResponse, status_code=201)
async def upload_resume(
    file: UploadFile = File(..., description="简历文件 (PDF/DOCX)"),
    source: str = Form(default="upload", description="来源"),
):
    """上传简历文件，自动启动AI解析"""
    if not file.filename:
        raise ValidationError("请选择要上传的文件")
    content = await file.read()
    if not content:
        raise ValidationError("文件内容为空")
    doc = await resume_service.upload_and_parse(
        filename=file.filename, file_content=content, source=source,
    )
    return _doc_to_response(doc)


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(resume_id: str):
    """获取简历详情"""
    doc = await resume_service.get_resume(resume_id)
    if not doc:
        raise NotFoundError("简历", resume_id)
    return _doc_to_response(doc)


@router.delete("/{resume_id}", status_code=204)
async def delete_resume(resume_id: str):
    """删除简历"""
    success = await resume_service.delete_resume(resume_id)
    if not success:
        raise NotFoundError("简历", resume_id)


@router.post("/{resume_id}/reparse", response_model=ResumeResponse)
async def reparse_resume(resume_id: str):
    """重新解析简历"""
    doc = await resume_service.get_resume(resume_id)
    if not doc:
        raise NotFoundError("简历", resume_id)
    await resume_service.reparse_resume(resume_id)
    doc = await resume_service.get_resume(resume_id)
    return _doc_to_response(doc)


@router.get("/{resume_id}/file")
async def download_resume_file(resume_id: str):
    """下载原始简历文件"""
    doc = await resume_service.get_resume(resume_id)
    if not doc:
        raise NotFoundError("简历", resume_id)
    file_path = get_resume_file_path(doc["file_path"])
    return FileResponse(
        path=str(file_path), filename=doc["original_filename"],
        media_type="application/octet-stream",
    )
