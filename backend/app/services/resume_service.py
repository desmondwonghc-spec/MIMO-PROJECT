"""
简历服务层
处理简历上传、AI解析编排、数据查询
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId, errors as bson_errors

from database import get_collection
from app.file_handlers.file_storage import save_upload_file, delete_resume_file
from app.file_handlers.pdf_handler import extract_text_from_pdf
from app.file_handlers.docx_handler import extract_text_from_docx
from app.ai.deepseek_client import chat_json
from app.ai.prompts.resume_extraction import SYSTEM_PROMPT, build_user_prompt
from app.ai.parsers.resume_parser import parse_resume_data
from app.models.resume import ParsingStatus

logger = logging.getLogger(__name__)


def _oid(resume_id: str) -> ObjectId:
    """安全转换 ObjectId"""
    try:
        return ObjectId(resume_id)
    except (bson_errors.InvalidId, Exception):
        raise ValueError(f"无效的简历ID: {resume_id}")


async def upload_and_parse(filename: str, file_content: bytes, source: str = "upload") -> dict:
    """
    上传简历文件并启动异步解析
    :param filename: 原始文件名
    :param file_content: 文件内容
    :param source: 来源 (boss/upload/referral/other)
    :return: MongoDB 文档（解析状态为 pending）
    """
    # 1. 保存文件到磁盘
    file_info = save_upload_file(filename, file_content)

    # 2. 创建 MongoDB 记录
    now = datetime.now(timezone.utc)
    doc = {
        "original_filename": filename,
        "file_path": file_info["file_path"],
        "file_type": file_info["file_type"],
        "file_size": file_info["file_size"],
        "source": source,
        "raw_text": "",
        "structured_data": None,
        "parsing_status": ParsingStatus.PENDING.value,
        "parsing_error": None,
        "parsing_model": "",
        "created_at": now,
        "updated_at": now,
    }

    collection = get_collection("resumes")
    result = await collection.insert_one(doc)
    resume_id = str(result.inserted_id)

    # 3. 启动异步解析（不阻塞响应）
    asyncio.create_task(_parse_resume_async(resume_id))

    doc["_id"] = resume_id
    return doc


async def _parse_resume_async(resume_id: str) -> None:
    """
    异步解析简历：提取文本 → AI结构化解析 → 存储结果
    """
    collection = get_collection("resumes")
    try:
        # 更新状态为处理中
        await collection.update_one(
            {"_id": _oid(resume_id)},
            {"$set": {"parsing_status": ParsingStatus.PROCESSING.value, "updated_at": datetime.now(timezone.utc)}}
        )

        # 获取文档
        doc = await collection.find_one({"_id": _oid(resume_id)})
        if not doc:
            return

        # 1. 提取文本
        file_path = doc["file_path"]
        file_type = doc["file_type"]
        if file_type == "pdf":
            raw_text = extract_text_from_pdf(file_path)
        else:
            raw_text = extract_text_from_docx(file_path)

        # 保存原始文本
        await collection.update_one(
            {"_id": _oid(resume_id)},
            {"$set": {"raw_text": raw_text}}
        )

        # 2. AI 结构化解析
        user_prompt = build_user_prompt(raw_text)
        ai_response = await chat_json(SYSTEM_PROMPT, user_prompt)

        # 3. 验证和转换
        structured = parse_resume_data(ai_response)

        # 4. 存储结果
        await collection.update_one(
            {"_id": _oid(resume_id)},
            {"$set": {
                "structured_data": structured.model_dump(),
                "parsing_status": ParsingStatus.COMPLETED.value,
                "parsing_model": "deepseek-chat",
                "updated_at": datetime.now(timezone.utc),
            }}
        )
        logger.info(f"简历 {resume_id} 解析完成")

    except Exception as e:
        logger.error(f"简历 {resume_id} 解析失败: {e}")
        await collection.update_one(
            {"_id": _oid(resume_id)},
            {"$set": {
                "parsing_status": ParsingStatus.FAILED.value,
                "parsing_error": str(e),
                "updated_at": datetime.now(timezone.utc),
            }}
        )


async def reparse_resume(resume_id: str) -> None:
    """重新解析简历"""
    collection = get_collection("resumes")
    doc = await collection.find_one({"_id": _oid(resume_id)})
    if not doc:
        raise ValueError(f"简历 {resume_id} 不存在")

    # 重置状态
    await collection.update_one(
        {"_id": _oid(resume_id)},
        {"$set": {
            "parsing_status": ParsingStatus.PENDING.value,
            "parsing_error": None,
            "structured_data": None,
            "updated_at": datetime.now(timezone.utc),
        }}
    )

    asyncio.create_task(_parse_resume_async(resume_id))


async def get_resume(resume_id: str) -> Optional[dict]:
    """获取简历详情"""
    collection = get_collection("resumes")
    return await collection.find_one({"_id": _oid(resume_id)})


async def list_resumes(
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """获取简历列表"""
    collection = get_collection("resumes")

    query = {}
    if status:
        query["parsing_status"] = status
    if search:
        query["$or"] = [
            {"original_filename": {"$regex": search, "$options": "i"}},
            {"structured_data.name": {"$regex": search, "$options": "i"}},
        ]

    total = await collection.count_documents(query)
    skip = (page - 1) * page_size
    cursor = collection.find(query).sort("created_at", -1).skip(skip).limit(page_size)
    docs = await cursor.to_list(length=page_size)

    # 转换 _id
    for doc in docs:
        doc["id"] = str(doc.pop("_id"))

    return {
        "items": docs,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


async def delete_resume(resume_id: str) -> bool:
    """删除简历（文件+记录）"""
    collection = get_collection("resumes")
    doc = await collection.find_one({"_id": _oid(resume_id)})
    if not doc:
        return False

    # 删除文件
    if doc.get("file_path"):
        delete_resume_file(doc["file_path"])

    # 删除记录
    result = await collection.delete_one({"_id": _oid(resume_id)})
    return result.deleted_count > 0
