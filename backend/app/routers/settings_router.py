"""
系统设置 API 路由
"""
from __future__ import annotations
from datetime import datetime, timezone
from fastapi import APIRouter
from bson import ObjectId

from database import get_collection
from config import settings as app_settings
from app.models.settings import (
    SettingsUpdate, SettingsResponse, EmailSettings,
    APITestRequest, APITestResponse,
)

router = APIRouter()

SETTINGS_KEY = "general"


async def _get_settings_doc() -> dict:
    """获取或创建设置文档"""
    collection = get_collection("app_settings")
    doc = await collection.find_one({"key": SETTINGS_KEY})
    if not doc:
        doc = {
            "key": SETTINGS_KEY,
            "deepseek_api_key": "",
            "deepseek_base_url": app_settings.deepseek_base_url,
            "deepseek_model": app_settings.deepseek_model,
            "email_smtp_host": "",
            "email_smtp_port": 587,
            "email_smtp_user": "",
            "email_smtp_password": "",
            "email_from_address": "",
            "language": "zh-CN",
            "theme": "light",
            "updated_at": datetime.now(timezone.utc),
        }
        await collection.insert_one(doc)
    return doc


def _mask_api_key(key: str) -> str:
    """掩码API密钥"""
    if not key or len(key) < 8:
        return ""
    return key[:4] + "*" * (len(key) - 8) + key[-4:]


@router.get("", response_model=SettingsResponse)
async def get_settings():
    """获取系统设置"""
    doc = await _get_settings_doc()
    return SettingsResponse(
        deepseek_api_key_set=bool(doc.get("deepseek_api_key")),
        deepseek_api_key_masked=_mask_api_key(doc.get("deepseek_api_key", "")),
        deepseek_base_url=doc.get("deepseek_base_url", app_settings.deepseek_base_url),
        deepseek_model=doc.get("deepseek_model", app_settings.deepseek_model),
        email=EmailSettings(
            smtp_host=doc.get("email_smtp_host", ""),
            smtp_port=doc.get("email_smtp_port", 587),
            smtp_user=doc.get("email_smtp_user", ""),
            smtp_password="",
            from_address=doc.get("email_from_address", ""),
        ),
        language=doc.get("language", "zh-CN"),
        theme=doc.get("theme", "light"),
    )


@router.put("", response_model=SettingsResponse)
async def update_settings(update: SettingsUpdate):
    """更新系统设置"""
    collection = get_collection("app_settings")

    update_data = update.model_dump(exclude_unset=True, exclude_none=True)
    if not update_data:
        return await get_settings()

    update_data["updated_at"] = datetime.now(timezone.utc)
    await collection.update_one(
        {"key": SETTINGS_KEY},
        {"$set": update_data},
        upsert=True,
    )

    # 如果更新了 API 密钥，重新初始化 DeepSeek 客户端
    if "deepseek_api_key" in update_data:
        await _reinit_deepseek()

    return await get_settings()


async def _reinit_deepseek():
    """重新初始化 DeepSeek 客户端"""
    from app.ai.deepseek_client import init_client

    doc = await _get_settings_doc()
    api_key = doc.get("deepseek_api_key", "")
    base_url = doc.get("deepseek_base_url", app_settings.deepseek_base_url)

    if api_key:
        try:
            await init_client(api_key, base_url)
        except Exception as e:
            print(f"DeepSeek 客户端重新初始化失败: {e}")


@router.post("/test-api", response_model=APITestResponse)
async def test_api_connection(req: APITestRequest):
    """测试 DeepSeek API 连接"""
    # 获取API密钥
    api_key = req.api_key
    if not api_key:
        doc = await _get_settings_doc()
        api_key = doc.get("deepseek_api_key", "")

    if not api_key:
        return APITestResponse(success=False, message="请先配置API密钥")

    base_url = req.base_url or app_settings.deepseek_base_url
    model = app_settings.deepseek_model

    try:
        import httpx
        from openai import AsyncOpenAI
        transport = httpx.AsyncHTTPTransport(local_address="0.0.0.0")
        http_client = httpx.AsyncClient(transport=transport, timeout=30)
        client = AsyncOpenAI(api_key=api_key, base_url=base_url, http_client=http_client)
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "你好，请回复'连接成功'"}],
            max_tokens=20,
        )
        reply = response.choices[0].message.content
        return APITestResponse(
            success=True,
            message=f"连接成功！模型回复: {reply}",
            model=model,
        )
    except Exception as e:
        return APITestResponse(
            success=False,
            message=f"连接失败: {str(e)}",
        )
