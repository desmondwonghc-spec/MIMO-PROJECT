"""
开发服务器启动脚本
同时启动 FastAPI 后端和 Vue 前端开发服务器
"""
import subprocess
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"


def main():
    processes = []

    # 启动后端
    print("🚀 启动后端服务器...")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app:create_app", "--factory",
         "--host", "127.0.0.1", "--port", "8765", "--reload"],
        cwd=str(BACKEND),
    )
    processes.append(backend_proc)

    # 启动前端
    print("🚀 启动前端开发服务器...")
    frontend_proc = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=str(FRONTEND),
        shell=True,
    )
    processes.append(frontend_proc)

    print("\n✅ 开发服务器已启动")
    print("   后端: http://127.0.0.1:8765")
    print("   前端: http://localhost:5173")
    print("   API文档: http://127.0.0.1:8765/docs")
    print("\n按 Ctrl+C 停止所有服务\n")

    try:
        for p in processes:
            p.wait()
    except KeyboardInterrupt:
        print("\n🛑 停止所有服务...")
        for p in processes:
            p.terminate()


if __name__ == "__main__":
    main()
