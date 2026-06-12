"""
文件存储管理
处理简历文件的保存、读取、删除
"""
import uuid
import shutil
from pathlib import Path
from config import get_resumes_path


def save_upload_file(filename: str, file_content: bytes) -> dict:
    """
    保存上传的文件到本地
    :param filename: 原始文件名
    :param file_content: 文件内容（字节）
    :return: {"file_path": str, "file_type": str, "file_size": int}
    """
    # 验证文件类型
    ext = Path(filename).suffix.lower()
    if ext not in (".pdf", ".docx"):
        raise ValueError(f"不支持的文件格式: {ext}，仅支持 .pdf 和 .docx")

    # 验证文件大小 (10MB)
    max_size = 10 * 1024 * 1024
    if len(file_content) > max_size:
        raise ValueError(f"文件过大: {len(file_content)} 字节，最大允许 {max_size} 字节")

    # 生成唯一文件名
    unique_id = uuid.uuid4().hex[:8]
    safe_name = f"{unique_id}_{filename}"
    save_path = get_resumes_path() / safe_name

    # 写入文件
    save_path.write_bytes(file_content)

    file_type = "pdf" if ext == ".pdf" else "docx"
    return {
        "file_path": str(save_path),
        "file_type": file_type,
        "file_size": len(file_content),
    }


def delete_resume_file(file_path: str) -> bool:
    """删除简历文件"""
    path = Path(file_path)
    if path.exists():
        path.unlink()
        return True
    return False


def get_resume_file_path(file_path: str) -> Path:
    """获取简历文件路径（验证存在）"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"简历文件不存在: {file_path}")
    return path
