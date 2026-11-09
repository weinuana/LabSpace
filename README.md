# LabSpace · 智能实验室预约系统

基于 **FastAPI + LangGraph + Vue 3** 的全栈 Agent 应用，支持 SQLite 和 MySQL，包含 JWT 鉴权、
预约时段冲突检测、RAG 知识库检索与 ReAct 式 Tool Calling 工作流。

> 本项目为个人学习与实践项目，从零实现「前端 → 接口 → 数据库 → 大模型 Agent」的完整链路。

## 功能

### 已完成

- 用户登录 / 注册页面
- 管理端整体布局（顶部栏 + 侧边导航）
- 登录接口 `POST /api/auth/login`
- **密码使用 bcrypt 哈希存储**（数据库中不保存明文）
- **JWT 登录鉴权**：登录成功后签发 token，受保护接口通过 `get_current_user` 依赖校验身份
- 获取当前登录用户信息接口 `GET /api/user/me`
- 用户账号具备角色区分（`admin` 管理员 / `student` 学生）与启用状态（禁用用户无法登录）
- **统一响应格式**（`Response` 封装 `code / message / data`）与**全局异常处理**
  （业务异常、HTTP 异常、参数校验异常、未捕获异常统一拦截）
- **前端接入后端登录接口**：基于 axios 封装请求层（`utils/request.js`），
  请求拦截器自动携带 `Authorization` 头，响应拦截器统一处理业务错误与 401 失效登出
- **登录态管理**：token 与用户信息持久化到 localStorage，路由守卫拦截未登录访问
- **用户注册接口** `POST /api/auth/register`：校验账号是否重复，密码 bcrypt 哈希后入库，
  默认角色为 `student`
- **Service 业务层**：路由层只负责参数接收与响应封装，业务逻辑下沉至
  `services/auth_service.py`
- CORS 跨域配置（后端显式允许前端源）
- **文件上传接口** `POST /api/files/upload`：后缀白名单校验、大小限制（100MB）、
  UUID 重命名避免冲突、流式写入磁盘，并通过 `/uploads` 静态路由访问
- **个人信息管理**：个人中心页面支持查看与修改资料（名称 / 邮箱 / 手机号 / 头像），
  头像上传后即时预览；后端提供 `GET /api/user/me` 与 `PUT /api/user/me`，
  通过 `user_service` 实现部分字段更新（仅更新提交的字段）
- **修改密码**：`PUT /api/user/password`，校验原密码是否正确、新旧密码不得相同，
  新密码经 bcrypt 重新哈希后入库，修改成功后前端清除登录态并要求重新登录
- **用户管理**：用户列表支持分页与关键词模糊搜索（账号 / 名称），
  管理员可新增、编辑、删除用户，并设置角色（学生 / 管理员）与启用状态；
  通过 `get_current_admin` 依赖做管理员权限校验，非管理员访问返回业务码 `403`
- **实验室管理**：实验室列表支持分页与关键词模糊搜索（名称 / 位置），
  管理员可新增、编辑、删除实验室，并可设置容量、开放时段、封面图与开放状态；
  创建与重命名时校验名称唯一性（更新时排除自身）
- **菜单权限**：侧边栏「实验室管理」「设备列表管理」「用户管理」仅对 `admin` 显示，
  「实验室列表」仅对学生显示
- **设备管理**：设备列表支持分页、关键词模糊搜索（名称 / 型号）与按实验室筛选，
  管理员可新增、编辑、删除设备；设备通过外键关联所属实验室，
  列表返回时带出 `lab_name`（用 `joinedload` 预加载，避免 N+1 查询）
- **学生端实验室列表**。学生登录后可以浏览实验室和所属设备，并从列表发起预约。实验室和设备资料由管理员维护。
- **预约申请**。`POST /api/reservation` 校验预约日期、起止时间和资源状态。
  预约日期最早为当天，当天预约的开始时间须在当前时刻或之后，结束时间须晚于开始时间。
  实验室须存在且处于开放状态，预约时段须在其开放时段内。预约设备时，还会校验设备是否属于所选实验室且状态可用。
  同一实验室或同一设备在同一日期的待审核、已通过记录参与**区间重叠检测**
  （`start < 目标结束 AND end > 目标开始`），避免重复预约。
- **预约记录查询**：`GET /api/reservation/list`，支持分页与按状态筛选；
  **学生只能看到自己的预约，管理员可见全部**；返回时补全 `user_name`、
  `lab_name`、`equipment_name` 与预约类型（实验室 / 设备）
- **取消预约**：`PUT /api/reservation/{id}/cancel`，校验记录归属（只能取消自己的）
  与状态（仅「待审核」可取消），取消后状态置为「已取消」
- **预约审核**：`PUT /api/reservation/{id}/audit`（管理员），
  仅「待审核」记录可审核为「已通过」或「已拒绝」，校验状态合法性
- **预约到期处理**。后端每分钟扫描待审核的预约，将已过结束时间的申请标为「已取消」。
- **AI 智能助手**：`POST /api/ai/chat/stream`（SSE 流式），基于 LangChain 的
  `ChatOpenAI` 对接兼容 OpenAI 接口的大模型服务；用 System Prompt 约束模型
  只回答系统相关问题、不编造数据；前端用 `marked` 渲染 Markdown、
  `DOMPurify` 过滤 HTML 防 XSS
- **流式对话**：后端用 `StreamingResponse` 推送 SSE 事件
  （`status` / `tool_start` / `tool_end` / `token` / `done` / `error`），
  对话过程中实时展示工具调用进度与流式输出。前端使用 `fetch` 发送带 JWT 的 POST 请求，
  通过 `ReadableStream` 解析 SSE，缓冲 TCP 分片并校验 `Content-Type`。
- **RAG 知识库检索**：把 `backend/data/kb/*.md` 中的实验室规则文档入库，
  用 `chromadb` 持久化向量 + `BAAI/bge-small-zh-v1.5` 中文 embedding；
  检索时带相似度阈值过滤与排序，结果作为工具返回值供模型引用。[实验室规则文档](backend/data/kb/)
- **LangGraph Agent（ReAct 工作流）**：用 `StateGraph` 编排
  `agent → tools_condition → tools → agent` 的循环，`ToolNode` 自动执行工具，
  `recursion_limit=20` 限制图执行步数，`temperature=0` 降低模型采样的随机性
- **Agent 工具集**：`@tool` 定义 `search_lab_docs`（RAG 检索）、`list_open_labs`、
  `list_lab_equipments`、`create_lab_reservation`、`get_today`；
  工具内部异常以 JSON 回传模型，使其能自行修正参数后重试
- **写操作二次确认**。系统提示词要求助手先复述实验室或设备、日期和时段，取得用户明确确认后再调用预约工具。
  工具复用普通预约接口的业务校验，提交成功后进入待审核状态。

### 开发中

- 预约时段可视化（在日历中查看可用和已占用时段）
- 预约到期提醒
- AI 助手支持查询预约状态
- 接口单元测试

## 技术栈

| 层次 | 技术 |
|---|---|
| 前端 | Vue 3、Vite、Vue Router、Element Plus、Axios |
| 后端 | FastAPI、SQLAlchemy 2.0、Pydantic v2、Uvicorn |
| 认证 | PyJWT（JWT 签发与校验）、bcrypt（密码哈希） |
| AI · Agent | **LangGraph**（StateGraph / ToolNode / ReAct 工作流）、LangChain Core（`@tool` 工具定义）、LangChain OpenAI（ChatOpenAI） |
| AI · 检索 | chromadb（向量库）、sentence-transformers（bge-small-zh-v1.5 中文 embedding） |
| AI · 前端 | marked（Markdown 渲染）、DOMPurify（XSS 过滤） |
| 数据库 | SQLite（本地体验）、MySQL 8（`utf8mb4`） |
| 驱动 | PyMySQL |

## 项目结构

以下列出仓库已跟踪的目录和文件。

```text
LabSpace/                                        # 项目根目录
├── backend/                                     # FastAPI 后端
│   ├── app/                                     # 后端应用包
│   │   ├── api/                                 # HTTP 接口路由
│   │   │   ├── __init__.py                      # 汇总各模块路由，统一挂载 /api 前缀
│   │   │   ├── ai.py                            # 接收聊天请求并返回 SSE 事件流
│   │   │   ├── auth.py                          # 登录与注册接口
│   │   │   ├── equipment.py                     # 设备列表、新增、修改与删除接口
│   │   │   ├── files.py                         # 校验上传文件，保存并返回访问地址
│   │   │   ├── lab.py                           # 实验室列表、详情及管理接口
│   │   │   ├── reservation.py                   # 提交、查询、取消及审核预约的接口
│   │   │   └── user.py                          # 个人资料、修改密码及用户管理接口
│   │   ├── common/                              # 公共响应结构与异常处理
│   │   │   ├── __init__.py                      # 公共模块的包声明
│   │   │   ├── exceptions.py                    # 业务异常定义及全局异常处理器
│   │   │   └── response.py                      # 统一接口响应与分页结果模型
│   │   ├── dependencies/                        # FastAPI 依赖注入模块
│   │   │   ├── __init__.py                      # 依赖注入模块的包声明
│   │   │   └── auth.py                          # 从 JWT 获取当前用户并校验管理员权限
│   │   ├── models/                              # SQLAlchemy ORM 模型
│   │   │   ├── __init__.py                      # 数据库模型模块的包声明
│   │   │   ├── equipment.py                     # 设备表，通过外键关联所属实验室
│   │   │   ├── lab.py                           # 实验室表，记录容量、开放时段及状态
│   │   │   ├── reservation.py                   # 预约表，关联用户、实验室和可选设备
│   │   │   └── user.py                          # 用户表，保存账号、角色及状态
│   │   ├── schemas/                             # Pydantic 请求与响应模型
│   │   │   ├── __init__.py                      # 数据模型校验模块的包声明
│   │   │   ├── ai.py                            # 聊天消息与对话请求模型
│   │   │   ├── auth.py                          # 登录、注册请求及登录响应模型
│   │   │   ├── equipment.py                     # 设备新增、更新与响应模型
│   │   │   ├── files.py                         # 上传文件信息及访问地址的响应模型
│   │   │   ├── lab.py                           # 实验室新增、更新与响应模型
│   │   │   ├── reservation.py                   # 预约创建、审核与响应模型
│   │   │   └── user.py                          # 用户新增、更新、改密与响应模型
│   │   ├── services/                            # 业务逻辑与 AI 助手服务
│   │   │   ├── __init__.py                      # 业务服务模块的包声明
│   │   │   ├── agent_service.py                 # LangGraph ReAct 工作流与流式事件
│   │   │   ├── agent_tools.py                   # 知识库检索、资源查询、日期查询与预约工具
│   │   │   ├── ai_service.py                    # 早期手写工具调用循环
│   │   │   ├── auth_service.py                  # 校验登录凭据、签发 JWT 与注册账号
│   │   │   ├── equipment_service.py             # 设备分页筛选及增删改
│   │   │   ├── kb_service.py                    # 加载中文向量模型、构建 Chroma 索引并检索
│   │   │   ├── lab_service.py                   # 实验室分页、详情、增删改及名称校验
│   │   │   ├── reservation_service.py           # 预约时段校验、冲突检测、审核与到期扫描
│   │   │   └── user_service.py                  # 个人资料、密码更新及用户管理
│   │   ├── utils/                               # 通用鉴权与密码工具
│   │   │   ├── __init__.py                      # 后端工具模块的包声明
│   │   │   ├── jwt.py                           # JWT 的签发与解析
│   │   │   └── password.py                      # bcrypt 密码哈希与校验
│   │   ├── __init__.py                          # 后端应用的包声明
│   │   ├── config.py                            # 读取 .env 并定义上传目录、大小及后缀限制
│   │   ├── database.py                          # SQLAlchemy 数据库连接、会话与模型基类
│   │   └── main.py                              # 注册路由、跨域和异常处理并启动到期扫描
│   ├── data/                                    # 后端知识库数据目录
│   │   └── kb/                                  # 供 RAG 检索的 Markdown 语料
│   │       ├── 安全规范.md                      # 实验室防护、设备故障与离场规范
│   │       ├── 开放时间.md                      # 实验室工作日与周末的开放时间说明
│   │       ├── 设备使用.md                      # 设备预约要求与使用注意事项
│   │       └── 预约规则.md                      # 预约提交、审核和取消规则说明
│   ├── .env.example                             # 后端数据库、JWT 和模型服务的配置模板
│   ├── requirements.txt                         # Python 依赖及版本
│   ├── seed_demo.py                             # 初始化演示账号、实验室和设备
│   └── seed_equipment.sql                       # 补齐实验室和设备演示数据的 SQL 脚本
├── frontend/                                    # Vue 3 前端
│   ├── .vscode/                                 # VS Code 项目配置
│   │   └── extensions.json                      # 推荐安装 Vue 和 Prettier 扩展
│   ├── public/                                  # Vite 直接发布的静态资源
│   │   └── favicon.ico                          # 浏览器标签页图标
│   ├── src/                                     # 前端应用源码
│   │   ├── api/                                 # 各业务模块的 API 客户端
│   │   │   ├── ai.js                            # 携带 JWT 发起聊天请求并解析 SSE 流
│   │   │   ├── auth.js                          # 登录与注册请求
│   │   │   ├── equipment.js                     # 设备分页查询及增删改请求
│   │   │   ├── file.js                          # 用 FormData 提交上传文件
│   │   │   ├── lab.js                           # 实验室列表、详情及增删改请求
│   │   │   ├── reservation.js                   # 创建、查询、取消及审核预约的请求
│   │   │   └── user.js                          # 个人资料、修改密码及用户管理请求
│   │   ├── assets/                              # 供前端打包的样式与图片
│   │   │   ├── css/                             # 样式资源
│   │   │   │   └── global.css                   # 全局样式与主题变量
│   │   │   └── imgs/                            # 图片资源
│   │   │       └── logo.png                     # 项目 Logo 图片
│   │   ├── components/                          # 页面间复用的 Vue 组件
│   │   │   ├── AuthShowcase.vue                 # 登录与注册页共用的品牌展示区
│   │   │   └── ReserveDialog.vue                # 实验室和设备共用的预约表单弹窗
│   │   ├── layouts/                             # 页面布局组件
│   │   │   └── Layout.vue                       # 顶部栏、按角色显示的侧边导航和内容区
│   │   ├── router/                              # 前端路由模块
│   │   │   └── index.js                         # 配置页面路由与未登录访问的跳转逻辑
│   │   ├── utils/                               # 请求封装与登录状态工具
│   │   │   ├── auth.js                          # 读写本地 JWT 和用户信息，处理退出登录
│   │   │   ├── request.js                       # Axios 实例、请求鉴权与统一响应拦截
│   │   │   └── user.js                          # 响应式用户信息与本地登录状态同步
│   │   ├── views/                               # 页面级 Vue 组件
│   │   │   ├── AIChat.vue                       # 流式聊天、工具调用进度与 Markdown 渲染及 HTML 清理
│   │   │   ├── AuditReservation.vue             # 管理员按状态查看预约并审核申请
│   │   │   ├── Equipment.vue                    # 管理员分页、筛选并维护设备
│   │   │   ├── Home.vue                         # 工作台首页、数据概览与功能入口
│   │   │   ├── Lab.vue                          # 管理员搜索并维护实验室资料
│   │   │   ├── LabEquipment.vue                 # 浏览指定实验室的设备并发起预约
│   │   │   ├── LabList.vue                      # 学生浏览实验室、查看设备及预约入口
│   │   │   ├── Login.vue                        # 登录表单与登录后跳转
│   │   │   ├── MyReservation.vue                # 查询、筛选及取消个人待审核预约
│   │   │   ├── Password.vue                     # 修改密码表单与重新登录流程
│   │   │   ├── Profile.vue                      # 查看、修改个人资料并上传头像
│   │   │   ├── Register.vue                     # 新用户注册表单
│   │   │   └── User.vue                         # 管理员分页查询并维护用户与角色
│   │   ├── App.vue                              # Vue 根组件，承载页面路由出口
│   │   └── main.js                              # 注册路由、Element Plus 和全局样式并挂载应用
│   ├── .env.development                         # Vite 开发环境的 API 基础地址配置
│   ├── .gitignore                               # 前端依赖、构建产物及工具缓存的忽略规则
│   ├── .prettierrc.json                         # Prettier 代码格式配置
│   ├── index.html                               # Vite HTML 入口与 Vue 挂载节点
│   ├── jsconfig.json                            # 前端编辑器路径别名与排除目录
│   ├── package-lock.json                        # npm 依赖的解析版本锁文件
│   ├── package.json                             # 前端依赖、Node.js 版本要求及开发脚本
│   ├── README.md                                # 前端开发、安装和构建说明
│   └── vite.config.js                           # Vite 插件、路径别名与开发代理
├── .gitignore                                   # 本地配置、依赖和运行产物的 Git 忽略规则
├── jsconfig.json                                # 仓库根目录的 JavaScript 编辑器配置
└── README.md                                    # 项目说明、启动步骤与接口文档
```

本地配置和运行产物由 `.gitignore` 排除，包括 `backend/.env`、`backend/.envone`、SQLite 数据库
`backend/lab_agent.db`、上传文件目录 `backend/uploads/` 和 Chroma 持久化向量索引目录 `backend/data/chroma/`。

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 22.18+（22.x）或 24.12+
- MySQL 8.0+（选择 MySQL 时）

首次从 GitHub 获取项目时，在 PowerShell 中克隆仓库并进入项目根目录。

```powershell
git clone https://github.com/weinuana/LabSpace.git
Set-Location LabSpace
```

### 1. 准备数据库

本地体验可以使用 SQLite。首次运行时，在项目根目录从模板复制后端配置文件。已有 `backend/.env` 时，可沿用并检查其中的配置。

```powershell
Copy-Item backend/.env.example backend/.env
```

编辑 `backend/.env`，填入 SQLite 连接串和以下配置。数据库文件会在初始化演示数据或首次启动后端时创建。

```dotenv
DATABASE_URL=sqlite:///./lab_agent.db
JWT_SECRET_KEY=replace-with-your-generated-key
LLM_API_KEY=
LLM_BASE_URL=https://api.example.com/v1
LLM_MODEL=your-model
KB_WARMUP_ENABLED=false
```

运行以下命令生成 JWT 密钥，并用输出替换 `JWT_SECRET_KEY` 的占位值。

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

如需使用 MySQL 8，请先创建数据库。后端启动时会自动创建缺失的表。

```sql
CREATE DATABASE lab_agent CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

在 `.env` 中将 `DATABASE_URL` 改为 MySQL 连接串，并替换账号和密码。

```dotenv
DATABASE_URL=mysql+pymysql://YOUR_DB_USER:YOUR_DB_PASSWORD@127.0.0.1:3306/lab_agent
```

> **`.env` 配置项**。缺少必填字段时，后端会报 `ValidationError: Field required`。
>
> | 配置项 | 说明 |
> |---|---|
> | `DATABASE_URL` | SQLite 或 MySQL 连接串 |
> | `JWT_SECRET_KEY` | JWT 签名密钥，使用上方命令生成 |
> | `LLM_API_KEY` | 大模型 API 密钥。仅体验预约功能时可留空 |
> | `LLM_BASE_URL` | 兼容 OpenAI API 的模型服务地址 |
> | `LLM_MODEL` | 模型服务提供的名称，所选模型需支持工具调用 |
> | `KB_WARMUP_ENABLED` | 可选。设为 `true` 时在启动阶段预加载向量模型与索引，设为 `false` 时在首次检索时加载 |
>
> 向量模型未缓存时需要联网下载。真实的 `.env` 由 Git 忽略。[配置模板](backend/.env.example)

### 2. 启动后端

```powershell
cd backend

# 创建并激活虚拟环境
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt

# 初始化演示账号、实验室与设备（幂等，可重复执行）
python seed_demo.py

# 启动服务
uvicorn app.main:app --reload
```

> 后端使用 `from app.xxx` 形式的绝对导入，上面的命令从 `backend` 目录执行。
> 从项目根目录直接执行上面的启动命令会报 `ModuleNotFoundError: No module named 'app'`。
> 在根目录可用 `uvicorn app.main:app --reload --app-dir backend`。
> SQLite 的相对数据库路径以当前工作目录为准，从根目录启动时可将 `DATABASE_URL` 改为指向同一数据库文件的绝对路径。

后端地址为 <http://127.0.0.1:8000>。

### 3. 启动前端

另开一个 PowerShell 窗口，从项目根目录执行。

```powershell
cd frontend

npm install
npm run dev
```

前端地址为 <http://localhost:5173>。Vite 开发服务器会将 `/api` 和 `/uploads` 转发到后端。

演示账号为管理员 `admin / admin123` 和学生 `student / student123`。
体验 AI 助手时，将 `LLM_API_KEY`、`LLM_BASE_URL` 和 `LLM_MODEL` 换成模型服务提供的值。
其余预约业务可使用 SQLite 在本地运行。

## 接口文档

FastAPI 自动生成交互式文档，服务启动后访问：

- Swagger UI：<http://127.0.0.1:8000/docs>
- ReDoc：<http://127.0.0.1:8000/redoc>

### 已实现接口

| 方法 | 路径 | 说明 | 需要认证 |
|---|---|---|---|
| GET | `/` | 连通性测试 | 否 |
| POST | `/api/auth/login` | 用户登录，返回 JWT token | 否 |
| POST | `/api/auth/register` | 用户注册 | 否 |
| GET | `/api/user/me` | 获取当前登录用户信息 | **是** |
| PUT | `/api/user/me` | 修改当前用户信息 | **是** |
| PUT | `/api/user/password` | 修改密码 | **是** |
| GET | `/api/user/list` | 用户列表（分页 + 关键词搜索） | **是（管理员）** |
| POST | `/api/user` | 新增用户 | **是（管理员）** |
| PUT | `/api/user/{user_id}` | 更新指定用户 | **是（管理员）** |
| DELETE | `/api/user/{user_id}` | 删除指定用户 | **是（管理员）** |
| GET | `/api/lab/list` | 实验室列表（分页 + 关键词搜索） | **是** |
| GET | `/api/lab/{lab_id}` | 查看指定实验室详情 | **是** |
| POST | `/api/lab` | 新增实验室 | **是（管理员）** |
| PUT | `/api/lab/{lab_id}` | 更新指定实验室 | **是（管理员）** |
| DELETE | `/api/lab/{lab_id}` | 删除指定实验室 | **是（管理员）** |
| GET | `/api/equipment/list` | 设备列表（分页 + 关键词 + 实验室筛选） | **是** |
| POST | `/api/equipment` | 新增设备 | **是（管理员）** |
| PUT | `/api/equipment/{equipment_id}` | 更新指定设备 | **是（管理员）** |
| DELETE | `/api/equipment/{equipment_id}` | 删除指定设备 | **是（管理员）** |
| POST | `/api/reservation` | 创建预约（含时段冲突检测） | **是** |
| GET | `/api/reservation/list` | 预约列表（学生看自己，管理员看全部） | **是** |
| PUT | `/api/reservation/{reservation_id}/cancel` | 取消预约 | **是** |
| PUT | `/api/reservation/{reservation_id}/audit` | 审核预约（通过 / 拒绝） | **是（管理员）** |
| POST | `/api/ai/chat/stream` | AI 对话（SSE 流式） | **是** |
| POST | `/api/files/upload` | 文件上传 | 否 |

### 登录

**请求**

```json
{
  "username": "admin",
  "password": "admin123"
}
```

**成功响应**

```json
{
  "code": 200,
  "message": "登陆成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "username": "admin",
      "name": "系统管理员",
      "role": "admin",
      "phone": null,
      "email": null,
      "avatar": null,
      "status": 1
    }
  }
}
```

**失败响应**（账号或密码错误）

```json
{
  "code": 500,
  "message": "账号或密码错误",
  "data": null
}
```

### 携带 token 访问受保护接口

在请求头中加入 `Authorization` 字段：

```
Authorization: Bearer <登录返回的 token>
```

示例：

```powershell
curl.exe http://127.0.0.1:8000/api/user/me -H "Authorization: Bearer 你的token"
```

token 有效期默认 24 小时（由 `.env` 的 `JWT_EXPIRE_HOURS` 控制），过期后需重新登录。

## 开发说明

### 数据库表结构

表由 SQLAlchemy 在应用启动时自动创建（`Base.metadata.create_all`），
新增模型后需要在 `app/main.py` 中导入，否则不会被创建。

所有表继承自 `app/database.py` 的 `Base`，默认包含三个公共字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | int | 主键，自增 |
| `create_time` | datetime | 创建时间 |
| `update_time` | datetime | 更新时间（自动更新） |

`users` 表字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| `username` | varchar(50) | 账号，非空 |
| `password` | varchar(255) | bcrypt 哈希值，非空 |
| `name` | varchar(50) | 姓名，非空 |
| `role` | varchar(50) | 角色：`student` / `admin`，非空 |
| `email` | varchar(50) | 邮箱，可空 |
| `phone` | varchar(50) | 手机号，可空 |
| `avatar` | varchar(50) | 头像，可空 |
| `status` | int | 状态：`0` 禁用、`1` 正常 |

> `create_all` 负责创建缺失的表。已有表的字段变更需要通过数据库迁移或 `ALTER TABLE` 应用。

### 认证流程

```
POST /api/auth/login
        │  校验账号密码（bcrypt.checkpw）
        ▼
   签发 JWT（payload 含 user_id、exp）
        │  返回给前端
        ▼
前端后续请求携带 Authorization: Bearer <token>
        │
        ▼
get_current_user 依赖：解析 token → 查询用户 → 校验 status
        │
        ▼
    注入到接口函数的 current_user 参数
```

## 已知待改进项

### 后端 / 安全

- [ ] `users.username` 增加唯一约束，避免出现同名账号
- [ ] `verify_password` 增加异常兜底，兼容非 bcrypt 格式的历史数据
- [ ] `get_current_user` 在用户不存在时返回 401 而非抛 500
- [ ] 登录失败使用对应的 HTTP 401/403 状态码（当前返回 HTTP 200 和业务码 `500`）
- [ ] 为 bcrypt 的密码输入增加 72 字节上限校验

### AI / Agent

- [ ] Agent 会话持久化（LangGraph checkpointer），支持上下文跨请求保留
- [ ] 补充 Agent 工具的单元测试（工具参数解析、异常回传）
- [ ] 清理旧版 `ai_service.py`（现由 LangGraph 实现替代，保留供方案对比）

### 通用

- [ ] 补充接口单元测试
- [ ] 引入 Alembic 管理数据库迁移（当前使用 `create_all` 创建缺失的表）

## License

仅供学习交流使用。
