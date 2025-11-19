<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { chinaTimeline, worldTimeline, type TimelineEvent } from '../data/mockData'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

const activeTab = ref<'china' | 'world'>('china')

const currentTimeline = computed<TimelineEvent[]>(() => {
  return activeTab.value === 'china' ? chinaTimeline : worldTimeline
})

const goToLesson = (lessonId?: string) => {
  if (lessonId) {
    router.push(`/lessons/${lessonId}`)
  }
}

const isCompleted = (lessonId?: string) => {
  if (!lessonId) return false
  return userStore.progress.completedLessons.includes(lessonId)
}
</script>

<template>
  <div class="space-y-8">
    <div class="text-center space-y-4">
      <h1 class="text-4xl font-bold text-gray-800">历史学习路径</h1>
      <p class="text-gray-600">沿着时间轴探索人类文明的发展历程</p>
    </div>

    <!-- 分支切换 -->
    <div class="flex justify-center">
      <div class="inline-flex bg-white rounded-lg p-1 shadow-lg">
        <button
          @click="activeTab = 'china'"
          :class="[
            'px-6 py-2 rounded-md font-semibold transition-all',
            activeTab === 'china'
              ? 'bg-amber-500 text-white shadow-md'
              : 'text-gray-600 hover:text-gray-800',
          ]"
        >
          🇨🇳 中国历史
        </button>
        <button
          @click="activeTab = 'world'"
          :class="[
            'px-6 py-2 rounded-md font-semibold transition-all',
            activeTab === 'world'
              ? 'bg-amber-500 text-white shadow-md'
              : 'text-gray-600 hover:text-gray-800',
          ]"
        >
          🌍 世界历史
        </button>
      </div>
    </div>

    <!-- 统计信息 -->
    <div class="bg-gradient-to-r from-amber-50 to-orange-50 rounded-xl p-4 text-center">
      <p class="text-gray-700">
        <span class="font-bold text-amber-600">{{ currentTimeline.length }}</span> 个历史事件
        <span v-if="activeTab === 'china'" class="ml-4 text-sm text-gray-600">
          从夏朝到辛亥革命，跨越4000多年
        </span>
        <span v-else class="ml-4 text-sm text-gray-600"> 从古代文明到现代世界，跨越5000多年 </span>
      </p>
    </div>

    <!-- 时间轴 -->
    <div class="relative">
      <!-- 时间轴线 -->
      <div
        class="absolute left-8 md:left-1/2 top-0 bottom-0 w-1 bg-amber-200 transform md:-translate-x-1/2"
      ></div>

      <!-- 时间轴事件 -->
      <div class="space-y-12">
        <div
          v-for="(event, index) in currentTimeline"
          :key="event.id"
          :class="[
            'relative flex items-center',
            index % 2 === 0 ? 'md:flex-row' : 'md:flex-row-reverse',
          ]"
        >
          <!-- 时间点 -->
          <div
            class="absolute left-6 md:left-1/2 w-4 h-4 bg-amber-500 rounded-full border-4 border-white shadow-lg transform md:-translate-x-1/2 z-10"
          ></div>

          <!-- 事件卡片 -->
          <div
            :class="[
              'ml-16 md:ml-0 md:w-5/12 bg-white rounded-xl shadow-lg p-6 cursor-pointer hover:shadow-xl transition-all',
              index % 2 === 0 ? 'md:mr-auto md:pr-12' : 'md:ml-auto md:pl-12',
              isCompleted(event.lessonId) ? 'ring-2 ring-green-500' : '',
            ]"
            @click="goToLesson(event.lessonId)"
          >
            <div class="flex items-start justify-between mb-2">
              <div>
                <div class="flex items-center space-x-2 mb-2">
                  <span class="text-2xl font-bold text-amber-600">{{ event.year }}</span>
                  <span
                    v-if="isCompleted(event.lessonId)"
                    class="text-green-500 text-xl"
                    title="已完成"
                    >✅</span
                  >
                </div>
                <h3 class="text-xl font-bold text-gray-800 mb-2">{{ event.title }}</h3>
                <p class="text-gray-600 text-sm mb-3">{{ event.description }}</p>
              </div>
            </div>

            <div class="flex items-center justify-between">
              <span
                class="px-3 py-1 bg-amber-100 text-amber-700 rounded-full text-xs font-semibold"
              >
                {{ event.civilization }}
              </span>
              <button
                v-if="event.lessonId"
                @click.stop="goToLesson(event.lessonId)"
                class="px-4 py-2 bg-amber-500 text-white rounded-lg text-sm font-semibold hover:bg-amber-600 transition-colors"
              >
                {{ isCompleted(event.lessonId) ? '重新学习' : '开始学习' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 说明 -->
    <div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
      <p class="text-sm text-gray-700">
        💡 提示：点击时间轴上的事件卡片可以跳转到对应的课程进行学习
      </p>
    </div>
  </div>
</template>
