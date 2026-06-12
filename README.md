# HR智能简历筛选系统

AI驱动的简历自动筛选桌面应用，帮助HR高效筛选BOSS直聘简历。

## 功能特性

- 📋 **岗位管理** — 创建和管理招聘岗位，设置岗位要求和薪资范围
- 📄 **简历解析** — 上传PDF/Word简历，AI自动提取结构化数据
- 🎯 **智能匹配** — 5维度AI评分（技能/经验/学历/地点/薪资）
- 💬 **AI预面试** — 基于岗位和简历生成面试问题，模拟Q&A评估
- 💰 **薪资分析** — AI调研市场薪资水平，预估候选人薪资
- ⚙️ **系统设置** — DeepSeek API配置

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + TypeScript + Vite |
| 后端 | Python FastAPI |
| 桌面 | pywebview |
| 数据库 | MongoDB |
| AI | DeepSeek API |

## 快速开始

### 前置要求

- Python 3.8+
- Node.js 18+
- MongoDB（本地运行）

### 安装

```bash
# 后端依赖
cd backend
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 前端依赖
cd frontend
npm install
```

### 开发模式

```bash
# 终端1: 启动后端
cd backend
.venv\Scripts\activate
python -m uvicorn app:create_app --factory --host 127.0.0.1 --port 8765 --reload

# 终端2: 启动前端
cd frontend
npm run dev
```

访问 http://localhost:5173

### 桌面模式

```bash
cd backend
python main.py
```

### 构建打包

```bash
# 1. 构建前端
cd frontend && npm run build

# 2. 打包桌面应用
cd ..
pyinstaller packaging/hr_screening.spec
```

## 项目结构

```
hr-system/
├── backend/          # Python FastAPI 后端
├── frontend/         # Vue 3 前端
├── data/             # 运行时数据
├── scripts/          # 构建脚本
└── packaging/        # PyInstaller 配置
```

## 环境变量

复制 `backend/.env.example` 为 `backend/.env` 并配置：

```env
MONGODB_URL=mongodb://localhost:27017
DEEPSEEK_API_KEY=your_api_key_here
```
