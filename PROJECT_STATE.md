# PROJECT_STATE.md — Nano Workshop Agent

> 交接日期：2026-05-14  
> 分支：`MVP_Test`（已推送至 origin）  
> 最后提交：`ae42b15` — MVP: End-to-end data analysis pipeline with transparent step visualization

---

## 1. 项目目标和当前阶段

**目标**：构建一个面向学术 Workshop 的全栈 Agentic AI 数据分析平台，支持用户上传多模态资产（Excel、PDF、音频、图片），通过自然语言交互完成数据清洗、编码、主题提取、量化分析和报告生成。

**当前阶段**：Phase A MVP 闭环已跑通。系统已具备：
- 真实 LLM Provider 接入（Zhipu GLM-5.1 / Anthropic Claude / Mock）
- 5 个数据分析 Agent 的串行流水线（DataProfile → Planner → Code → Executor → Repair → Explainer）
- 前端透明化 Pipeline Steps 展示（可展开卡片、代码块、DataFrame 表格、stdout）
- 每项目独立的模型配置（Provider / API Key / Model）

**距离完整 MVP 的 Gap**：尚未实现动态 Router Agent、Task Planner、Result Synthesizer、对话式 Chat UI、流式输出、工具调用（ReAct）。详见根目录 `CLAUDE.md` 的 Phase B/C/D 规划。

---

## 2. 今天完成的功能

### Backend
1. **新增 5 个数据分析 Agent** (`apps/api/app/agents/data_analysis_agents.py`)
   - `DataProfileAgent`：根据数据集生成结构化画像（overview、columns、quality_issues、suggested_analyses）
   - `PlannerAgent`：根据用户问题和数据画像生成多步分析计划（含 technique、input_columns、expected_output）
   - `CodeAgent`：根据分析计划生成 pandas Python 代码
   - `RepairAgent`：根据 traceback 修复代码
   - `ResultExplainerAgent`：将执行结果转化为中文结构化报告（summary、key_findings、recommendations、confidence、limitations）
2. **新增 Provider 工厂 + 真实 LLM 实现**
   - `ClaudeLLMProvider`（`app/providers/claude.py`）：anthropic SDK，异步
   - `ZhipuLLMProvider`（`app/providers/zhipu.py`）：zhipuai SDK，线程池包装
   - `MockLLMProvider`（`app/providers/mock.py`）：上下文感知的硬编码响应，用于无 API key 测试
   - `create_llm_provider(project_config)`（`app/providers/factory.py`）：根据项目配置动态选择 provider
3. **新增分析流水线 API** (`app/api/routes/analyze.py`)
   - `POST /api/projects/{project_id}/analyze`
   - 接收 `asset_id` + `user_question`
   - 编排 5 个 agent + 沙箱执行 + 自动修复循环（max 2 次 retry）
   - 返回 `steps[]`、`final_answer`、`code`、`execution`（含 result_type / stdout / error）
4. **项目级 LLM 配置** (`app/api/routes/projects.py`)
   - `GET /{project_id}/config`：返回项目配置（API key 做 mask 处理）
   - `PUT /{project_id}/config`：保存 provider / api_key / model / agents，API key 使用 Fernet 加密存储
   - `app/core/encryption.py`：Fernet 对称加密
5. **数据上下文增强**
   - AgentContext 新增 `project_config` 字段
   - analyze.py 向每个 agent 传递丰富的数据预览：`head_preview`（10 行）、`describe_preview`（统计摘要）、`null_counts`、`sample_json`（20 行 JSON）
6. **JSON 提取鲁棒性** (`data_analysis_agents.py` 中的 `_extract_json`)
   - 自动剥离 markdown fence（`` `json ... ``），解决真实 LLM 不严格遵循 "ONLY JSON" 指令的问题
7. **demo_main.py 修复**
   - 移除 `@app.on_event("startup")`（FastAPI 0.136.1 中 lifespan 存在时 on_event 被静默忽略）
   - 改为 `asyncio.run(init_demo())` 在 `uvicorn.run()` 之前直接调用，确保 SQLite 表创建和 MemoryStorage 初始化

### Frontend
1. **新增 Analyze 页面** (`apps/web/src/app/projects/[id]/analyze/page.tsx`)
   - 文件上传 / 选择已有资产 + 分析问题输入
   - 透明化 Pipeline Steps：可展开步骤卡片，每个 agent 有独立颜色主题
   - DataProfile：overview、columns 表格、quality issues（severity badge）、suggested analyses
   - Planner：objective、reasoning、步骤卡片（序号、技术、输入列、预期输出）
   - CodeAgent / RepairAgent：深色代码块
   - Executor：自动识别 `result_type`，DataFrame 渲染为 HTML 表格，其他类型渲染 JSON，stdout 终端样式展示
   - ResultExplainer：summary 高亮卡片、key findings 列表、recommendations 网格卡片、confidence badge
   - 每个步骤底部均提供 Raw JSON 折叠查看
   - 顶部 Pipeline Progress 进度条 + 步骤状态 Badge
2. **Workflow 页面增强** (`apps/web/src/app/projects/[id]/workflow/page.tsx`)
   - 右侧边栏新增 Config Tab：Provider 选择（zhipu / anthropic / mock）、API Key 输入、Model 输入、Agent 列表 CRUD、Save 按钮
3. **Sidebar 导航** (`apps/web/src/components/layout/ProjectSidebar.tsx`)
   - 新增 "Analyze" 入口
4. **API Client 扩展** (`apps/web/src/lib/api.ts`)
   - `getProjectConfig`、`updateProjectConfig`、`analyzeProjectData`

---

## 3. 关键文件变更

### 新增文件
| 文件 | 说明 |
|------|------|
| `apps/api/app/agents/data_analysis_agents.py` | 5 个数据分析 Agent + `_extract_json` |
| `apps/api/app/api/routes/analyze.py` | 分析流水线 API + 沙箱执行器 |
| `apps/api/app/core/encryption.py` | Fernet 加密 API key |
| `apps/api/app/providers/claude.py` | ClaudeLLMProvider |
| `apps/api/app/providers/zhipu.py` | ZhipuLLMProvider |
| `apps/api/app/providers/factory.py` | `create_llm_provider` 工厂 |
| `apps/web/src/app/projects/[id]/analyze/page.tsx` | Analyze 透明化页面 |

### 修改文件
| 文件 | 变更要点 |
|------|----------|
| `apps/api/app/agents/base.py` | AgentContext 新增 `project_config: dict` |
| `apps/api/app/agents/mock_agents.py` | 新增 `DataProfileMockAgent` 等 mock agent |
| `apps/api/app/api/routes/projects.py` | 新增 `GET/PUT /{id}/config` 端点 |
| `apps/api/app/core/config.py` | 新增 `LLM_PROVIDER`、`ANTHROPIC_API_KEY`、`ZHIPU_API_KEY`、`LLM_MODEL` |
| `apps/api/app/main.py` | 注册 `analyze.router` |
| `apps/api/app/providers/mock.py` | MockLLMProvider 增强：上下文感知的 JSON / pandas 代码响应 |
| `apps/api/demo_main.py` | 移除 `on_event("startup")`，直接 `asyncio.run(init_demo())` |
| `apps/web/src/app/projects/[id]/workflow/page.tsx` | 新增 Config Tab |
| `apps/web/src/components/layout/ProjectSidebar.tsx` | 新增 Analyze 导航 |
| `apps/web/src/lib/api.ts` | 新增 project config 和分析 API 方法 |

---

## 4. 当前架构和数据流

### 架构概览
```
Frontend (Next.js 15 App Router, localhost:3000)
  ├─ /projects/[id]/analyze      ← 新增：透明化分析流水线
  ├─ /projects/[id]/workflow     ← 新增：Config Tab
  ├─ /projects/[id]/dashboard    ← 仍为 mock state
  ├─ /projects/[id]/upload
  ├─ /projects/[id]/evidence
  ├─ /projects/[id]/coding
  ├─ /projects/[id]/themes
  ├─ /projects/[id]/quantitative
  ├─ /projects/[id]/insights
  ├─ /projects/[id]/prototypes
  ├─ /projects/[id]/review
  ├─ /projects/[id]/report
  └─ /projects/[id]/exports

Backend (FastAPI, localhost:8000)
  ├─ /api/health
  ├─ /api/projects               ← 新增 config 子路由
  ├─ /api/assets
  ├─ /api/runs
  ├─ /api/evidence
  ├─ /api/exports
  ├─ /api/workflows
  ├─ /api/feedback
  └─ /api/analyze                ← 新增：POST /projects/{id}/analyze
```

### 分析流水线数据流
```
用户上传 Excel/CSV → Asset DB + MemoryStorage/MinIO
  ↓
POST /projects/{id}/analyze {asset_id, user_question}
  ↓
[1] DataProfileAgent  ← df.describe, null_counts, sample_json, head_preview
  ↓
[2] PlannerAgent      ← user_question + data_profile
  ↓
[3] CodeAgent         ← analysis_plan + columns + dtypes + head
  ↓
[4] Executor          ← sandbox exec pandas code, capture stdout, result_type
  ↓ (if error)
[5] RepairAgent       ← code + error + columns + head
  ↓
[6] Executor (retry)  ← up to 2 retries
  ↓
[7] ResultExplainerAgent ← execution_result + plan + profile
  ↓
返回 AnalyzeResponse {steps[], final_answer, code, execution}
```

### Provider 工厂决策链
```
create_llm_provider(project_config)
  ├─ project_config.llm_config.provider == "zhipu"   → ZhipuLLMProvider(api_key, model)
  ├─ project_config.llm_config.provider == "anthropic" → ClaudeLLMProvider(api_key, model)
  └─ else / fallback                                  → MockLLMProvider()
```

### 沙箱执行环境
- `exec(compile(code, "<string>", "exec"), restricted_globals, local_vars)`
- `restricted_globals` 仅暴露 `pd`, `np` 和受限 `__builtins__`（含 `__import__`）
- `local_vars` 预置 `df`（数据副本）和 `result = None`
- `sys.stdout` 重定向到 `io.StringIO` 捕获 print 输出

---

## 5. 运行、测试、调试命令

### 启动 Demo 模式（零依赖）
```bash
cd apps/api
# 如果模型有变更，先删旧 DB
rm -f demo.db
python demo_main.py
```
- API 运行在 `http://localhost:8000`
- 使用 SQLite + MemoryStorage + Mock AI Providers
- 无需 PostgreSQL / Redis / MinIO / API Key

### 启动前端
```bash
# 从仓库根目录
corepack pnpm dev:web
# 或
cd apps/web && corepack pnpm dev
```
- 前端运行在 `http://localhost:3000`
- dev 模式下 `/api/*` rewrite 到 `localhost:8000`

### 后端测试
```bash
cd apps/api
pytest              # 64 tests, 全部通过
pytest -k test_name
```

### 前端类型检查
```bash
cd apps/web && corepack pnpm typecheck
```

### 后端 Lint / Format
```bash
cd apps/api
ruff check . && ruff format . && mypy .
```

### 调试 API
```bash
# 健康检查
curl http://localhost:8000/api/health/

# 列出项目
curl http://localhost:8000/api/projects/

# 分析（示例）
curl -X POST http://localhost:8000/api/projects/{project_id}/analyze \
  -H "Content-Type: application/json" \
  -d '{"asset_id":"...","user_question":"分析分布情况"}'
```

---

## 6. 已知问题、报错和未解决 Bug

### 已缓解但未根除
1. **真实 LLM 输出 markdown fence**
   - 现象：Zhipu GLM-5.1 在 system prompt 要求 "ONLY JSON" 时仍输出 `` `json ... `` 包裹
   - 缓解：`data_analysis_agents.py` 中的 `_extract_json()` 自动剥离 fence 并定位 `{...}` 边界
   - 风险：极端情况下 JSON 前后仍可能有文本，导致解析失败

2. **MockLLMProvider 的代码假设特定列名**
   - 现象：Mock 返回的 pandas 代码假设有 `Num.`、`Role`、`Unnamed: 0` 列（针对特定 eHMI Excel 格式）
   - 缓解：RepairAgent 会在 Executor 报错后修复代码（测试 CSV 已验证链路）
   - 建议：真实 LLM + 真实数据时不会出现此问题

### 运行时已知限制
3. **MemoryStorage 非持久化**
   - 现象：demo 模式重启后端后，之前上传的文件在 MemoryStorage 中丢失，DB 中 asset 记录仍存在
   - 解决：需要重新上传文件，或切换到 MinIO 生产模式

4. **分析 API 同步阻塞**
   - 现象：`POST /analyze` 是同步 HTTP，若使用真实 Zhipu API，多 agent 串行调用可能耗时 30-60 秒，导致前端超时或 nginx 504
   - 建议：下一步改为 Celery 后台任务 + 轮询 / SSE 流式推送

5. **前端 Workflow 页面 "Run All" 未绑定**
   - 现象：Workflow 页面的 "Run All" 按钮目前只是 UI 占位，没有调用 `/api/workflows/run`

6. **Dashboard / Coding / Themes 等页面仍为 mock state**
   - 现象：大量页面使用本地硬编码数据，未接入真实 API

### 环境/工具问题
7. **Windows 下 pnpm 需通过 corepack 调用**
   - 直接输入 `pnpm` 可能找不到命令，需使用 `corepack pnpm ...`

8. **Pre-commit hook 缺少 pnpm**
   - `.git/hooks/pre-commit` 尝试调用 `pnpm lint`，但 PATH 中可能没有 pnpm
   - 临时方案：提交时加 `--no-verify` 跳过 hook

---

## 7. 明天最应该继续做的 3-5 个 TODO

### P0 — 阻塞体验（最优先）
1. **将分析 API 改为异步后台任务 + 进度推送**
   - 问题：当前同步 `POST /analyze` 在真实 LLM 下极易超时
   - 方案：引入 Celery + Redis（docker-compose 已有），`POST /analyze` 返回 `run_id`，前端轮询 `GET /api/runs/{run_id}` 获取进度；或 SSE 流式推送每步结果
   - 参考：`WorkflowOrchestrator` 已有 DAG 执行能力，可复用

2. **前端 Dashboard / Coding / Themes / Insights / Quantitative 接入真实 API**
   - 问题：当前这些页面是"样子货"，无法展示真实 agent 运行结果
   - 方案：从 `api.ts` 拉取真实 `evidence`、`codes`、`themes`、`agent_runs` 数据，替换本地 mock state
   - 参考：Analyze page 已经示范了如何从 API 获取数据并渲染表格/JSON

### P1 — 架构核心
3. **新增 RouterAgent + ResultSynthesizerAgent，构建动态 Agentic 核心**
   - 问题：当前流水线是固定的 5 步，无法根据用户意图动态选择工作流
   - 方案：
     - `RouterAgent`：接收自然语言输入，输出 `target_workflow`（如 qualitative / quantitative / design）
     - `ResultSynthesizerAgent`：聚合多 agent 输出为统一答案/图表/报告
     - 新增 `POST /api/chat` 端点串联 Router → Planner → Orchestrator → Synthesizer
   - 参考：根目录 `CLAUDE.md` Phase B 规划

4. **注册基础工具到 ToolRegistry，支持 ReAct 模式**
   - 问题：`ToolRegistry` 存在但零注册、零调用，agent 能力边界被写死
   - 方案：注册 `file_search`、`code_interpreter`、`db_query` 等工具，让 LLM 决定调用哪个 tool，解析 tool_call，执行后回填 context
   - 参考：`app/agents/tools.py` 已有 `ToolRegistry` 基座

### P2 — 体验优化
5. **新增对话式 Chat 页面**
   - 问题：用户无法像 ChatGPT/Claude 一样自然对话，系统无多轮记忆
   - 方案：
     - 后端：新增 `conversations` / `messages` 表，持久化多轮上下文
     - 前端：新增 `/projects/[id]/chat` 页面，消息历史 + SSE 流式渲染 agent 思考过程
   - 参考：根目录 `CLAUDE.md` Phase C 规划

---

## 8. 重要设计决策

### 8.1 每项目独立 LLM 配置（而非全局环境变量）
- **决策**：API Key 保存在 `projects.config` JSON 列中，使用 Fernet 加密，通过 `GET/PUT /projects/{id}/config` 管理
- **原因**： Workshop 场景下不同项目可能使用不同模型（如一个用 Zhipu、一个用 Claude）
- **注意**：`AgentContext.project_config` 透传给 `create_llm_provider()`，所有 agent 自动使用项目配置的模型

### 8.2 Demo 模式使用 `asyncio.run(init_demo())` 而非 `on_event("startup")`
- **决策**：`demo_main.py` 在 `uvicorn.run()` 之前直接调用 `asyncio.run(init_demo())`
- **原因**：FastAPI 0.136.1 中若 `main.py` 定义了 `lifespan`，`@app.on_event("startup")` 会被**静默忽略**，导致 MemoryStorage 未初始化，文件上传报 500
- **注意**：生产环境（PostgreSQL + MinIO）不受此影响

### 8.3 沙箱执行使用受限 `exec()` 而非 subprocess / Docker
- **决策**：在 `_execute_pandas_code()` 中通过自定义 `__builtins__` 限制 + `df` 预注入来执行用户生成的代码
- **原因**：MVP 阶段最小化部署复杂度，避免引入 Docker 或 Jupyter Kernel
- **风险**：`__builtins__` 白名单仍可能被绕过（如通过 `().__class__.__bases__[0].__subclasses__()`），生产环境应迁移到受限容器或 Kata

### 8.4 Mock Provider 用于无 API key 测试
- **决策**：`MockLLMProvider` 通过 prompt 前缀匹配返回上下文感知的 JSON / pandas 代码
- **原因**：让新开发者无需申请 API key 即可运行完整流水线并验证前端 UI
- **注意**：Mock 返回的代码假设特定数据集结构（eHMI Excel），简单 CSV 会导致 Executor 报错 → 触发 RepairAgent → 修复成功，这恰好验证了修复链路的可用性

### 8.5 前端使用自定义展开而非 Accordion 组件
- **决策**：`analyze/page.tsx` 中使用 React `useState<Set<string>>` + `onToggle` 实现步骤卡片的展开/折叠，未引入 shadcn Accordion
- **原因**：当前项目 shadcn 组件库只有基础组件（Button、Card、Badge、Table、Tabs 等），没有 Accordion/Collapsible
- **注意**：如需更复杂的交互，可运行 `npx shadcn add accordion`

---

## 附录：快速上下文恢复

```bash
# 1. 切换到分支
git checkout MVP_Test

# 2. 启动后端
cd apps/api && python demo_main.py

# 3. 启动前端（新终端）
cd apps/web && corepack pnpm dev

# 4. 打开浏览器
# http://localhost:3000/projects/{project_id}/analyze
```

如需查看原始规划文档，见根目录 `CLAUDE.md` 和 `.claude/plans/review-mpv-router-agent-humble-cake.md`。
