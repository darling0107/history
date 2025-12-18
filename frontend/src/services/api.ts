/**
 * API 服务配置
 * 用于连接 Python FastAPI 后端
 */
import axios from 'axios'

// API 基础 URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

// 创建 axios 实例
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器 - 添加 Supabase Token
api.interceptors.request.use(
  (config) => {
    // 从 localStorage 获取 Supabase session
    const sessionStr = localStorage.getItem('supabase.auth.token')
    if (sessionStr) {
      try {
        const session = JSON.parse(sessionStr)
        if (session?.currentSession?.access_token) {
          config.headers.Authorization = `Bearer ${session.currentSession.access_token}`
        }
      } catch (e) {
        console.error('Failed to parse session:', e)
      }
    }

    // 尝试从 supabase-js 的存储格式获取
    const keys = Object.keys(localStorage)
    for (const key of keys) {
      if (key.startsWith('sb-') && key.endsWith('-auth-token')) {
        try {
          const data = JSON.parse(localStorage.getItem(key) || '{}')
          if (data?.access_token) {
            config.headers.Authorization = `Bearer ${data.access_token}`
            break
          }
        } catch (e) {
          console.error('Failed to parse session:', e)
        }
      }
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

// 响应拦截器 - 处理错误
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token 过期或无效，可以触发重新登录
      console.warn('Unauthorized - Token may be expired')
    }
    return Promise.reject(error)
  },
)

export default api

// ============ 用户相关 API ============
export const userApi = {
  // 获取当前用户信息
  getMe: () => api.get('/users/me'),

  // 更新用户信息
  updateMe: (data: { username?: string; avatar_url?: string }) =>
    api.put('/users/me', null, { params: data }),

  // 获取学习统计
  getStats: () => api.get('/users/me/stats'),

  // 添加学习时长
  addStudyTime: (minutes: number) =>
    api.post('/users/me/study-time', null, { params: { minutes } }),
}

// ============ 课程相关 API ============
export const lessonApi = {
  // 获取所有课程
  getAll: () => api.get('/lessons'),

  // 获取单个课程
  getById: (id: string) => api.get(`/lessons/${id}`),

  // 获取所有进度
  getAllProgress: () => api.get('/lessons/progress/all'),

  // 获取单个课程进度
  getProgress: (lessonId: string) => api.get(`/lessons/progress/${lessonId}`),

  // 完成课程
  complete: (data: {
    lesson_id: string
    correct_count: number
    total_count: number
    score: number
  }) => api.post('/lessons/complete', data),

  // 提交答案
  submitAnswer: (data: { lesson_id: string; question_id: string; answer: number }) =>
    api.post('/lessons/submit-answer', data),
}

// ============ AI 聊天相关 API ============
export const chatApi = {
  // 流式聊天（返回 EventSource URL）
  getStreamUrl: () => `${API_BASE_URL}/chat/stream`,

  // 流式聊天
  stream: async function* (
    messages: Array<{ role: string; content: string }>,
    options: { temperature?: number; max_tokens?: number } = {},
  ) {
    const response = await fetch(`${API_BASE_URL}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: api.defaults.headers.common['Authorization'] as string,
      },
      body: JSON.stringify({
        messages,
        temperature: options.temperature || 0.7,
        max_tokens: options.max_tokens || 2000,
      }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body?.getReader()
    if (!reader) return

    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          if (data === '[DONE]') return
          try {
            const parsed = JSON.parse(data)
            if (parsed.content) {
              yield parsed.content
            }
            if (parsed.error) {
              throw new Error(parsed.error)
            }
          } catch (e) {
            console.error('Failed to parse response:', e)
          }
        }
      }
    }
  },

  // 非流式聊天
  complete: (messages: Array<{ role: string; content: string }>) =>
    api.post('/chat/complete', { messages }),

  // 获取聊天历史
  getHistory: () => api.get('/chat/history'),

  // 保存聊天历史
  saveHistory: (messages: Array<{ role: string; content: string }>) =>
    api.post('/chat/history/save', messages),

  // 清空聊天历史
  clearHistory: () => api.delete('/chat/history'),
}

// ============ 历史人物相关 API ============
export const figureApi = {
  // 获取所有历史人物
  getAll: () => api.get('/figures'),

  // 获取单个历史人物
  getById: (id: string) => api.get(`/figures/${id}`),

  // 与历史人物流式对话
  stream: async function* (
    figureId: string,
    messages: Array<{ role: string; content: string }>,
    options: { temperature?: number; max_tokens?: number } = {},
  ) {
    const response = await fetch(`${API_BASE_URL}/figures/${figureId}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: api.defaults.headers.common['Authorization'] as string,
      },
      body: JSON.stringify({
        messages,
        temperature: options.temperature || 0.7,
        max_tokens: options.max_tokens || 2000,
      }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body?.getReader()
    if (!reader) return

    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          if (data === '[DONE]') return
          try {
            const parsed = JSON.parse(data)
            if (parsed.content) {
              yield parsed.content
            }
            if (parsed.error) {
              throw new Error(parsed.error)
            }
          } catch (e) {
            console.error('Failed to parse response:', e)
          }
        }
      }
    }
  },

  // 获取与人物的聊天历史
  getHistory: (figureId: string) => api.get(`/figures/${figureId}/history`),

  // 保存聊天历史
  saveHistory: (figureId: string, messages: Array<{ role: string; content: string }>) =>
    api.post(`/figures/${figureId}/history/save`, messages),

  // 清空聊天历史
  clearHistory: (figureId: string) => api.delete(`/figures/${figureId}/history`),
}

// ============ 社交相关 API ============
export const socialApi = {
  // 获取好友列表
  getFriends: () => api.get('/social/friends'),

  // 发送好友请求
  sendFriendRequest: (friendId: string) =>
    api.post('/social/friends/request', { friend_id: friendId }),

  // 获取好友请求
  getFriendRequests: () => api.get('/social/friends/requests'),

  // 接受好友请求
  acceptFriendRequest: (requestId: string) => api.post(`/social/friends/accept/${requestId}`),

  // 删除好友
  removeFriend: (friendId: string) => api.delete(`/social/friends/${friendId}`),

  // 开始 PK
  startPK: (opponentId: string) => api.post('/social/pk/start', { opponent_id: opponentId }),

  // 提交 PK 答案
  submitPKAnswer: (matchId: string, questionIndex: number, answer: number) =>
    api.post('/social/pk/answer', {
      match_id: matchId,
      question_index: questionIndex,
      answer,
    }),

  // 结束 PK
  finishPK: (matchId: string) => api.post(`/social/pk/${matchId}/finish`),

  // 获取 PK 历史
  getPKHistory: () => api.get('/social/pk/history'),
}
