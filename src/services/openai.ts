/**
 * DeepSeek API 服务
 * 使用 DeepSeek 官方 API，支持流式响应
 * DeepSeek API 与 OpenAI API 兼容，使用相同的格式
 */

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

export interface ChatCompletionOptions {
  model?: string
  temperature?: number
  maxTokens?: number
}

/**
 * 获取 DeepSeek API Key
 */
function getApiKey(): string {
  const apiKey = import.meta.env.VITE_DEEPSEEK_API_KEY
  if (!apiKey) {
    throw new Error('请设置 VITE_DEEPSEEK_API_KEY 环境变量')
  }
  return apiKey
}

/**
 * 检查 API 响应错误
 */
async function handleResponseError(response: Response): Promise<never> {
  const errorText = await response.text()
  let errorMessage = 'API 请求失败'

  try {
    const errorData = JSON.parse(errorText)
    errorMessage = errorData.error?.message || errorMessage

    // 处理常见的错误情况
    if (response.status === 401) {
      errorMessage = 'API Key 无效，请检查环境变量配置'
    } else if (response.status === 429) {
      errorMessage = '请求过于频繁，请稍后再试'
    } else if (response.status === 500) {
      errorMessage = 'DeepSeek 服务器错误，请稍后重试'
    }
  } catch {
    errorMessage = '服务器过于频繁，请稍后再试'
  }

  throw new Error(errorMessage)
}

/**
 * 调用 DeepSeek Chat Completions API (流式响应)
 * DeepSeek API 与 OpenAI API 格式兼容
 */
export async function* streamChatCompletion(
  messages: ChatMessage[],
  options: ChatCompletionOptions = {},
): AsyncGenerator<string, void, unknown> {
  const apiKey = getApiKey()
  const {
    model = 'deepseek-chat', // DeepSeek 的默认模型
    temperature = 0.7,
    maxTokens = 2000,
  } = options

  // 构建系统消息
  const systemMessage: ChatMessage = {
    role: 'system',
    content:
      '你是一个专业的历史知识助手，专门帮助用户学习历史知识。你是HistoriaQuest应用的AI助手，可以回答关于中国历史、世界历史、历史课程、博物馆、文物等相关问题。请用友好、专业、易懂的方式回答用户的问题。如果用户询问的问题与历史无关，你可以友好地引导用户回到历史话题。',
  }

  // 准备请求体（使用 OpenAI 兼容格式）
  const requestBody = {
    model,
    messages: [systemMessage, ...messages],
    temperature,
    max_tokens: maxTokens,
    stream: true,
  }

  try {
    // 发送请求到 DeepSeek API
    const response = await fetch('https://api.deepseek.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify(requestBody),
    })

    // 检查响应状态
    if (!response.ok) {
      await handleResponseError(response)
    }

    // 检查响应体是否存在
    if (!response.body) {
      throw new Error('无法读取响应体')
    }

    // 读取流式响应
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    try {
      while (true) {
        const { done, value } = await reader.read()

        if (done) {
          break
        }

        // 解码数据块
        buffer += decoder.decode(value, { stream: true })

        // 按行分割数据
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        // 处理每一行
        for (const line of lines) {
          const trimmedLine = line.trim()
          // 跳过空行和非数据行
          if (!trimmedLine || !trimmedLine.startsWith('data: ')) {
            continue
          }
          // 提取 JSON 数据
          const data = trimmedLine.slice(6) // 移除 'data: ' 前缀
          // 检查是否结束
          if (data === '[DONE]') {
            return
          }

          try {
            // 解析 JSON 数据
            const parsed = JSON.parse(data)

            // 提取内容（OpenAI 兼容格式）
            const delta = parsed.choices?.[0]?.delta
            const content = delta?.content

            if (content) {
              yield content
            }

            // 检查是否完成
            const finishReason = parsed.choices?.[0]?.finish_reason
            if (finishReason === 'stop') {
              return
            }
          } catch (parseError) {
            // 忽略 JSON 解析错误（可能是部分数据）
            console.warn('解析响应数据失败:', parseError)
          }
        }
      }
    } finally {
      // 确保释放 reader
      reader.releaseLock()
    }
  } catch (error) {
    // 处理网络错误
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('网络连接失败，请检查网络连接')
    }

    // 处理其他错误
    if (error instanceof Error) {
      throw error
    }

    throw new Error('请求失败，请稍后重试')
  }
}
