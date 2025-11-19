// src/composables/useChat.ts
// 注意：此文件已更新为使用 DeepSeek API
// 如果不需要此 composable，可以删除此文件

import { ref } from 'vue'
import { streamChatCompletion, type ChatMessage } from '@/services/openai'

export function useChat() {
  const messages = ref<ChatMessage[]>([])
  const loading = ref(false)

  async function ask(question: string) {
    loading.value = true
    messages.value.push({ role: 'user', content: question })

    try {
      // 使用 DeepSeek API
      const conversationMessages: ChatMessage[] = messages.value
        .filter((msg) => msg.content.trim())
        .slice(-10) // 只保留最近10条消息

      const options = {
        model: 'deepseek-chat',
        temperature: 0.7,
        maxTokens: 2000,
      }

      let assistantReply = ''

      // 流式获取回复
      for await (const chunk of streamChatCompletion(conversationMessages, options)) {
        assistantReply += chunk
      }

      messages.value.push({ role: 'assistant', content: assistantReply })
    } catch (error) {
      console.error('DeepSeek API error:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  return { messages, loading, ask }
}
