# 🎯 MIMO-PROJECT — HR智能简历筛选系统

<p align="center">
  <strong>AI驱动的桌面应用，帮助HR高效筛选简历、智能匹配评分、预面试评估</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?logo=python" />
  <img src="https://img.shields.io/badge/Vue-3-42b883?logo=vue.js" />
  <img src="https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi" />
  <img src="https://img.shields.io/badge/MongoDB-8.0-47A248?logo=mongodb" />
  <img src="https://img.shields.io/badge/DeepSeek-AI-FF6B35" />
</p>

---

## 📸 项目概览

HR智能简历筛选系统（TalentLens）是一个本地桌面应用，专为HR专业人士设计，通过AI技术自动化简历筛选流程。

### 核心价值

传统HR每天需要花费大量时间阅读简历、筛选候选人。本系统通过DeepSeek AI自动完成：

- **简历结构化解析**：上传PDF/Word简历，AI自动提取姓名、学历、经验、技能等结构化数据
- **5维度智能匹配**：技能(30%) + 经验(25%) + 薪资(20%) + 学历(15%) + 地点(10%)，生成0-100评分
- **AI预面试**：根据岗位要求和候选人简历差距，自动生成8-12道面试问题，实时评分反馈
- **薪资智能分析**：调研市场薪资水平，为每位候选人推荐个性化薪资区间

---

## 🏗 技术架构

```
┌─────────────────────────────────────────────────┐
│                桌面窗口 (pywebview)                │
│  ┌─────────────────────────────────────────────┐ │
│  │          Vue 3 + TypeScript 前端             │ │
│  │   (Pinia状态管理 / Vue Router / Axios)       │ │
│  └──────────────────┬──────────────────────────┘ │
│                     │ HTTP API                    │
│  ┌──────────────────▼──────────────────────────┐ │
│  │          Python FastAPI 后端                  │ │
│  │   ┌──────┐ ┌────────┐ ┌────────────────┐   │ │
│  │   │ 路由  │→│ 服务层  │→│ AI层(DeepSeek) │   │ │
│  │   └──────┘ └────────┘ └────────────────┘   │ │
│  │   ┌──────────────┐ ┌────────────────────┐  │ │
│  │   │ 文件处理器    │ │  MongoDB (Motor)   │  │ │
│  │   │ PDF/DOCX     │ │  异步驱动          │  │ │
│  │   └──────────────┘ └────────────────────┘  │ │
│  └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

### 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **桌面** | pywebview | 原生窗口，加载Vue前端 |
| **前端** | Vue 3 + TypeScript + Vite | Composition API, Pinia, Vue Router |
| **后端** | Python FastAPI | 异步框架，RESTful API |
| **数据库** | MongoDB | Motor异步驱动，本地存储 |
| **AI** | DeepSeek API | OpenAI兼容接口 |
| **文件解析** | PyMuPDF + python-docx | PDF/DOCX文本提取 |
| **打包** | PyInstaller | 桌面应用打包 |

---

## 🚀 快速开始

### 环境要求

- **Python** 3.8+
- **Node.js** 18+
- **MongoDB** （本地运行，默认端口27017）
- **DeepSeek API 密钥**（[申请地址](https://platform.deepseek.com/)）

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/desmondwonghc-spec/MIMO-PROJECT.git
cd MIMO-PROJECT/hr-system

# 2. 安装后端依赖
cd backend
py -3.8 -m venv .venv        # 或 python -m venv .venv
.venv\Scripts\activate         # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt

# 3. 安装前端依赖
cd ../frontend
npm install

# 4. 配置环境变量（可选，也可在界面上配置）
copy backend\.env.example backend\.env
# 编辑 .env 填入 DEEPSEEK_API_KEY
```

### 启动方式

**方式一：开发模式（前后端分离）**
```bash
# 终端1: 启动后端
cd backend
.venv\Scripts\activate
python -m uvicorn app:create_app --factory --port 8765

# 终端2: 启动前端
cd frontend
npm run dev
# 访问 http://localhost:5173
```

**方式二：桌面模式（推荐）**
```bash
# 先构建前端
cd frontend && npm run build && cd ..

# 启动桌面应用
cd backend
.venv\Scripts\activate
python main.py
# 自动弹出原生桌面窗口
```

**方式三：一键启动**
```
双击桌面上的 "HR智能简历筛选系统" 快捷方式
或双击项目根目录的 "启动HR系统.bat"
```

---

## 📋 功能详解

### 1. 📊 工作台（Dashboard）
- 实时统计：在招岗位数、收到简历数、匹配结果数
- 快速操作入口
- 最新匹配评分环形仪表盘（签名设计元素）

### 2. 💼 岗位管理
- **创建岗位**：填写岗位名称、地点、描述、职责、要求（学历/经验/技能）、薪资范围
- **编辑/删除**：支持全字段修改
- **搜索筛选**：关键词搜索 + 状态筛选（草稿/招聘中/暂停/关闭）
- **市场薪资**：AI自动调研岗位市场薪资水平

### 3. 📄 简历库
- **上传简历**：支持PDF和DOCX格式，拖拽上传
- **AI解析**：自动提取姓名、联系方式、学历、工作经历、技能、期望薪资等
- **解析状态追踪**：pending → processing → completed / failed
- **重新解析**：失败时可手动重试
- **人工校正**：解析结果可查看，HR可手动验证

### 4. 🎯 智能匹配评分
- **选择岗位** + **多选简历** → 一键批量匹配
- **5维度评分**：
  - 技能匹配（30%）：必备技能 + 加分技能重合度
  - 经验匹配（25%）：年限、行业、岗位相关性
  - 薪资匹配（20%）：期望薪资 vs 岗位范围
  - 学历匹配（15%）：层次 + 专业
  - 地点匹配（10%）：同城100 / 同省80 / 异地50
- **推荐等级**：强烈推荐 / 推荐 / 一般 / 不推荐 / 不匹配
- **优势/不足**：AI自动分析并标注

### 5. 💰 薪资分析
- **市场薪资调研**：选择岗位或手动输入，AI估算P25/平均/P75薪资
- **候选人薪资预估**：综合市场数据 + 简历质量 + 匹配度，推荐个性化薪资区间
- **可视化**：薪资区间柱状图 + 推荐范围标注

### 6. 💬 AI预面试
- **自动出题**：根据岗位要求和候选人差距生成8-12道问题
  - 技术类（3-5题）
  - 行为类（2-3题）
  - 情景类（1-2题）
  - 追问类（1-2题，针对简历薄弱点）
- **实时评分**：候选人回答后AI即时评分（1-10分）+ 反馈
- **总评**：技术/沟通/文化3维度评分 + 推荐等级

### 7. ⚙️ 系统设置
- DeepSeek API 密钥配置 + 连接测试
- 邮件SMTP配置（Phase 2）

---

## 🎨 设计系统

项目采用独立设计的视觉系统（非模板化）：

| 元素 | 方案 |
|------|------|
| **品牌名** | 人才洞察 TalentLens |
| **配色** | Obsidian `#1C1F26` 侧边栏 / Paper `#FAF8F5` 背景 / Amber `#E8A838` 强调色 / Sage `#7BAE7F` 积极状态 |
| **字体** | DM Sans（标题，几何精确感）+ Inter（正文/数据，高可读性） |
| **签名元素** | 环形评分盘（SVG仪表隐喻）+ 侧边栏Amber光晕 |

---

## 📁 项目结构

```
hr-system/
├── backend/                          # Python FastAPI 后端
│   ├── main.py                       # 应用入口（FastAPI + pywebview）
│   ├── config.py                     # 配置管理
│   ├── database.py                   # MongoDB连接
│   ├── requirements.txt              # Python依赖
│   └── app/
│       ├── __init__.py               # FastAPI应用工厂
│       ├── models/                   # Pydantic数据模型 (8个)
│       ├── routers/                  # API路由 (6个模块)
│       ├── services/                 # 业务逻辑层 (4个服务)
│       ├── ai/
│       │   ├── deepseek_client.py    # DeepSeek API封装
│       │   ├── prompts/              # Prompt模板 (6个)
│       │   └── parsers/              # AI响应解析器
│       ├── file_handlers/            # PDF/DOCX处理
│       └── utils/                    # 工具函数
├── frontend/                         # Vue 3 前端
│   ├── src/
│   │   ├── views/                    # 页面组件 (10个)
│   │   ├── components/layout/        # 布局组件
│   │   ├── router/                   # 路由配置
│   │   ├── stores/                   # Pinia状态管理
│   │   ├── types/                    # TypeScript类型
│   │   └── utils/                    # Axios封装
│   └── vite.config.ts                # Vite配置
├── data/                             # 运行时数据（简历文件）
├── scripts/                          # 构建脚本
├── packaging/                        # PyInstaller配置
├── 启动HR系统.bat                     # 一键启动脚本
└── README.md
```

---

## 🔌 API 接口

共 **21个** RESTful API 端点：

| 模块 | 端点数 | 说明 |
|------|--------|------|
| 岗位管理 | 5 | CRUD + 搜索筛选 |
| 简历管理 | 7 | 上传/列表/详情/删除/重解析/下载 |
| 匹配评分 | 5 | 单个/批量匹配 + 结果查询 |
| 薪资分析 | 2 | 市场调研 + 候选人预估 |
| AI预面试 | 5 | 启动/回答/完成/详情/列表 |
| 系统设置 | 3 | 读取/更新/测试连接 |

完整API文档：启动后端后访问 `http://127.0.0.1:8765/docs`

---

## 📊 开发进度

| 周次 | 内容 | 状态 |
|------|------|------|
| 第1周 | 基础框架 + 岗位管理 + UI骨架 | ✅ |
| 第2周 | 简历解析 + UI视觉设计系统 | ✅ |
| 第3周 | 智能匹配评分 + 薪资分析 | ✅ |
| 第4周 | AI预面试 | ✅ |
| 第5周 | 打磨 + 打包配置 + 全链路测试 | ✅ |

### Phase 2（后续迭代）
- [ ] 候选人流程追踪（Kanban看板）
- [ ] 批量处理 + 批量报告
- [ ] 数据可视化仪表盘（ECharts）
- [ ] 自动面试邀请邮件

---

## 🧪 测试

```bash
# 后端API测试（启动后端后）
cd backend
.venv\Scripts\activate
python -c "from app import create_app; app = create_app(); print('OK')"

# 前端编译测试
cd frontend
npm run build

# 全链路API测试（共12项）
# 详见 scripts/test_api.py
```

---

## 📦 打包为桌面应用

```bash
# 1. 构建前端
cd frontend && npm run build && cd ..

# 2. PyInstaller打包
pyinstaller packaging/hr_screening.spec

# 3. 输出目录
dist/HR智能简历筛选/
  └── HR智能简历筛选.exe
```

---

## 🔒 安全设计

- **API密钥本地加密**：DeepSeek密钥存储在MongoDB，启动时加载到内存
- **网络隔离**：FastAPI仅绑定 `127.0.0.1`，不暴露外部网络
- **文件验证**：上传简历校验magic bytes + 大小限制(10MB)
- **无需认证**：单机桌面应用，数据全在本地

---

## 📄 许可证

MIT License

---

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) — 高性能Python Web框架
- [Vue.js](https://vuejs.org/) — 渐进式JavaScript框架
- [pywebview](https://pywebview.flowrl.com/) — 轻量级桌面窗口库
- [DeepSeek](https://deepseek.com/) — AI大模型服务
- [MongoDB](https://www.mongodb.com/) — 文档数据库
