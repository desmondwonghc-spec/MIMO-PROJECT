"""
系统设置相关 Pydantic 模型
"""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class EmailSettings(BaseModel):
    smtp_host: str = Field(default="", description="SMTP 服务器")
    smtp_port: int = Field(default=587, description="SMTP 端口")
    smtp_user: str = Field(default="", description="SMTP 用户名")
    smtp_password: str = Field(default="", description="SMTP 密码")
    from_address: str = Field(default="", description="发件人地址")


class EmailTemplates(BaseModel):
    interview_invitation: str = Field(default="", description="面试邀请模板")
    rejection: str = Field(default="", description="拒绝通知模板")
    offer: str = Field(default="", description="Offer通知模板")


class SettingsUpdate(BaseModel):
    deepseek_api_key: Optional[str] = Field(default=None, description="DeepSeek API 密钥")
    deepseek_base_url: Optional[str] = None
    deepseek_model: Optional[str] = None
    email_smtp_host: Optional[str] = None
    email_smtp_port: Optional[int] = None
    email_smtp_user: Optional[str] = None
    email_smtp_password: Optional[str] = None
    email_from_address: Optional[str] = None
    language: Optional[str] = None
    theme: Optional[str] = None


class APITestRequest(BaseModel):
    api_key: Optional[str] = Field(default=None, description="API密钥")
    base_url: Optional[str] = None


class SettingsResponse(BaseModel):
    deepseek_api_key_set: bool = Field(description="是否已配置API密钥")
    deepseek_api_key_masked: str = Field(default="", description="掩码后的API密钥")
    deepseek_base_url: str
    deepseek_model: str
    email: EmailSettings
    language: str
    theme: str


class APITestResponse(BaseModel):
    success: bool
    message: str
    model: str = Field(default="")
