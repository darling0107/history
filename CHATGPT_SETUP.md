# DeepSeek API 配置说明

> **注意**：本项目已迁移到 DeepSeek API。DeepSeek API 支持国内访问，无需代理，价格更实惠。

## 设置步骤

1. **创建 `.env` 文件**

   在项目根目录创建 `.env` 文件，添加以下内容：

   ```
   VITE_DEEPSEEK_API_KEY=your_deepseek_api_key_here
   ```

2. **获取 DeepSeek API Key**
   - 访问 [DeepSeek 开放平台](https://platform.deepseek.com/)
   - 登录或注册账号
   - 进入 [API Keys](https://platform.deepseek.com/api_keys) 页面
   - 创建新的 API Key
   - 将 API Key 复制到 `.env` 文件中

3. **重启开发服务器**

   配置环境变量后，需要重启 Vite 开发服务器：

   ```bash
   npm run dev
   ```

## 功能特性

- ✅ **流式响应**：实现类似 ChatGPT 的打字机效果
- ✅ **对话历史**：保留最近10条消息上下文
- ✅ **错误处理**：友好的错误提示，包括网络错误、API错误等
- ✅ **自动滚动**：消息自动滚动到底部
- ✅ **类型安全**：完整的 TypeScript 类型支持
- ✅ **最新模型**：使用最新的 DeepSeek Chat 模型（快速且经济）
- ✅ **国内访问**：DeepSeek API 支持国内访问，无需代理

## API 使用方法

### 流式响应（推荐）

```typescript
import { streamChatCompletion, type ChatMessage } from '@/services/openai'

const messages: ChatMessage[] = [{ role: 'user', content: '你好' }]

// 使用默认配置（deepseek-chat）
for await (const chunk of streamChatCompletion(messages)) {
  console.log(chunk) // 输出每个文本块
}

// 使用自定义配置
const options = {
  model: 'deepseek-chat-v2',
  temperature: 0.7,
  maxTokens: 2000,
}

for await (const chunk of streamChatCompletion(messages, options)) {
  console.log(chunk)
}
```

### 非流式响应

```typescript
import { chatCompletion, type ChatMessage } from '@/services/openai'

const messages: ChatMessage[] = [{ role: 'user', content: '你好' }]

const response = await chatCompletion(messages)
console.log(response) // 完整的回复内容
```

## 可用模型

| 模型               | 名称             | 描述                            | 成本 |
| ------------------ | ---------------- | ------------------------------- | ---- |
| `deepseek-chat`    | DeepSeek Chat    | DeepSeek 的标准对话模型（推荐） | 低   |
| `deepseek-chat-v2` | DeepSeek Chat V2 | DeepSeek 的升级版对话模型       | 中   |
| `deepseek-coder`   | DeepSeek Coder   | DeepSeek 的代码生成模型         | 低   |

## 配置选项

```typescript
interface ChatCompletionOptions {
  model?: string // 模型名称，默认 'deepseek-chat'
  temperature?: number // 温度参数，默认 0.7 (0-2)
  maxTokens?: number // 最大token数，默认 2000
}
```

## 错误处理

API 服务会自动处理以下错误：

- **401 错误**：API Key 无效，请检查环境变量配置
- **429 错误**：请求过于频繁，请稍后再试
- **500 错误**：DeepSeek 服务器错误，请稍后重试
- **网络错误**：无法连接到 DeepSeek API，请检查网络连接
- **其他错误**：显示具体的错误消息

## DeepSeek 优势

1. **国内访问**：DeepSeek API 支持国内访问，无需配置代理或 VPN
2. **价格实惠**：相比 OpenAI，DeepSeek 的价格更加实惠
3. **性能优秀**：DeepSeek Chat 模型性能优秀，响应速度快
4. **API 兼容**：DeepSeek API 与 OpenAI API 格式兼容，易于迁移

## 网络问题解决

DeepSeek API 支持国内访问，通常不会遇到网络问题。如果遇到连接问题：

1. **检查网络连接**：确保网络连接正常
2. **检查 API Key**：确保 API Key 配置正确
3. **查看错误信息**：查看具体的错误信息，根据错误信息进行排查

## 最佳实践

1. **使用流式响应**：可以节省 token 并提升用户体验
2. **限制对话历史**：只保留最近的对话，避免 token 过多
3. **处理错误**：始终处理可能的错误情况
4. **使用合适的模型**：根据需求选择合适的模型（推荐使用 deepseek-chat）
5. **监控使用量**：定期检查 API 使用量，避免超出预算

## 注意事项

- `.env` 文件已添加到 `.gitignore`，不会被提交到版本控制
- API Key 请妥善保管，不要泄露
- 使用流式响应可以节省 token 并提升用户体验
- 默认使用 `deepseek-chat` 模型，可以在代码中修改
- API 的使用可能涉及费用，建议在使用前查看 DeepSeek 的定价策略
- DeepSeek API 支持国内访问，无需配置代理

## 更新日志

### 2024-12-XX

- ✅ 迁移到 DeepSeek API
- ✅ 使用最新的 DeepSeek Chat 模型（默认）
- ✅ 改进错误处理，提供更友好的错误提示
- ✅ 添加完整的 TypeScript 类型支持
- ✅ 优化流式响应处理
- ✅ 添加非流式响应支持
- ✅ 支持国内访问，无需代理

## 迁移说明

如果你之前使用的是 OpenAI API，迁移到 DeepSeek API 非常简单：

1. **更新环境变量**：将 `VITE_OPENAI_API_KEY` 改为 `VITE_DEEPSEEK_API_KEY`
2. **更新 API Key**：使用 DeepSeek 的 API Key 替换 OpenAI 的 API Key
3. **更新模型名称**：将模型名称从 `gpt-4o-mini` 改为 `deepseek-chat`
4. **无需修改代码**：代码无需修改，因为 DeepSeek API 与 OpenAI API 格式兼容
