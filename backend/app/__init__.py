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
    yield
    # 关闭：断开数据库
    await close_db()
    print("✅ MongoDB 连接已关闭")


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
