<script setup lang="ts">
import { useRouter } from 'vue-router'
import { historicalFigures } from '@/data/historicalFigures'

const router = useRouter()

const startChat = (id: string) => {
  router.push(`/figures/${id}`)
}
</script>

<template>
  <div class="space-y-8">
    <div class="text-center space-y-4">
      <h1 class="text-4xl font-bold text-gray-800">与历史对话</h1>
      <p class="text-gray-600">选择一位历史人物，开启一场跨越时空的对话</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      <div
        v-for="figure in historicalFigures"
        :key="figure.id"
        class="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden group cursor-pointer border border-gray-100"
        @click="startChat(figure.id)"
      >
        <div class="p-6 flex flex-col items-center text-center space-y-4">
          <div
            class="w-24 h-24 bg-gradient-to-br from-amber-100 to-orange-100 rounded-full flex items-center justify-center text-5xl shadow-inner group-hover:scale-110 transition-transform duration-300"
          >
            {{ figure.avatar }}
          </div>

          <div>
            <h3 class="text-2xl font-bold text-gray-800">{{ figure.name }}</h3>
            <p class="text-amber-600 font-medium text-sm mt-1">{{ figure.title }}</p>
          </div>

          <div class="px-3 py-1 bg-gray-100 rounded-full text-xs text-gray-500">
            {{ figure.period }}
          </div>

          <p class="text-gray-600 text-sm line-clamp-2">
            {{ figure.description }}
          </p>

          <button
            class="w-full py-2 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-xl font-semibold opacity-0 group-hover:opacity-100 transform translate-y-2 group-hover:translate-y-0 transition-all duration-300"
          >
            开始对话
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
