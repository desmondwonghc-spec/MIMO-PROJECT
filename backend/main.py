"""
HR智能简历筛选系统 — 应用入口
启动 FastAPI 服务器 + pywebview 桌面窗口
"""
import sys
import os
import threading
import time
from pathlib import Path

# 修复 Windows 控制台编码
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

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
    import argparse
    from config import settings

    parser = argparse.ArgumentParser(description="HR智能简历筛选系统")
    parser.add_argument("--host", default=settings.server_host, help="绑定地址 (默认: 127.0.0.1, 远程: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=settings.server_port, help="端口号 (默认: 8765)")
    parser.add_argument("--debug", action="store_true", default=settings.debug, help="调试模式")
    parser.add_argument("--no-window", action="store_true", help="不打开桌面窗口（服务器模式）")
    args = parser.parse_args()

    host = args.host
    port = args.port
    debug = args.debug
    no_window = args.no_window

    # 1. 启动 FastAPI 服务器（守护线程）
    server_thread = threading.Thread(
        target=start_server,
        args=(host, port, debug),
        daemon=True,
    )
    server_thread.start()

    # 等待服务器就绪
    time.sleep(1.5)
    print(f"API 服务器已启动: http://{host}:{port}")

    if no_window:
        # 服务器模式：无桌面窗口
        print("服务器模式运行中，按 Ctrl+C 停止")
        try:
            server_thread.join()
        except KeyboardInterrupt:
            print("\n服务器已停止")
        return

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
        print("pywebview 未安装，仅运行 API 服务器模式")
        print(f"请在浏览器中访问: http://{host}:{port}")
        try:
            server_thread.join()
        except KeyboardInterrupt:
            print("\n服务器已停止")


if __name__ == "__main__":
    main()
