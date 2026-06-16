<#
.SYNOPSIS
    HR智能简历筛选系统 - Windows Server 部署脚本
.DESCRIPTION
    在阿里云 Windows Server 2022 上一键部署
    使用前请先远程连接到服务器，在 PowerShell 中运行
#>

$ErrorActionPreference = "Stop"
$APP_DIR = "C:\hr-system"
$REPO_URL = "https://github.com/desmondwonghc-spec/MIMO-PROJECT.git"

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  HR智能简历筛选系统 - Windows部署" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 检查/安装必要工具
Write-Host "[1/6] 检查环境..." -ForegroundColor Yellow

# 检查 Git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "  安装 Git..."
    winget install --id Git.Git -e --accept-package-agreements --accept-source-agreements
}

# 检查 Node.js
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "  安装 Node.js..."
    winget install --id OpenJS.NodeJS.LTS -e --accept-package-agreements --accept-source-agreements
}

# 检查 Python
$pyVer = & python --version 2>&1
Write-Host "  Python: $pyVer"
Write-Host "  Node.js: $(node --version 2>&1)"
Write-Host "  Git: $(git --version 2>&1)"

# 2. 检查/安装 MongoDB
Write-Host ""
Write-Host "[2/6] 检查 MongoDB..." -ForegroundColor Yellow
$mongod = Get-Command mongod -ErrorAction SilentlyContinue
if (-not $mongod) {
    Write-Host "  MongoDB 未安装，请手动安装 MongoDB Community Server"
    Write-Host "  下载地址: https://www.mongodb.com/try/download/community"
    Write-Host "  安装后重启此脚本"
    exit 1
} else {
    $mongodVer = & mongod --version 2>&1 | Select-String "db version" | Select-Object -First 1
    Write-Host "  MongoDB: $mongodVer"

    # 确保 MongoDB 服务运行
    $mongoService = Get-Service -Name "MongoDB*" -ErrorAction SilentlyContinue
    if ($mongoService) {
        if ($mongoService.Status -ne "Running") {
            Start-Service $mongoService.Name
            Write-Host "  MongoDB 服务已启动"
        }
    }
}

# 3. 克隆代码
Write-Host ""
Write-Host "[3/6] 部署代码..." -ForegroundColor Yellow
if (Test-Path "$APP_DIR\.git") {
    Set-Location $APP_DIR
    git pull origin main
} else {
    git clone $REPO_URL $APP_DIR
    Set-Location "$APP_DIR\hr-system"
}
Write-Host "  代码部署完成: $APP_DIR"

# 4. 构建前端
Write-Host ""
Write-Host "[4/6] 构建前端..." -ForegroundColor Yellow
Set-Location "$APP_DIR\hr-system\frontend"
npm install --no-proxy
npm run build
Write-Host "  前端构建完成"

# 5. 安装后端依赖
Write-Host ""
Write-Host "[5/6] 安装后端依赖..." -ForegroundColor Yellow
Set-Location "$APP_DIR\hr-system\backend"

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

& .\.venv\Scripts\activate.ps1
.\.venv\Scripts\pip.exe install -r requirements.txt --proxy "" --trusted-host pypi.org --trusted-host files.pythonhosted.org 2>$null
Write-Host "  后端依赖安装完成"

# 6. 配置防火墙
Write-Host ""
Write-Host "[6/6] 配置防火墙..." -ForegroundColor Yellow
# 检查端口是否已开放
$rule = Get-NetFirewallRule -DisplayName "HR-System-8765" -ErrorAction SilentlyContinue
if (-not $rule) {
    New-NetFirewallRule -DisplayName "HR-System-8765" -Direction Inbound -Protocol TCP -LocalPort 8765 -Action Allow
    Write-Host "  防火墙规则已添加 (端口 8765)"
} else {
    Write-Host "  防火墙规则已存在"
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "  部署完成!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  访问地址: http://47.98.97.215:8765"
Write-Host "  默认账号: admin / admin123"
Write-Host ""
Write-Host "  启动方式:"
Write-Host "  cd $APP_DIR\hr-system\backend"
Write-Host "  .\.venv\Scripts\activate.ps1"
Write-Host "  python main.py --host 0.0.0.0"
Write-Host ""
Write-Host "  或者启动桌面模式:"
Write-Host "  python main.py"
Write-Host ""
