"""
应用配置管理
使用 pydantic-settings 从环境变量和 .env 文件加载配置
"""
import sys
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


def get_base_path() -> Path:
    """获取应用根路径，兼容 PyInstaller 打包"""
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def get_frontend_dist_path() -> Path:
    """获取 Vue 前端构建产物路径"""
    return get_base_path() / "frontend" / "dist"


def get_data_path() -> Path:
    """获取运行时数据目录（简历文件、备份等），始终在打包目录外"""
    if getattr(sys, 'frozen', False):
        base = Path(sys.executable).parent / "data"
    else:
        base = get_base_path() / "data"
    base.mkdir(parents=True, exist_ok=True)
    return base


def get_resumes_path() -> Path:
    """获取简历文件存储目录"""
    path = get_data_path() / "resumes"
    path.mkdir(parents=True, exist_ok=True)
    return path


class Settings(BaseSettings):
    """应用配置"""
    # MongoDB
    mongodb_url: str = Field(default="mongodb://localhost:27017", description="MongoDB 连接地址")
    mongodb_db_name: str = Field(default="hr_screening", description="数据库名称")

    # DeepSeek API
    deepseek_api_key: str = Field(default="", description="DeepSeek API 密钥")
    deepseek_base_url: str = Field(default="https://api.deepseek.com", description="DeepSeek API 地址")
    deepseek_model: str = Field(default="deepseek-chat", description="默认模型")
    deepseek_timeout: int = Field(default=60, description="API 请求超时（秒）")

    # 服务器
    server_host: str = Field(default="127.0.0.1", description="服务器绑定地址")
    server_port: int = Field(default=8765, description="服务器端口")

    # 文件上传
    max_upload_size: int = Field(default=10 * 1024 * 1024, description="最大上传文件大小（字节）")

    # 开发模式
    debug: bool = Field(default=False, description="调试模式")

    model_config = {
        "env_file": str(get_base_path() / ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


# 全局配置实例
settings = Settings()
