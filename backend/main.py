"""
HR智能简历筛选系统 — 应用入口
启动 FastAPI 服务器 + pywebview 桌面窗口
"""
import sys
import threading
import time
from pathlib import Path

# 将 backend 目录加入 Python 路径
sys.path.insert(0, str(Path(__file__).resolve().parent))


def start_server(host: str, port: int, debug: bool):
    """在子线程中启动 FastAPI 服务器"""
    import uvicorn
    from app import create_app

    app = create_app()
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info" if debug else "warning",
    )


def main():
    from config import settings

    host = settings.server_host
    port = settings.server_port
    debug = settings.debug

    # 1. 启动 FastAPI 服务器（守护线程）
    server_thread = threading.Thread(
        target=start_server,
        args=(host, port, debug),
        daemon=True,
    )
    server_thread.start()

    # 等待服务器就绪
    time.sleep(1.5)
    print(f"✅ API 服务器已启动: http://{host}:{port}")

    # 2. 启动 pywebview 桌面窗口
    try:
        import webview

        window = webview.create_window(
            title="HR智能简历筛选系统",
            url=f"http://{host}:{port}",
            width=1400,
            height=900,
            min_size=(1024, 768),
            resizable=True,
        )
        webview.start(debug=debug)
    except ImportError:
        # pywebview 未安装时，只运行服务器
        print("⚠️ pywebview 未安装，仅运行 API 服务器模式")
        print(f"请在浏览器中访问: http://{host}:{port}")
        try:
            server_thread.join()
        except KeyboardInterrupt:
            print("\n服务器已停止")


if __name__ == "__main__":
    main()
