# HistoriaQuest - 软件工程综合实践项目

## 🎯 项目信息

- **组号**：8组
- **学生**：何俊阳 (202530495236)
- **学生**：危颖龙 (202530495234)
- **课程**：《软件工程综合实践》
- **技术栈**：Vue3 (前端) + FastAPI (后端) + Supabase/PostgreSQL (数据库)
- **项目周期**：[2025-11-11] - [2025-12-12]

## 📖 项目简介

HistoriaQuest 是一个基于 AI 的历史知识学习平台，提供以下核心功能：

- **AI 历史助手**：基于 DeepSeek/OpenAI API 的流式对话，扮演历史人物进行互动
- **课程学习系统**：结构化的历史课程与学习进度追踪
- **博物馆浏览**：虚拟博物馆与文物详情展示
- **社交互动**：好友系统、排行榜、知识 PK 对战
- **徽章与统计**：学习成就系统与数据可视化

## 🚀 快速启动 (评审老师请看这里)

我们提供了两种方式快速运行本项目：

### 方式一：使用 Docker Compose (推荐)

**前提**：确保本地已安装 [Docker](https://www.docker.com/) 和 Docker Compose。

```bash
# 1. 克隆或解压项目
git clone [仓库地址]

# 2. 进入项目根目录
cd vue-project

# 3. 配置后端环境变量
cp backend/.env.example backend/.env
# 编辑 backend/.env 填入必要的 API Key

# 4. 一键启动所有服务 (前端、后端)
docker-compose up -d --build

# 5. 查看服务状态
docker-compose ps

# 6. 查看日志（可选）
docker-compose logs -f
```

**访问地址**：
| 服务 | 地址 | 说明 |
|------|------|------|
| 前端 | http://localhost:3000 | Vue3 应用 |
| 后端 API | http://localhost:8000 | FastAPI 服务 |
| API 文档 | http://localhost:8000/docs | Swagger UI |
| 健康检查 | http://localhost:8000/api/health | 服务状态 |

**停止服务**：
```bash
docker-compose down
```

### 方式二：手动启动 (开发环境)

#### 1. 启动后端

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入必要配置

# 启动服务
uvicorn app.main:app --reload --port 8000
```

#### 2. 启动前端

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 配置环境变量（可选，开发环境已有默认值）
# 创建 .env.local 文件

# 启动开发服务器
npm run dev
```

**访问地址**：
- 前端：http://localhost:5173
- 后端：http://localhost:8000

## 📁 项目结构

```
vue-project/
├── frontend/                    # Vue3 前端项目
│   ├── public/                  # 静态资源
│   │   └── images/              # 图片资源
│   ├── src/
│   │   ├── components/          # 通用组件 (AIChat, Layout, HistoryCard 等)
│   │   ├── composables/         # 可复用逻辑 (useChat 等)
│   │   ├── data/                # 静态数据 (课程、博物馆数据)
│   │   ├── lib/                 # 第三方 SDK 初始化 (Supabase)
│   │   ├── router/              # Vue Router 路由配置
│   │   ├── services/            # API 服务封装 (OpenAI, API 调用)
│   │   ├── stores/              # Pinia 状态管理
│   │   ├── views/               # 页面组件
│   │   ├── App.vue              # 根组件
│   │   └── main.ts              # 应用入口
│   ├── Dockerfile               # 前端 Docker 构建文件
│   ├── nginx.conf               # Nginx 配置 (生产环境)
│   ├── package.json             # 前端依赖配置
│   └── vite.config.ts           # Vite 构建配置
│
├── backend/                     # FastAPI 后端项目
│   ├── app/
│   │   ├── models/              # 数据模型
│   │   ├── routers/             # API 路由
│   │   ├── schemas/             # Pydantic 数据验证
│   │   ├── services/            # 业务逻辑服务
│   │   ├── utils/               # 工具函数
│   │   ├── config.py            # 配置管理
│   │   ├── database.py          # 数据库连接
│   │   └── main.py              # 应用入口
│   ├── Dockerfile               # 后端 Docker 构建文件
│   └── requirements.txt         # Python 依赖清单
│
├── database/                    # 数据库相关
│   ├── supabase/                # Supabase 配置与函数
│   ├── schema.sql               # 数据库建表 SQL 脚本
│   └── dummy_data.sql           # 模拟数据脚本
│
├── docs/                        # 项目文档
│   ├── DATABASE_SCHEMA.md       # 数据库设计文档
│   ├── SUPABASE_SETUP.md        # Supabase 配置指南
│   ├── DEEPSEEK_SETUP.md        # DeepSeek API 配置
│   └── CHATGPT_SETUP.md         # ChatGPT 配置说明
│
├── tests/                       # 测试用例
│   ├── frontend/                # 前端测试
│   └── backend/                 # 后端测试
│
├── docker-compose.yml           # Docker 编排配置
├── .gitignore                   # Git 忽略配置
└── package.json                 # 根项目脚本
```

## 🛠 技术架构说明

### 前端 (Vue3)

| 技术 | 说明 |
|------|------|
| **构建工具** | Vite 7 |
| **核心框架** | Vue 3 + Composition API + `<script setup>` |
| **状态管理** | Pinia |
| **路由** | Vue Router 4 (History 模式) |
| **HTTP 客户端** | Axios |
| **UI 样式** | TailwindCSS |
| **AI 集成** | OpenAI SDK (兼容 DeepSeek API) |
| **类型检查** | TypeScript + vue-tsc |
| **代码规范** | ESLint + Prettier |

### 后端 (FastAPI)

| 技术 | 说明 |
|------|------|
| **Web 框架** | FastAPI |
| **ASGI 服务器** | Uvicorn |
| **数据库 ORM** | SQLAlchemy 2.0 (异步) |
| **数据验证** | Pydantic v2 |
| **身份认证** | Supabase Auth + JWT |
| **AI 服务** | OpenAI SDK |
| **API 文档** | 自动生成 Swagger UI |

### 数据库 (Supabase/PostgreSQL)

| 特性 | 说明 |
|------|------|
| **数据库** | PostgreSQL (Supabase 托管) |
| **认证** | Supabase Auth |
| **安全** | Row Level Security (RLS) |
| **ER 图** | 见 [docs/DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) |

### Docker 部署架构

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                        │
│                  (historia-network)                      │
│                                                          │
│  ┌──────────────────┐      ┌──────────────────┐         │
│  │    frontend      │      │     backend      │         │
│  │  (historia-web)  │      │  (historia-api)  │         │
│  │                  │      │                  │         │
│  │  Nginx + Vue     │─────▶│  FastAPI +       │         │
│  │  Port: 3000:80   │ /api │  Uvicorn         │         │
│  │                  │      │  Port: 8000      │         │
│  └──────────────────┘      └──────────────────┘         │
│                                     │                    │
└─────────────────────────────────────│────────────────────┘
                                      │
                                      ▼
                            ┌──────────────────┐
                            │    Supabase      │
                            │   (Cloud DB)     │
                            └──────────────────┘
```

### Nginx 配置说明

前端 Nginx 配置 (`frontend/nginx.conf`) 包含以下关键特性：

- **API 代理**：`/api` 路径代理到后端服务
- **Vue Router 支持**：History 模式回退到 `index.html`
- **Gzip 压缩**：优化静态资源传输
- **静态资源缓存**：`/assets` 目录设置 1 年缓存
- **SSE 流式支持**：禁用代理缓冲，支持 AI 流式响应
- **安全头**：X-Frame-Options, X-Content-Type-Options, X-XSS-Protection

## 🔧 开发环境搭建

### 前置要求

- Node.js >= 20.19.0
- Python >= 3.11
- Docker & Docker Compose (可选)

### 环境变量配置

**前端 (`frontend/.env.local`)**：
```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_KEY=your-supabase-anon-key
VITE_DEEPSEEK_API_KEY=your-deepseek-api-key
```

**后端 (`backend/.env`)**：
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-service-key
OPENAI_API_KEY=your-openai-or-deepseek-key
OPENAI_BASE_URL=https://api.deepseek.com/v1
```

### 数据库初始化

```bash
# 在 Supabase SQL Editor 中执行
# 1. 执行建表脚本
database/schema.sql

# 2. 插入测试数据（可选）
database/dummy_data.sql
```

## 📡 API 接口

- **在线文档**：http://localhost:8000/docs (Swagger UI)
- **ReDoc 文档**：http://localhost:8000/redoc
- **基础 URL**：`http://localhost:8000/api`

### 主要接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| POST | `/api/chat` | AI 对话（流式） |
| GET | `/api/lessons` | 获取课程列表 |
| GET | `/api/progress` | 获取学习进度 |
| POST | `/api/progress` | 更新学习进度 |

## 🧪 测试

```bash
# 前端测试
cd frontend && npm run test:unit

# 后端测试
cd backend && python -m pytest tests/

# 类型检查
cd frontend && npm run type-check

# 代码规范检查
cd frontend && npm run lint
```

## 📈 项目亮点

1. **工程化**：完整的前后端分离架构，Docker 一键部署，规范的 Git 工作流
2. **技术深度**：
   - Vue3 Composition API + TypeScript 实现响应式数据流
   - FastAPI 异步框架 + SQLAlchemy 2.0 异步 ORM
   - AI 流式对话（SSE）实现实时响应
3. **用户体验**：
   - TailwindCSS 响应式设计
   - 流式 AI 对话，打字机效果
   - 完善的加载状态与错误处理
4. **代码质量**：
   - TypeScript 类型安全
   - ESLint + Prettier 代码规范
   - Pydantic 数据验证

## 📝 问题与解决

| 问题 | 解决方案 |
|------|----------|
| **跨域问题** | 后端配置 CORS 中间件，生产环境通过 Nginx 代理 |
| **前端路由刷新 404** | Nginx 配置 `try_files $uri $uri/ /index.html` |
| **AI 流式响应** | Nginx 配置 `proxy_buffering off` 禁用缓冲 |
| **环境变量注入** | Docker 构建时通过 ARG 注入 VITE 环境变量 |

## 🎥 演示与截图

- **演示视频**：[docs/演示视频.mp4](docs/History.mp4)
- **在线演示**：https://hjy.dmmcloud.com (如已部署)

### 系统截图

| 首页 | AI 对话 |
|------|---------|
| ![首页](docs/screenshots/home.png) | ![AI对话](docs/screenshots/chat.png) |

| 课程学习 | 博物馆 |
|----------|--------|
| ![课程](docs/screenshots/lessons.png) | ![博物馆](docs/screenshots/museum.png) |

## 📄 文档清单

- [数据库设计文档](docs/DATABASE_SCHEMA.md)
- [Supabase 配置指南](docs/SUPABASE_SETUP.md)
- [DeepSeek API 配置](docs/DEEPSEEK_SETUP.md)
- [ChatGPT 配置说明](docs/CHATGPT_SETUP.md)

## 📜 开源协议

本项目仅用于教学目的，版权归作者所有。
