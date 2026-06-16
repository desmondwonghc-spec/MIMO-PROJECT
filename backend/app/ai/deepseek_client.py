"""
DeepSeek API 客户端封装
使用 OpenAI SDK 兼容接口
"""
import json
import logging
from typing import Optional
import httpx
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

# 全局客户端实例
_client: Optional[AsyncOpenAI] = None


async def init_client(api_key: str, base_url: str = "https://api.deepseek.com") -> None:
    """初始化 DeepSeek 客户端（强制IPv4避免连接问题）"""
    global _client
    # 创建 httpx 客户端，强制使用 IPv4
    transport = httpx.AsyncHTTPTransport(local_address="0.0.0.0")
    http_client = httpx.AsyncClient(transport=transport, timeout=60)
    _client = AsyncOpenAI(
        api_key=api_key,
        base_url=base_url,
        http_client=http_client,
    )
    logger.info("DeepSeek 客户端已初始化")


def get_client() -> AsyncOpenAI:
    """获取客户端实例"""
    if _client is None:
        raise RuntimeError("DeepSeek 客户端未初始化，请先在设置中配置 API 密钥")
    return _client


async def chat_json(
    system_prompt: str,
    user_prompt: str,
    model: str = "deepseek-chat",
    temperature: float = 0.1,
    max_tokens: int = 4096,
) -> dict:
    """
    发送请求并返回 JSON 格式的响应
    用于简历解析、匹配评分等需要结构化输出的场景
    """
    client = get_client()
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=temperature,
            max_tokens=max_tokens,
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except json.JSONDecodeError as e:
        logger.error(f"AI 响应 JSON 解析失败: {e}")
        raise RuntimeError(f"AI 返回的数据格式错误: {str(e)}")
    except Exception as e:
        logger.error(f"DeepSeek API 调用失败: {e}")
        raise RuntimeError(f"AI 服务调用失败: {str(e)}")


async def chat_text(
    system_prompt: str,
    user_prompt: str,
    model: str = "deepseek-chat",
    temperature: float = 0.3,
    max_tokens: int = 4096,
) -> str:
    """
    发送请求并返回纯文本响应
    用于面试问答、邮件生成等场景
    """
    client = get_client()
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"DeepSeek API 调用失败: {e}")
        raise RuntimeError(f"AI 服务调用失败: {str(e)}")
