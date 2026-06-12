"""
PDF 文件文本提取
使用 PyMuPDF (fitz)
"""
from pathlib import Path
import fitz  # PyMuPDF


def extract_text_from_pdf(file_path: str) -> str:
    """
    从 PDF 文件中提取纯文本
    :param file_path: PDF 文件路径
    :return: 提取的文本内容
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF 文件不存在: {file_path}")

    text_parts = []
    try:
        doc = fitz.open(str(path))
        for page in doc:
            text = page.get_text("text")
            if text.strip():
                text_parts.append(text.strip())
        doc.close()
    except Exception as e:
        raise RuntimeError(f"PDF 解析失败: {str(e)}")

    full_text = "\n\n".join(text_parts)
    if not full_text.strip():
        raise ValueError("PDF 文件中未提取到文本内容，可能是扫描件（需OCR）")

    return full_text
