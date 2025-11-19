**项目概览**

- **名称**: `vue-project`（仓库名: `history`）
- **说明**: 一个基于 Vue 3 + Vite 的前端学习/教学类应用，集成了 AI 聊天（DeepSeek/OpenAI 兼容接口）、Supabase 后端、课程与博物馆数据，以及丰富的页面（课程、博物馆、学习、PK、统计等）。

**快速开始**

- **安装依赖**（示例使用 `npm`）:

```
npm install
```

- **启动开发服务器**:

```
npm run dev
```

- **构建生产包**:

```
npm run build
```

- **本地预览构建产物**:

```
npm run preview
```

- **类型检查**:

```
npm run type-check
```

- **代码风格**:

```
npm run lint
npm run format
```

**关键环境变量**

项目使用 Vite 环境变量（以 `VITE_` 前缀）在构建/运行时注入：

- `VITE_DEEPSEEK_API_KEY`：DeepSeek（与 OpenAI API 兼容）的 API Key，位于 `src/services/openai.ts` 中读取并用于流式聊天。
- `VITE_SUPABASE_URL`：Supabase 实例的 URL，`src/lib/supabase.ts` 使用该值创建客户端。
- `VITE_SUPABASE_KEY`：Supabase 公共匿名 key（或服务 key，按使用场景而定）。

在 macOS / zsh 下可以创建 `.env` 或 `.env.local`（切勿提交到仓库）并包含：

```
VITE_DEEPSEEK_API_KEY=your_deepseek_api_key
VITE_SUPABASE_URL=https://xxxxx.supabase.co
VITE_SUPABASE_KEY=your_supabase_anon_key
```

**主要功能概览**

- **AI 聊天（流式）**: 使用 `src/services/openai.ts` 中的 `streamChatCompletion` 连接 DeepSeek（或 OpenAI 兼容）API，支持增量流式输出，内置系统提示为“历史知识助手”。
- **数据与认证**: 使用 Supabase（客户端在 `src/lib/supabase.ts`）做数据存取、认证与会话管理。
- **教学/历史模块**: 提供课程（`Lessons`）、课程详情、历史学习、博物馆浏览与文物详情页面。
- **社交与互动**: 支持好友/排行榜/PK 对战、徽章系统与统计视图。

**项目结构（高层）**

- `src/`：源码入口。
  - `src/main.ts`：应用入口与挂载。
  - `src/App.vue`：根组件。
  - `src/router/index.ts`：路由配置。
  - `src/stores/`：Pinia 状态管理（`user.ts`, `lesson.ts`, `friend.ts`, `counter.ts`）。
  - `src/services/`：外部 API 封装（如 `openai.ts` 用于 DeepSeek/OpenAI 兼容调用）。
  - `src/lib/`：第三方 SDK 初始化（如 `supabase.ts`）。
  - `src/composables/`：可复用逻辑（如 `useChat.ts`）。
  - `src/components/`：通用界面组件（`AIChat.vue`, `HistoryCard.vue`, `Layout.vue` 等）。
  - `src/views/`：页面组件（`Home.vue`, `Lessons.vue`, `Museums.vue`, `HistoryStudy.vue`, `PK.vue`, `Stats.vue`, `Timeline.vue` 等）。
- `public/`：静态资源。
- `supabase/`：Supabase 本地函数与配置（示例 Edge Functions 等）。

**依赖与脚本**

- 运行时依赖示例：`vue@3`, `vue-router`, `pinia`, `@supabase/supabase-js`, `openai`, `axios`, `vue3-toastify`。
- 常用脚本（见 `package.json`）:
  - `dev`：启动开发服务器
  - `build`：类型检查并构建
  - `preview`：预览构建产物
  - `type-check`：运行 `vue-tsc` 类型检查
  - `lint`：运行 ESLint
  - `format`：Prettier 格式化 `src/`

**调试与开发建议**

- 编辑器：推荐 `VS Code` + `Volar`（Vue + TypeScript 支持）
- 浏览器：推荐使用 Chromium 系并安装 `Vue.js devtools` 以便调试

**安全注意**

- 环境变量（API keys）放在本地 `.env` 或 CI secrets 中，避免提交到仓库。

**扩展建议（可选）**

- 生成 `.env.example` 列出所需环境变量模板。
- 添加单元/集成测试（`vitest` + `@vue/test-utils`）。
- 配置 CI（如 GitHub Actions）执行类型检查、lint 与构建。

---

如果你希望我现在把这个 README 提交（commit）并推送到 `dev` 分支，或者我为你生成 `.env.example`，请告诉我偏好的包管理器（`npm` / `pnpm` / `yarn`）以及是否需要我替你创建并推送 commit。

