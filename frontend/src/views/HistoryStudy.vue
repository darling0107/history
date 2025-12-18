<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import HistoryCard from '@/components/HistoryCard.vue'
import {
  chinaHistoryEvents,
  historyByDynasty,
  historyByCategory,
  type HistoryEvent,
} from '@/data/chinaHistory'

const searchQuery = ref('')
const selectedDynasty = ref<string>('全部')
const selectedCategory = ref<string>('全部')
const selectedEvent = ref<HistoryEvent | null>(null)
const viewMode = ref<'grid' | 'timeline'>('grid')

// 朝代列表
const dynasties = computed(() => [
  '全部',
  ...Object.keys(historyByDynasty).filter(
    (d) => historyByDynasty[d as keyof typeof historyByDynasty].length > 0,
  ),
])

// 类别列表
const categories = computed(() => [
  '全部',
  ...Object.keys(historyByCategory).filter(
    (c) => historyByCategory[c as keyof typeof historyByCategory].length > 0,
  ),
])

const extractYear = (year?: string) => {
  if (!year) {
    return 0
  }
  const isBeforeCommonEra = /前/.test(year)
  const sanitized = year.replace(/[^0-9-]/g, '')
  const [start] = sanitized.split('-')
  const numericYear = parseInt(start || '0') || 0
  return isBeforeCommonEra ? -numericYear : numericYear
}

// 筛选后的历史事件
const filteredEvents = computed(() => {
  let events = chinaHistoryEvents

  // 按朝代筛选
  if (selectedDynasty.value !== '全部') {
    events = events.filter((e) => e.dynasty === selectedDynasty.value)
  }

  // 按类别筛选
  if (selectedCategory.value !== '全部') {
    events = events.filter((e) => e.category === selectedCategory.value)
  }

  // 按搜索关键词筛选
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    events = events.filter(
      (e) =>
        e.title.toLowerCase().includes(query) ||
        e.description.toLowerCase().includes(query) ||
        e.content.toLowerCase().includes(query) ||
        e.keywords.some((k) => k.toLowerCase().includes(query)),
    )
  }

  // 按时间排序（从早到晚）
  return events.sort((a, b) => {
    const yearA = extractYear(a.year)
    const yearB = extractYear(b.year)
    return yearA - yearB
  })
})

// 按时间线分组
const timelineEvents = computed(() => {
  const timeline: Record<string, HistoryEvent[]> = {}
  filteredEvents.value.forEach((event) => {
    const dynasty = event.dynasty
    if (!timeline[dynasty]) {
      timeline[dynasty] = []
    }
    timeline[dynasty].push(event)
  })
  return timeline
})

const openEventDetail = (event: HistoryEvent) => {
  selectedEvent.value = event
}

const closeEventDetail = () => {
  selectedEvent.value = null
}

// 页面加载动画
const pageLoaded = ref(false)
onMounted(() => {
  setTimeout(() => {
    pageLoaded.value = true
  }, 100)
})
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50">
    <!-- 页面头部 -->
    <div
      class="bg-white/80 backdrop-blur-sm shadow-lg sticky top-0 z-40 transition-all duration-700"
      :class="pageLoaded ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-10'"
    >
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div
          class="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0"
        >
          <!-- 标题 -->
          <div>
            <h1
              class="text-3xl font-bold bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent mb-2"
            >
              📚 中国历史学习
            </h1>
            <p class="text-gray-600">探索中国5000年文明史，了解重要历史事件和人物</p>
          </div>

          <!-- 视图切换 -->
          <div class="flex items-center space-x-4">
            <button
              @click="viewMode = 'grid'"
              :class="[
                'px-4 py-2 rounded-lg font-semibold transition-all duration-300',
                viewMode === 'grid'
                  ? 'bg-amber-500 text-white shadow-lg'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300',
              ]"
            >
              <span class="flex items-center space-x-2">
                <span>🔲</span>
                <span>卡片视图</span>
              </span>
            </button>
            <button
              @click="viewMode = 'timeline'"
              :class="[
                'px-4 py-2 rounded-lg font-semibold transition-all duration-300',
                viewMode === 'timeline'
                  ? 'bg-amber-500 text-white shadow-lg'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300',
              ]"
            >
              <span class="flex items-center space-x-2">
                <span>📅</span>
                <span>时间线视图</span>
              </span>
            </button>
          </div>
        </div>

        <!-- 搜索和筛选 -->
        <div class="mt-6 space-y-4">
          <!-- 搜索框 -->
          <div class="relative">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索历史事件、人物、关键词..."
              class="w-full px-4 py-3 pl-12 rounded-xl border-2 border-gray-200 focus:border-amber-500 focus:ring-4 focus:ring-amber-200 outline-none transition-all duration-300"
            />
            <span class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 text-xl">🔍</span>
          </div>

          <!-- 筛选器 -->
          <div class="flex flex-wrap gap-4">
            <!-- 朝代筛选 -->
            <div class="flex-1 min-w-[200px]">
              <label class="block text-sm font-semibold text-gray-700 mb-2">朝代</label>
              <select
                v-model="selectedDynasty"
                class="w-full px-4 py-2 rounded-lg border-2 border-gray-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-200 outline-none transition-all duration-300"
              >
                <option v-for="dynasty in dynasties" :key="dynasty" :value="dynasty">
                  {{ dynasty }}
                </option>
              </select>
            </div>

            <!-- 类别筛选 -->
            <div class="flex-1 min-w-[200px]">
              <label class="block text-sm font-semibold text-gray-700 mb-2">类别</label>
              <select
                v-model="selectedCategory"
                class="w-full px-4 py-2 rounded-lg border-2 border-gray-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-200 outline-none transition-all duration-300"
              >
                <option v-for="category in categories" :key="category" :value="category">
                  {{ category }}
                </option>
              </select>
            </div>
          </div>

          <!-- 统计信息 -->
          <div class="flex items-center space-x-4 text-sm text-gray-600">
            <span
              >共找到
              <strong class="text-amber-600">{{ filteredEvents.length }}</strong> 个历史事件</span
            >
            <span v-if="searchQuery" class="text-amber-600">搜索: "{{ searchQuery }}"</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 卡片视图 -->
      <Transition name="fade" mode="out-in">
        <div v-if="viewMode === 'grid'" key="grid" class="space-y-8">
          <div
            v-if="filteredEvents.length === 0"
            class="text-center py-16 bg-white rounded-2xl shadow-lg"
          >
            <span class="text-6xl mb-4 block">🔍</span>
            <p class="text-gray-600 text-lg">没有找到相关历史事件</p>
            <p class="text-gray-500 text-sm mt-2">试试调整搜索条件或筛选器</p>
          </div>

          <div
            v-else
            class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 transition-all duration-500 auto-rows-fr"
          >
            <HistoryCard
              v-for="event in filteredEvents"
              :key="event.id"
              :event="event"
              :is-active="selectedEvent?.id === event.id"
              @view-detail="openEventDetail"
              class="transition-all duration-500 hover:scale-105"
            />
          </div>
        </div>

        <!-- 时间线视图 -->
        <div v-else key="timeline" class="space-y-8">
          <div
            v-if="Object.keys(timelineEvents).length === 0"
            class="text-center py-16 bg-white rounded-2xl shadow-lg"
          >
            <span class="text-6xl mb-4 block">🔍</span>
            <p class="text-gray-600 text-lg">没有找到相关历史事件</p>
            <p class="text-gray-500 text-sm mt-2">试试调整搜索条件或筛选器</p>
          </div>

          <div v-else class="space-y-12">
            <div
              v-for="(events, dynasty) in timelineEvents"
              :key="dynasty"
              class="relative bg-white rounded-2xl shadow-lg p-6 overflow-hidden"
            >
              <!-- 朝代标题 -->
              <div class="flex items-center space-x-4 mb-6 pb-4 border-b-2 border-amber-200">
                <div
                  class="w-16 h-16 bg-gradient-to-r from-amber-500 to-orange-500 rounded-full flex items-center justify-center text-white text-2xl font-bold shadow-lg"
                >
                  {{ dynasty.charAt(0) }}
                </div>
                <div>
                  <h2 class="text-2xl font-bold text-gray-800">{{ dynasty }}</h2>
                  <p class="text-gray-600 text-sm">{{ events.length }} 个历史事件</p>
                </div>
              </div>

              <!-- 时间线事件 -->
              <div class="relative pl-8">
                <!-- 时间线 -->
                <div
                  class="absolute left-4 top-0 bottom-0 w-1 bg-gradient-to-b from-amber-400 to-orange-400 rounded-full"
                ></div>

                <!-- 事件卡片 -->
                <div class="space-y-6">
                  <div
                    v-for="(event, index) in events"
                    :key="event.id"
                    class="relative flex items-start space-x-4 pl-8"
                  >
                    <!-- 时间点 -->
                    <div
                      class="absolute left-0 w-8 h-8 bg-gradient-to-r from-amber-500 to-orange-500 rounded-full border-4 border-white shadow-lg flex items-center justify-center text-white text-xs font-bold transform -translate-x-1/2 z-10"
                      :style="{ top: '0.5rem' }"
                    >
                      {{ index + 1 }}
                    </div>

                    <!-- 事件卡片 -->
                    <div class="flex-1">
                      <HistoryCard
                        :event="event"
                        :is-active="selectedEvent?.id === event.id"
                        @view-detail="openEventDetail"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </div>

    <!-- 详情面板 -->
    <Transition name="detail-fade">
      <div
        v-if="selectedEvent"
        class="fixed inset-0 z-50 flex items-center justify-center px-4 py-8 bg-black/40 backdrop-blur-sm"
      >
        <div
          class="relative bg-white rounded-3xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
        >
          <button
            class="absolute top-4 right-4 w-10 h-10 rounded-full bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors flex items-center justify-center text-xl"
            @click="closeEventDetail"
          >
            ×
          </button>

          <div class="p-8 space-y-6">
            <div class="flex flex-col gap-6 md:flex-row md:items-center">
              <div
                class="w-20 h-20 bg-gradient-to-r from-amber-500 to-orange-500 rounded-2xl text-white text-3xl font-bold flex items-center justify-center shadow-lg"
              >
                {{ selectedEvent.dynasty.charAt(0) }}
              </div>
              <div class="flex-1 space-y-2">
                <p class="text-sm uppercase tracking-widest text-amber-600">
                  {{ selectedEvent.category }}
                </p>
                <h2 class="text-3xl font-bold text-gray-900">{{ selectedEvent.title }}</h2>
                <div class="flex flex-wrap gap-4 text-gray-600">
                  <span class="flex items-center gap-2">
                    <span>📅</span>
                    <span>{{ selectedEvent.period }}</span>
                  </span>
                  <span class="flex items-center gap-2">
                    <span>🏛️</span>
                    <span>{{ selectedEvent.dynasty }}</span>
                  </span>
                </div>
              </div>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <div class="p-4 bg-amber-50 rounded-2xl border border-amber-100">
                <p class="text-sm text-amber-600 mb-1">关键词</p>
                <div class="flex flex-wrap gap-2">
                  <span
                    v-for="keyword in selectedEvent.keywords"
                    :key="keyword"
                    class="px-3 py-1 bg-white rounded-full text-amber-700 text-xs font-semibold border border-amber-100"
                  >
                    {{ keyword }}
                  </span>
                </div>
              </div>
              <div class="p-4 bg-blue-50 rounded-2xl border border-blue-100">
                <p class="text-sm text-blue-600 mb-1">历史意义</p>
                <p class="text-gray-700 leading-relaxed">
                  {{ selectedEvent.significance }}
                </p>
              </div>
            </div>

            <div class="space-y-4">
              <div
                class="p-6 bg-gradient-to-r from-amber-50 to-orange-50 rounded-3xl border border-amber-100"
              >
                <h3 class="text-xl font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <span>📖</span>
                  <span>事件概览</span>
                </h3>
                <p class="text-gray-700 leading-relaxed">{{ selectedEvent.description }}</p>
              </div>
              <div class="p-6 bg-white rounded-3xl border border-gray-100">
                <h3 class="text-xl font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <span>📝</span>
                  <span>详细讲解</span>
                </h3>
                <p class="text-gray-700 leading-relaxed whitespace-pre-line">
                  {{ selectedEvent.content }}
                </p>
              </div>
            </div>

            <div
              v-if="selectedEvent.relatedEvents && selectedEvent.relatedEvents.length > 0"
              class="p-6 bg-gray-50 rounded-3xl border border-gray-200"
            >
              <h3 class="text-xl font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <span>🔗</span>
                <span>相关事件</span>
              </h3>
              <p class="text-sm text-gray-600">推荐继续探索这些事件，强化对该历史阶段的理解。</p>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.detail-fade-enter-active,
.detail-fade-leave-active {
  transition: opacity 0.2s ease;
}

.detail-fade-enter-from,
.detail-fade-leave-to {
  opacity: 0;
}
</style>
