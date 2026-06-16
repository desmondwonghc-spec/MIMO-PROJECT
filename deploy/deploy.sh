#!/bin/bash
# HR智能简历筛选系统 - 阿里云一键部署脚本
# 用法: sudo bash deploy/deploy.sh

set -e

echo "========================================="
echo "  HR智能简历筛选系统 - 自动部署"
echo "========================================="

# 配置
APP_DIR="/opt/hr-system"
REPO_URL="https://github.com/desmondwonghc-spec/MIMO-PROJECT.git"

# 1. 安装系统依赖
echo "[1/8] 安装系统依赖..."
apt-get update -y
apt-get install -y python3 python3-pip python3-venv nginx mongodb

# 2. 安装 Node.js 22
echo "[2/8] 安装 Node.js..."
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
    apt-get install -y nodejs
fi
echo "  Node.js $(node --version)"

# 3. 启动 MongoDB
echo "[3/8] 启动 MongoDB..."
systemctl enable mongod
systemctl start mongod

# 4. 克隆代码
echo "[4/8] 部署代码..."
if [ -d "$APP_DIR" ]; then
    cd $APP_DIR && git pull origin main
else
    git clone $REPO_URL $APP_DIR
    cd $APP_DIR
fi

# 5. 构建前端
echo "[5/8] 构建前端..."
cd $APP_DIR/hr-system/frontend
npm install
npm run build

# 6. 安装后端依赖
echo "[6/8] 安装后端依赖..."
cd $APP_DIR/hr-system/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 7. 配置 Nginx
echo "[7/8] 配置 Nginx..."
cp $APP_DIR/hr-system/deploy/nginx.conf /etc/nginx/sites-available/hr-system
ln -sf /etc/nginx/sites-available/hr-system /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# 8. 配置 systemd 服务
echo "[8/8] 配置开机自启..."
cp $APP_DIR/hr-system/deploy/hr-system.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable hr-system
systemctl start hr-system

echo ""
echo "========================================="
echo "  部署完成!"
echo "========================================="
echo ""
echo "  应用状态:  systemctl status hr-system"
echo "  查看日志:  journalctl -u hr-system -f"
echo "  Nginx状态: systemctl status nginx"
echo "  访问地址:  http://$(curl -s ifconfig.me)"
echo ""
echo "  默认管理员: admin / admin123"
echo "  请登录后立即修改密码!"
echo ""
