<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { streamChatCompletion, type ChatMessage } from '@/services/openai'

const isOpen = defineModel<boolean>('isOpen', { default: false })

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

const messages = ref<Message[]>([
  {
    id: '1',
    role: 'assistant',
    content: '你好！我是HistoriaQuest的AI助手，可以帮助你解答历史相关的问题。有什么想了解的吗？',
    timestamp: new Date(),
  },
])

const inputMessage = ref('')
const isLoading = ref(false)
const messageContainer = ref<HTMLElement>()
const errorMessage = ref('')

const sendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return

  const userMessage = {
    id: Date.now().toString(),
    role: 'user' as const,
    content: inputMessage.value.trim(),
    timestamp: new Date(),
  }

  messages.value.push(userMessage)
  inputMessage.value = ''
  isLoading.value = true
  errorMessage.value = ''

  // 滚动到底部
  await nextTick()
  scrollToBottom()

  // 创建AI回复消息（初始为空，流式更新）
  const aiMessageId = (Date.now() + 1).toString()
  const aiMessage = {
    id: aiMessageId,
    role: 'assistant' as const,
    content: '',
    timestamp: new Date(),
  }
  messages.value.push(aiMessage)

  try {
    // 准备消息历史（只保留最近的对话，避免token过多）
    // 排除系统消息和空的AI消息（包括刚创建的空的AI消息）
    const conversationMessages: ChatMessage[] = messages.value
      .filter((msg) => msg.id !== aiMessageId && msg.content.trim()) // 排除空的AI消息和其他空消息
      .slice(-10) // 只保留最近10条消息
      .map((msg) => ({
        role: msg.role,
        content: msg.content,
      }))

    // 使用 DeepSeek API 配置（使用 deepseek-chat 模型，快速且经济）
    const options = {
      model: 'deepseek-chat',
      temperature: 0.7,
      maxTokens: 2000,
    }

    // 流式获取AI回复
    let fullContent = ''
    for await (const chunk of streamChatCompletion(conversationMessages, options)) {
      fullContent += chunk

      // 更新AI消息内容
      const messageIndex = messages.value.findIndex((m) => m.id === aiMessageId)
      if (messageIndex > -1 && messages.value[messageIndex]) {
        messages.value[messageIndex].content = fullContent
      }

      // 自动滚动到底部（节流处理，避免频繁滚动）
      await nextTick()
      scrollToBottom()
    }

    // 确保最终内容已更新
    const finalMessageIndex = messages.value.findIndex((m) => m.id === aiMessageId)
    if (finalMessageIndex > -1 && messages.value[finalMessageIndex]) {
      messages.value[finalMessageIndex].content = fullContent
    }

    isLoading.value = false
    errorMessage.value = ''
  } catch (error) {
    console.error('DeepSeek API error:', error)

    // 提供更友好的错误提示
    if (error instanceof Error) {
      errorMessage.value = error.message
    } else {
      errorMessage.value = '请求失败，请稍后重试'
    }

    // 移除空的AI消息
    const messageIndex = messages.value.findIndex((m) => m.id === aiMessageId)
    if (messageIndex > -1 && messages.value[messageIndex]?.content === '') {
      messages.value.splice(messageIndex, 1)
    }

    isLoading.value = false

    // 滚动到底部以显示错误消息
    await nextTick()
    scrollToBottom()
  }
}

const scrollToBottom = () => {
  if (messageContainer.value) {
    messageContainer.value.scrollTop = messageContainer.value.scrollHeight
  }
}

const formatTime = (date: Date) => {
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}
</script>

<template>
  <div
    v-if="isOpen"
    class="fixed bottom-20 left-4 z-50 w-96 max-w-[calc(100vw-2rem)] h-[600px] max-h-[calc(100vh-6rem)] flex flex-col bg-white rounded-2xl shadow-2xl border border-gray-200 overflow-hidden"
  >
    <!-- 头部 -->
    <div
      class="bg-gradient-to-r from-amber-500 to-orange-500 text-white p-4 flex items-center justify-between"
    >
      <div class="flex items-center gap-2">
        <div class="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
          <span class="text-xl">🤖</span>
        </div>
        <div>
          <h3 class="font-bold text-lg">AI 历史助手</h3>
          <p class="text-xs text-white/90">随时为你解答历史问题</p>
        </div>
      </div>
      <button
        @click="isOpen = false"
        class="w-8 h-8 rounded-full bg-white/20 hover:bg-white/30 flex items-center justify-center transition-colors"
      >
        <span class="text-lg">×</span>
      </button>
    </div>

    <!-- 消息列表 -->
    <div ref="messageContainer" class="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
      <div
        v-for="message in messages"
        :key="message.id"
        class="flex"
        :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
      >
        <div
          :class="[
            'max-w-[80%] rounded-2xl px-4 py-3',
            message.role === 'user'
              ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-white'
              : 'bg-white text-gray-800 shadow-sm border border-gray-200',
          ]"
        >
          <p class="text-sm leading-relaxed whitespace-pre-wrap">{{ message.content }}</p>
          <p :class="['text-xs mt-1', message.role === 'user' ? 'text-white/70' : 'text-gray-500']">
            {{ formatTime(message.timestamp) }}
          </p>
        </div>
      </div>

      <!-- 错误提示 -->
      <div v-if="errorMessage" class="flex justify-start">
        <div
          class="bg-red-50 border-l-4 border-red-500 rounded-2xl px-4 py-3 shadow-sm max-w-[80%]"
        >
          <p class="text-sm text-red-700">{{ errorMessage }}</p>
        </div>
      </div>
    </div>

    <!-- 输入框 -->
    <div class="p-4 bg-white border-t border-gray-200">
      <form @submit.prevent="sendMessage" class="flex gap-2">
        <input
          v-model="inputMessage"
          type="text"
          placeholder="输入你的问题..."
          class="flex-1 px-4 py-2 rounded-xl border-2 border-gray-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-200 outline-none transition-all"
          :disabled="isLoading"
        />
        <button
          type="submit"
          :disabled="!inputMessage.trim() || isLoading"
          class="px-4 py-2 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-xl font-semibold hover:from-amber-600 hover:to-orange-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          发送
        </button>
      </form>
      <p class="text-xs text-gray-500 mt-2 text-center">💡 可以问我关于历史、课程、博物馆等问题</p>
    </div>
  </div>
</template>

<style scoped>
/* 自定义滚动条 */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #fbbf24;
  border-radius: 10px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #f59e0b;
}
</style>
