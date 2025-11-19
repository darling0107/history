<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { HistoryEvent } from '@/data/chinaHistory'

interface Props {
  event: HistoryEvent
  isExpanded?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isExpanded: false,
})

const emit = defineEmits<{
  expand: [id: string]
  collapse: [id: string]
}>()

const isExpanded = ref(props.isExpanded)
const isHovered = ref(false)

// 监听props变化
watch(
  () => props.isExpanded,
  (newVal) => {
    isExpanded.value = newVal
  },
)

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

const toggleExpand = () => {
  isExpanded.value = !isExpanded.value
  if (isExpanded.value) {
    emit('expand', props.event.id)
  } else {
    emit('collapse', props.event.id)
  }
}
</script>

<template>
  <div
    class="history-card relative bg-white rounded-2xl shadow-lg overflow-hidden transition-all duration-500 hover:shadow-2xl transform hover:-translate-y-2"
    :class="isExpanded ? 'ring-4 ring-amber-300' : ''"
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
            <span>{{ event.period }}</span>
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
      <p class="text-gray-700 mb-4 line-clamp-2" :class="isExpanded ? '' : 'line-clamp-2'">
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

      <!-- 详细内容（展开时显示） -->
      <Transition name="slide-down">
        <div v-if="isExpanded" class="mt-4 space-y-4">
          <!-- 详细讲解 -->
          <div
            class="bg-gradient-to-r from-amber-50 to-orange-50 rounded-xl p-4 border-l-4 border-amber-500"
          >
            <h4 class="font-semibold text-gray-800 mb-2 flex items-center space-x-2">
              <span>📖</span>
              <span>详细讲解</span>
            </h4>
            <p class="text-gray-700 leading-relaxed whitespace-pre-line">{{ event.content }}</p>
          </div>

          <!-- 历史意义 -->
          <div
            class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-4 border-l-4 border-blue-500"
          >
            <h4 class="font-semibold text-gray-800 mb-2 flex items-center space-x-2">
              <span>⭐</span>
              <span>历史意义</span>
            </h4>
            <p class="text-gray-700">{{ event.significance }}</p>
          </div>

          <!-- 相关事件 -->
          <div
            v-if="event.relatedEvents && event.relatedEvents.length > 0"
            class="bg-gray-50 rounded-xl p-4"
          >
            <h4 class="font-semibold text-gray-800 mb-2 flex items-center space-x-2">
              <span>🔗</span>
              <span>相关事件</span>
            </h4>
            <p class="text-sm text-gray-600">查看其他相关历史事件以了解更多背景</p>
          </div>
        </div>
      </Transition>

      <!-- 展开/收起按钮 -->
      <button
        @click="toggleExpand"
        class="w-full mt-4 py-2 px-4 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-lg font-semibold transition-all duration-300 hover:from-amber-600 hover:to-orange-600 hover:shadow-lg transform hover:scale-105 active:scale-95 flex items-center justify-center space-x-2"
      >
        <span>{{ isExpanded ? '收起' : '展开详情' }}</span>
        <span
          class="transform transition-transform duration-300"
          :class="isExpanded ? 'rotate-180' : ''"
        >
          ▼
        </span>
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

.slide-down-enter-active {
  transition: all 0.3s ease-out;
}

.slide-down-leave-active {
  transition: all 0.2s ease-in;
}

.slide-down-enter-from {
  opacity: 0;
  transform: translateY(-10px);
  max-height: 0;
}

.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-10px);
  max-height: 0;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
