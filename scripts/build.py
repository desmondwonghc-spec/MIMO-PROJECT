"""
构建脚本：前端构建 + PyInstaller 打包
用法: python scripts/build.py
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"
BACKEND = ROOT / "backend"
PACKAGING = ROOT / "packaging"


def run(cmd, cwd, desc):
    print(f"\n{'='*50}")
    print(f"  {desc}")
    print(f"{'='*50}")
    result = subprocess.run(cmd, cwd=str(cwd), shell=True)
    if result.returncode != 0:
        print(f"❌ {desc} 失败 (exit code {result.returncode})")
        sys.exit(1)
    print(f"✅ {desc} 完成")


def main():
    print("🚀 HR智能简历筛选系统 - 构建打包")
    print(f"   项目路径: {ROOT}")

    # Step 1: 构建前端
    run("npm run build", FRONTEND, "Step 1: 构建 Vue 前端")

    # Step 2: 检查 dist 是否存在
    dist = FRONTEND / "dist"
    if not dist.exists():
        print("❌ 前端构建产物不存在")
        sys.exit(1)
    print(f"   前端产物: {dist} ({len(list(dist.rglob('*')))} files)")

    # Step 3: PyInstaller 打包
    spec = PACKAGING / "hr_screening.spec"
    run(f'pyinstaller "{spec}" --distpath "{ROOT / "dist"}'  f'" --workpath "{ROOT / "build"}"',
        ROOT, "Step 2: PyInstaller 打包")

    # Step 4: 输出结果
    output = ROOT / "dist" / "HR智能简历筛选"
    if output.exists():
        print(f"\n{'='*50}")
        print(f"  🎉 打包完成!")
        print(f"  输出路径: {output}")
        print(f"  可执行文件: {output / 'HR智能简历筛选.exe'}")
        print(f"{'='*50}")
    else:
        print("⚠️ 打包输出目录不存在，请检查错误信息")


if __name__ == "__main__":
    main()
