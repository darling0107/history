<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useFriendStore } from '@/stores/friend'
import type { Friend } from '@/stores/friend'

const router = useRouter()
const friendStore = useFriendStore()

const searchQuery = ref('')
const showAddFriend = ref(false)
const newFriendUsername = ref('')

const filteredFriends = computed(() => {
  if (!searchQuery.value) {
    return friendStore.friends
  }
  return friendStore.friends.filter((friend) =>
    friend.username.toLowerCase().includes(searchQuery.value.toLowerCase()),
  )
})

const addFriend = () => {
  if (!newFriendUsername.value.trim()) return

  const newFriend: Friend = {
    id: `friend-${Date.now()}`,
    username: newFriendUsername.value.trim(),
    avatar: '👤',
    status: 'offline',
    level: 1,
    winCount: 0,
    totalMatches: 0,
    lastActive: new Date(),
  }

  friendStore.addFriend(newFriend)
  newFriendUsername.value = ''
  showAddFriend.value = false
}

const startPK = (friend: Friend) => {
  friendStore.startPK(friend)
  router.push('/pk')
}

const getStatusColor = (status: Friend['status']) => {
  switch (status) {
    case 'online':
      return 'bg-green-500'
    case 'in-game':
      return 'bg-blue-500'
    default:
      return 'bg-gray-400'
  }
}

const getStatusText = (status: Friend['status']) => {
  switch (status) {
    case 'online':
      return '在线'
    case 'in-game':
      return '游戏中'
    default:
      return '离线'
  }
}
</script>

<template>
  <div class="space-y-8">
    <!-- 标题 -->
    <div class="text-center space-y-4">
      <h1
        class="text-5xl md:text-6xl font-bold bg-gradient-to-r from-amber-600 via-orange-500 to-red-500 bg-clip-text text-transparent"
      >
        好友系统
      </h1>
      <p class="text-xl text-gray-600">添加好友，一起PK历史知识！</p>
    </div>

    <!-- 搜索和添加 -->
    <div class="flex flex-col sm:flex-row gap-4 items-center justify-between">
      <div class="flex-1 max-w-md">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="搜索好友..."
          class="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-200 outline-none transition-all"
        />
      </div>
      <button
        @click="showAddFriend = !showAddFriend"
        class="px-6 py-3 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-xl font-bold hover:from-amber-600 hover:to-orange-600 transition-all shadow-lg hover:shadow-xl"
      >
        {{ showAddFriend ? '取消' : '+ 添加好友' }}
      </button>
    </div>

    <!-- 添加好友表单 -->
    <div v-if="showAddFriend" class="bg-white rounded-2xl shadow-lg p-6 border border-gray-200">
      <h3 class="text-xl font-bold text-gray-800 mb-4">添加新好友</h3>
      <div class="flex gap-4">
        <input
          v-model="newFriendUsername"
          type="text"
          placeholder="输入好友用户名"
          class="flex-1 px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-amber-500 focus:ring-2 focus:ring-amber-200 outline-none transition-all"
          @keyup.enter="addFriend"
        />
        <button
          @click="addFriend"
          class="px-6 py-3 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-xl font-bold hover:from-amber-600 hover:to-orange-600 transition-all"
        >
          添加
        </button>
      </div>
    </div>

    <!-- 在线好友 -->
    <div v-if="friendStore.onlineFriends.length > 0" class="space-y-4">
      <h2 class="text-2xl font-bold text-gray-800">在线好友</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="friend in friendStore.onlineFriends"
          :key="friend.id"
          class="bg-white rounded-2xl shadow-lg p-6 border border-gray-200 hover:shadow-xl transition-all"
        >
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-3">
              <div class="text-4xl">{{ friend.avatar }}</div>
              <div>
                <h3 class="text-lg font-bold text-gray-800">{{ friend.username }}</h3>
                <p class="text-sm text-gray-500">等级 {{ friend.level }}</p>
              </div>
            </div>
            <div
              :class="['w-3 h-3 rounded-full', getStatusColor(friend.status)]"
              :title="getStatusText(friend.status)"
            ></div>
          </div>

          <div class="space-y-2 mb-4 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-600">胜场：</span>
              <span class="font-semibold text-green-600">{{ friend.winCount }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">总场次：</span>
              <span class="font-semibold text-gray-800">{{ friend.totalMatches }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">胜率：</span>
              <span class="font-semibold text-amber-600">
                {{
                  friend.totalMatches > 0
                    ? Math.round((friend.winCount / friend.totalMatches) * 100)
                    : 0
                }}%
              </span>
            </div>
          </div>

          <button
            @click="startPK(friend)"
            :disabled="friend.status === 'in-game'"
            :class="[
              'w-full py-2 rounded-xl font-bold transition-all',
              friend.status === 'in-game'
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-gradient-to-r from-amber-500 to-orange-500 text-white hover:from-amber-600 hover:to-orange-600 shadow-lg hover:shadow-xl',
            ]"
          >
            {{ friend.status === 'in-game' ? '游戏中...' : '发起PK' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 所有好友 -->
    <div class="space-y-4">
      <h2 class="text-2xl font-bold text-gray-800">所有好友 ({{ filteredFriends.length }})</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="friend in filteredFriends"
          :key="friend.id"
          class="bg-white rounded-2xl shadow-lg p-6 border border-gray-200 hover:shadow-xl transition-all"
        >
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-3">
              <div class="text-4xl">{{ friend.avatar }}</div>
              <div>
                <h3 class="text-lg font-bold text-gray-800">{{ friend.username }}</h3>
                <p class="text-sm text-gray-500">等级 {{ friend.level }}</p>
              </div>
            </div>
            <div
              :class="['w-3 h-3 rounded-full', getStatusColor(friend.status)]"
              :title="getStatusText(friend.status)"
            ></div>
          </div>

          <div class="space-y-2 mb-4 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-600">胜场：</span>
              <span class="font-semibold text-green-600">{{ friend.winCount }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">总场次：</span>
              <span class="font-semibold text-gray-800">{{ friend.totalMatches }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">胜率：</span>
              <span class="font-semibold text-amber-600">
                {{
                  friend.totalMatches > 0
                    ? Math.round((friend.winCount / friend.totalMatches) * 100)
                    : 0
                }}%
              </span>
            </div>
          </div>

          <div class="flex gap-2">
            <button
              @click="startPK(friend)"
              :disabled="friend.status === 'in-game' || friend.status === 'offline'"
              :class="[
                'flex-1 py-2 rounded-xl font-bold transition-all',
                friend.status === 'in-game' || friend.status === 'offline'
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-gradient-to-r from-amber-500 to-orange-500 text-white hover:from-amber-600 hover:to-orange-600 shadow-lg hover:shadow-xl',
              ]"
            >
              {{
                friend.status === 'in-game' ? '游戏中' : friend.status === 'offline' ? '离线' : 'PK'
              }}
            </button>
            <button
              @click="friendStore.removeFriend(friend.id)"
              class="px-4 py-2 bg-red-100 text-red-600 rounded-xl font-bold hover:bg-red-200 transition-colors"
              title="删除好友"
            >
              删除
            </button>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="filteredFriends.length === 0" class="text-center py-12">
        <div class="text-6xl mb-4">👥</div>
        <p class="text-gray-600 text-lg">没有找到好友</p>
        <p class="text-gray-500 text-sm mt-2">尝试添加新好友或调整搜索条件</p>
      </div>
    </div>
  </div>
</template>
