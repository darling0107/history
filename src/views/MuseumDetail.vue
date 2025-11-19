<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getMuseumById, type Artifact } from '@/data/museumData'

const route = useRoute()
const router = useRouter()

const museum = computed(() => {
  const id = route.params.id as string
  return getMuseumById(id)
})

const selectedArtifact = ref<Artifact | null>(null)

const showArtifactDetail = (artifact: Artifact) => {
  selectedArtifact.value = artifact
}

const closeArtifactDetail = () => {
  selectedArtifact.value = null
}

onMounted(() => {
  if (!museum.value) {
    router.push('/museums')
  }
})
</script>

<template>
  <div v-if="museum" class="space-y-8">
    <!-- 博物馆信息 -->
    <div
      class="relative bg-gradient-to-r from-amber-50 via-orange-50 to-red-50 rounded-3xl shadow-2xl p-8 md:p-12 overflow-hidden"
    >
      <!-- 背景装饰 -->
      <div class="absolute inset-0 opacity-10">
        <div class="absolute top-0 right-0 w-64 h-64 bg-amber-400 rounded-full blur-3xl"></div>
        <div class="absolute bottom-0 left-0 w-64 h-64 bg-orange-400 rounded-full blur-3xl"></div>
      </div>

      <div class="relative z-10">
        <div class="flex items-start justify-between mb-6">
          <div class="flex-1">
            <div class="text-8xl mb-4">{{ museum.coverImage }}</div>
            <h1 class="text-4xl md:text-5xl font-bold text-gray-800 mb-2">
              {{ museum.name }}
            </h1>
            <p class="text-xl text-gray-600 italic mb-4">{{ museum.nameEn }}</p>
            <p class="text-gray-700 text-lg leading-relaxed max-w-3xl">
              {{ museum.description }}
            </p>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <div class="bg-white/80 backdrop-blur-sm rounded-xl p-4">
            <div class="text-sm text-gray-600 mb-1">位置</div>
            <div class="text-lg font-bold text-gray-800">{{ museum.location }}</div>
          </div>
          <div class="bg-white/80 backdrop-blur-sm rounded-xl p-4">
            <div class="text-sm text-gray-600 mb-1">建立时间</div>
            <div class="text-lg font-bold text-gray-800">{{ museum.established }}</div>
          </div>
          <div class="bg-white/80 backdrop-blur-sm rounded-xl p-4">
            <div class="text-sm text-gray-600 mb-1">文物数量</div>
            <div class="text-lg font-bold text-gray-800">{{ museum.artifacts.length }} 件精选</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 文物列表 -->
    <div class="space-y-6">
      <h2 class="text-3xl font-bold text-gray-800">精选文物</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="artifact in museum.artifacts"
          :key="artifact.id"
          class="group bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-2xl transition-all cursor-pointer transform hover:-translate-y-2 border border-gray-100"
          @click="showArtifactDetail(artifact)"
        >
          <!-- 图片区域 -->
          <div class="relative h-64 bg-gradient-to-br from-amber-100 to-orange-100 overflow-hidden">
            <img
              :src="artifact.imageUrl"
              :alt="artifact.name"
              class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
              @error="
                (e) => {
                  ;(e.target as HTMLImageElement).style.display = 'none'
                }
              "
            />
            <div class="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent"></div>
            <div class="absolute bottom-4 left-4 right-4">
              <h3 class="text-xl font-bold text-white mb-1">{{ artifact.name }}</h3>
              <p class="text-sm text-white/90 italic">{{ artifact.nameEn }}</p>
            </div>
          </div>

          <!-- 信息区域 -->
          <div class="p-6">
            <div class="space-y-2 mb-4">
              <div class="flex items-center text-sm text-gray-600">
                <span class="mr-2">📅</span>
                <span class="font-medium">{{ artifact.period }}</span>
              </div>
              <div class="flex items-center text-sm text-gray-600">
                <span class="mr-2">🌍</span>
                <span class="font-medium">{{ artifact.civilization }}</span>
              </div>
              <div class="flex items-center text-sm text-gray-600">
                <span class="mr-2">🔧</span>
                <span class="font-medium">{{ artifact.material }}</span>
              </div>
            </div>
            <p class="text-gray-700 text-sm line-clamp-3 mb-4">{{ artifact.description }}</p>
            <button
              class="w-full px-4 py-2 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-lg text-sm font-bold hover:from-amber-600 hover:to-orange-600 transition-all"
            >
              查看详情 →
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 文物详情模态框 -->
    <div
      v-if="selectedArtifact"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
      @click.self="closeArtifactDetail"
    >
      <div
        class="relative bg-white rounded-3xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
        @click.stop
      >
        <!-- 关闭按钮 -->
        <button
          @click="closeArtifactDetail"
          class="absolute top-4 right-4 z-10 w-10 h-10 bg-gray-100 hover:bg-gray-200 rounded-full flex items-center justify-center transition-colors"
        >
          <span class="text-2xl">×</span>
        </button>

        <!-- 内容 -->
        <div class="p-8">
          <!-- 图片 -->
          <div class="mb-6">
            <div
              class="relative h-96 bg-gradient-to-br from-amber-100 to-orange-100 rounded-2xl overflow-hidden"
            >
              <img
                :src="selectedArtifact.imageUrl"
                :alt="selectedArtifact.name"
                class="w-full h-full object-cover"
                @error="
                  (e) => {
                    ;(e.target as HTMLImageElement).style.display = 'none'
                  }
                "
              />
            </div>
          </div>

          <!-- 基本信息 -->
          <div class="mb-6">
            <h2 class="text-3xl md:text-4xl font-bold text-gray-800 mb-2">
              {{ selectedArtifact.name }}
            </h2>
            <p class="text-xl text-gray-600 italic mb-4">{{ selectedArtifact.nameEn }}</p>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div class="bg-amber-50 rounded-xl p-4">
                <div class="text-sm text-gray-600 mb-1">📅 时期</div>
                <div class="text-lg font-bold text-gray-800">{{ selectedArtifact.period }}</div>
              </div>
              <div class="bg-orange-50 rounded-xl p-4">
                <div class="text-sm text-gray-600 mb-1">🌍 文明</div>
                <div class="text-lg font-bold text-gray-800">
                  {{ selectedArtifact.civilization }}
                </div>
              </div>
              <div class="bg-red-50 rounded-xl p-4">
                <div class="text-sm text-gray-600 mb-1">🔧 材质</div>
                <div class="text-lg font-bold text-gray-800">{{ selectedArtifact.material }}</div>
              </div>
              <div class="bg-yellow-50 rounded-xl p-4">
                <div class="text-sm text-gray-600 mb-1">📏 尺寸</div>
                <div class="text-lg font-bold text-gray-800">{{ selectedArtifact.dimensions }}</div>
              </div>
            </div>
          </div>

          <!-- 详细描述 -->
          <div class="space-y-6">
            <div>
              <h3 class="text-2xl font-bold text-gray-800 mb-3 flex items-center gap-2">
                <span
                  class="w-1 h-8 bg-gradient-to-b from-amber-500 to-orange-500 rounded-full"
                ></span>
                文物介绍
              </h3>
              <p class="text-gray-700 leading-relaxed text-lg">
                {{ selectedArtifact.detailedDescription }}
              </p>
            </div>

            <div>
              <h3 class="text-2xl font-bold text-gray-800 mb-3 flex items-center gap-2">
                <span
                  class="w-1 h-8 bg-gradient-to-b from-amber-500 to-orange-500 rounded-full"
                ></span>
                历史意义
              </h3>
              <p class="text-gray-700 leading-relaxed text-lg">
                {{ selectedArtifact.significance }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div v-else class="text-center py-12">
    <p class="text-gray-600">博物馆不存在</p>
  </div>
</template>
