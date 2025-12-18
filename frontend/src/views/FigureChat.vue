<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { historicalFigures } from '@/data/historicalFigures'
import { streamChatCompletion, type ChatMessage } from '@/services/openai'

const route = useRoute()
const router = useRouter()

const figureId = route.params.id as string
const figure = historicalFigures.find((f) => f.id === figureId)

// 如果找不到人物，返回列表页
if (!figure) {
  router.push('/figures')
}

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

const messages = ref<Message[]>([])
const inputMessage = ref('')
const isLoading = ref(false)
const messageContainer = ref<HTMLElement>()
const errorMessage = ref('')

// 初始化欢迎语
onMounted(() => {
  if (figure) {
    messages.value.push({
      id: 'init',
      role: 'assistant',
      content: figure.greeting,
      timestamp: new Date(),
    })
  }
})

const sendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value || !figure) return

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

  await nextTick()
  scrollToBottom()

  const aiMessageId = (Date.now() + 1).toString()
  const aiMessage = {
    id: aiMessageId,
    role: 'assistant' as const,
    content: '',
    timestamp: new Date(),
  }
  messages.value.push(aiMessage)

  try {
    const conversationMessages: ChatMessage[] = messages.value
      .filter((msg) => msg.id !== aiMessageId && msg.content.trim())
      .slice(-10)
      .map((msg) => ({
        role: msg.role,
        content: msg.content,
      }))

    const options = {
      model: 'deepseek-chat',
      temperature: 0.8, // 稍微提高温度以增加创造性
      maxTokens: 2000,
      systemPrompt: figure.systemPrompt,
    }

    let fullContent = ''
    for await (const chunk of streamChatCompletion(conversationMessages, options)) {
      fullContent += chunk
      const messageIndex = messages.value.findIndex((m) => m.id === aiMessageId)
      if (messageIndex > -1 && messages.value[messageIndex]) {
        messages.value[messageIndex].content = fullContent
      }
      await nextTick()
      scrollToBottom()
    }

    isLoading.value = false
  } catch (error) {
    console.error('Chat error:', error)
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
    v-if="figure"
    class="h-[calc(100vh-8rem)] flex flex-col bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100"
  >
    <!-- 头部 -->
    <div
      class="bg-gradient-to-r from-amber-500 to-orange-500 text-white p-4 flex items-center justify-between shadow-md z-10"
    >
      <div class="flex items-center gap-4">
        <button
          @click="router.push('/figures')"
          class="p-2 hover:bg-white/20 rounded-full transition-colors"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 19l-7-7 7-7"
            />
          </svg>
        </button>
        <div
          class="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center text-2xl border-2 border-white/30"
        >
          {{ figure.avatar }}
        </div>
        <div>
          <h3 class="font-bold text-xl">{{ figure.name }}</h3>
          <p class="text-xs text-white/90">{{ figure.title }}</p>
        </div>
      </div>
    </div>

    <!-- 消息列表 -->
    <div ref="messageContainer" class="flex-1 overflow-y-auto p-6 space-y-6 bg-gray-50">
      <div
        v-for="message in messages"
        :key="message.id"
        class="flex"
        :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
      >
        <!-- 头像 -->
        <div
          v-if="message.role === 'assistant'"
          class="w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center text-xl mr-3 flex-shrink-0 border border-amber-200"
        >
          {{ figure.avatar }}
        </div>

        <div
          :class="[
            'max-w-[70%] rounded-2xl px-6 py-4 shadow-sm',
            message.role === 'user'
              ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-tr-none'
              : 'bg-white text-gray-800 border border-gray-100 rounded-tl-none',
          ]"
        >
          <p class="text-base leading-relaxed whitespace-pre-wrap">{{ message.content }}</p>
          <p :class="['text-xs mt-2', message.role === 'user' ? 'text-white/70' : 'text-gray-400']">
            {{ formatTime(message.timestamp) }}
          </p>
        </div>
      </div>

      <!-- 错误提示 -->
      <div v-if="errorMessage" class="flex justify-center">
        <div
          class="bg-red-50 text-red-600 px-4 py-2 rounded-lg text-sm border border-red-100 shadow-sm"
        >
          {{ errorMessage }}
        </div>
      </div>
    </div>

    <!-- 输入框 -->
    <div class="p-4 bg-white border-t border-gray-100">
      <form @submit.prevent="sendMessage" class="flex gap-4 max-w-4xl mx-auto">
        <input
          v-model="inputMessage"
          type="text"
          :placeholder="`与${figure.name}对话...`"
          class="flex-1 px-6 py-3 rounded-xl border-2 border-gray-100 focus:border-amber-500 focus:ring-4 focus:ring-amber-100 outline-none transition-all text-gray-700 placeholder-gray-400"
          :disabled="isLoading"
        />
        <button
          type="submit"
          :disabled="!inputMessage.trim() || isLoading"
          class="px-8 py-3 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-xl font-bold hover:from-amber-600 hover:to-orange-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-md hover:shadow-lg transform hover:-translate-y-0.5"
        >
          发送
        </button>
      </form>
    </div>
  </div>
</template>
