<script setup lang="ts">
import { ref, computed } from 'vue'
import type { HistoryEvent } from '@/data/chinaHistory'

interface Props {
  event: HistoryEvent
  isActive?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isActive: false,
})

const emit = defineEmits<{
  viewDetail: [event: HistoryEvent]
}>()

const isHovered = ref(false)

const formatPeriod = (period?: string) => {
  if (!period) {
    return ''
  }
  if (/公元前/.test(period)) {
    return period
  }
  return period.replace(/公元(?!前)\s*/g, '').trim()
}

const formattedPeriod = computed(() => formatPeriod(props.event.period))

const cardColor = computed(() => {
  const colors: Record<string, string> = {
    政治: 'from-blue-500 to-blue-600',
    文化: 'from-purple-500 to-purple-600',
    战争: 'from-red-500 to-red-600',
    科技: 'from-green-500 to-green-600',
    经济: 'from-amber-500 to-amber-600',
    社会: 'from-pink-500 to-pink-600',
  }
  return colors[props.event.category] || 'from-gray-500 to-gray-600'
})

const categoryIcon = computed(() => {
  const icons: Record<string, string> = {
    政治: '👑',
    文化: '📚',
    战争: '⚔️',
    科技: '🔬',
    经济: '💰',
    社会: '👥',
  }
  return icons[props.event.category] || '📖'
})

const cardBorderClass = computed(() => (props.isActive ? 'ring-4 ring-amber-300' : ''))

const handleViewDetail = () => {
  emit('viewDetail', props.event)
}
</script>

<template>
  <div
    class="history-card relative bg-white rounded-2xl shadow-lg overflow-hidden transition-all duration-500 hover:shadow-2xl transform hover:-translate-y-2"
    :class="cardBorderClass"
    @mouseenter="isHovered = true"
    @mouseleave="isHovered = false"
  >
    <!-- 卡片头部 -->
    <div class="relative h-32 bg-gradient-to-r p-6 text-white overflow-hidden" :class="cardColor">
      <!-- 背景装饰 -->
      <div
        class="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16 transform transition-transform duration-500"
        :class="isHovered ? 'scale-150' : 'scale-100'"
      ></div>
      <div
        class="absolute bottom-0 left-0 w-24 h-24 bg-white/10 rounded-full -ml-12 -mb-12 transform transition-transform duration-500"
        :class="isHovered ? 'scale-150' : 'scale-100'"
      ></div>

      <!-- 内容 -->
      <div class="relative z-10">
        <div class="flex items-start justify-between mb-2">
          <div class="flex-1">
            <div class="flex items-center space-x-2 mb-1">
              <span class="text-2xl">{{ categoryIcon }}</span>
              <span class="px-2 py-1 bg-white/20 rounded-lg text-xs font-semibold backdrop-blur-sm">
                {{ event.category }}
              </span>
            </div>
            <h3 class="text-xl font-bold mb-1 line-clamp-2">{{ event.title }}</h3>
          </div>
        </div>
        <div class="flex items-center space-x-4 text-sm opacity-90">
          <span class="flex items-center space-x-1">
            <span>📅</span>
            <span>{{ formattedPeriod }}</span>
          </span>
          <span class="flex items-center space-x-1">
            <span>🏛️</span>
            <span>{{ event.dynasty }}</span>
          </span>
        </div>
      </div>
    </div>

    <!-- 卡片内容 -->
    <div class="p-6">
      <!-- 简介 -->
      <p class="text-gray-700 mb-4 line-clamp-2">
        {{ event.description }}
      </p>

      <!-- 关键词 -->
      <div class="flex flex-wrap gap-2 mb-4">
        <span
          v-for="keyword in event.keywords.slice(0, 4)"
          :key="keyword"
          class="px-2 py-1 bg-amber-100 text-amber-700 rounded-lg text-xs font-medium"
        >
          {{ keyword }}
        </span>
      </div>

      <!-- 查看详情 -->
      <button
        @click="handleViewDetail"
        class="w-full mt-4 py-3 px-4 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-lg font-semibold transition-all duration-300 hover:from-amber-600 hover:to-orange-600 hover:shadow-lg transform hover:scale-105 active:scale-95 flex items-center justify-center space-x-2 group"
      >
        <span>查看详情</span>
        <span class="transition-transform duration-300 group-hover:translate-x-1">→</span>
      </button>
    </div>

    <!-- 装饰性边框 -->
    <div
      class="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-white/50 to-transparent transform transition-opacity duration-500"
      :class="isHovered ? 'opacity-100' : 'opacity-0'"
    ></div>
  </div>
</template>

<style scoped>
.history-card {
  animation: fadeInUp 0.5s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
