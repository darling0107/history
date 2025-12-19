<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { mockBadges } from '../data/mockData'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()

// 进入页面时刷新用户数据
onMounted(async () => {
  await userStore.refreshUserData()
})

const allBadges = computed(() => {
  return mockBadges.map((badge) => ({
    ...badge,
    unlocked: userStore.progress.badges.includes(badge.id),
    unlockedAt: userStore.progress.badges.includes(badge.id) ? new Date().toISOString() : undefined,
  }))
})

const unlockedCount = computed(() => {
  return allBadges.value.filter((b) => b.unlocked).length
})
</script>

<template>
  <div class="space-y-8">
    <div class="text-center space-y-4">
      <h1 class="text-4xl font-bold text-gray-800">勋章系统</h1>
      <p class="text-gray-600">已解锁 {{ unlockedCount }} / {{ allBadges.length }} 个勋章</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="badge in allBadges"
        :key="badge.id"
        :class="[
          'bg-white rounded-xl shadow-lg p-6 transition-all',
          badge.unlocked
            ? 'ring-2 ring-amber-500 transform hover:scale-105'
            : 'opacity-60 grayscale',
        ]"
      >
        <div class="text-center space-y-4">
          <div class="text-6xl">{{ badge.icon }}</div>
          <div>
            <h3 class="text-xl font-bold text-gray-800">{{ badge.name }}</h3>
            <p class="text-gray-600 text-sm mt-2">{{ badge.description }}</p>
          </div>
          <div class="pt-4 border-t border-gray-200">
            <p class="text-xs text-gray-500">获得条件：{{ badge.requirement }}</p>
            <div v-if="badge.unlocked" class="mt-2">
              <span
                class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-700"
              >
                ✓ 已解锁
              </span>
            </div>
            <div v-else class="mt-2">
              <span
                class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-gray-100 text-gray-500"
              >
                🔒 未解锁
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 进度统计 -->
    <div class="bg-gradient-to-r from-amber-500 to-orange-500 rounded-xl p-6 text-white">
      <div class="text-center space-y-2">
        <p class="text-2xl font-bold">收集进度</p>
        <div class="w-full bg-white/20 rounded-full h-4 mt-4">
          <div
            class="bg-white h-4 rounded-full transition-all duration-500"
            :style="{ width: `${(unlockedCount / allBadges.length) * 100}%` }"
          ></div>
        </div>
        <p class="text-lg">{{ Math.round((unlockedCount / allBadges.length) * 100) }}%</p>
      </div>
    </div>
  </div>
</template>
