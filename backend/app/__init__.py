"""
FastAPI 应用工厂
"""
from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from database import connect_db, close_db
from config import settings, get_frontend_dist_path


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动：连接数据库
    await connect_db()
    print(f"✅ MongoDB 已连接: {settings.mongodb_url}")

    # 尝试初始化 DeepSeek 客户端
    await _init_deepseek()

    yield
    # 关闭：断开数据库
    await close_db()
    print("✅ MongoDB 连接已关闭")


async def _init_deepseek():
    """从数据库设置中加载 API 密钥并初始化 DeepSeek 客户端"""
    try:
        from database import get_collection
        from app.ai.deepseek_client import init_client

        # 先用环境变量中的密钥
        api_key = settings.deepseek_api_key
        base_url = settings.deepseek_base_url

        # 尝试从数据库加载
        doc = await get_collection("app_settings").find_one({"key": "general"})
        if doc:
            if doc.get("deepseek_api_key"):
                api_key = doc["deepseek_api_key"]
            if doc.get("deepseek_base_url"):
                base_url = doc["deepseek_base_url"]

        if api_key:
            await init_client(api_key, base_url)
            print(f"✅ DeepSeek 客户端已初始化")
        else:
            print("⚠️ DeepSeek API 密钥未配置，请在设置页面中配置")
    except Exception as e:
        print(f"⚠️ DeepSeek 客户端初始化失败: {e}")


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    app = FastAPI(
        title="HR智能简历筛选系统",
        description="自动筛选简历、AI匹配评分、预面试、薪资分析",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS 配置（开发模式需要）
    if settings.debug:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # 注册自定义异常处理器
    from app.utils.exceptions import AppError, app_error_handler
    app.add_exception_handler(AppError, app_error_handler)

    # 注册 API 路由
    from app.routers import jobs, resumes, matching, interview, salary, settings_router
    app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["岗位管理"])
    app.include_router(resumes.router, prefix="/api/v1/resumes", tags=["简历管理"])
    app.include_router(matching.router, prefix="/api/v1/matching", tags=["匹配评分"])
    app.include_router(interview.router, prefix="/api/v1/interview", tags=["预面试"])
    app.include_router(salary.router, prefix="/api/v1/salary", tags=["薪资分析"])
    app.include_router(settings_router.router, prefix="/api/v1/settings", tags=["系统设置"])

    # 静态文件服务（生产模式）
    _mount_frontend(app)

    return app


def _mount_frontend(app: FastAPI) -> None:
    """挂载 Vue 前端静态文件"""
    frontend_dist = get_frontend_dist_path()

    if not frontend_dist.exists():
        # 开发模式下前端可能未构建，跳过
        return

    # 静态资源
    assets_path = frontend_dist / "assets"
    if assets_path.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_path)), name="static-assets")

    # SPA catch-all: 所有非 API 路由返回 index.html
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # 跳过 API 路由
        if full_path.startswith("api/"):
            return None
        file_path = frontend_dist / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dist / "index.html")
