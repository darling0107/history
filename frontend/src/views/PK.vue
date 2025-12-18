<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useFriendStore } from '@/stores/friend'
// import { useUserStore } from '@/stores/user'

const router = useRouter()
const friendStore = useFriendStore()
// const userStore = useUserStore()

const selectedAnswer = ref<number | null>(null)
const showResult = ref(false)
const opponentAnswered = ref(false)

const currentMatch = computed(() => friendStore.currentMatch)

const currentQuestion = computed(() => {
  if (!currentMatch.value) return null
  return currentMatch.value.questions[currentMatch.value.currentQuestionIndex]
})

const progress = computed(() => {
  if (!currentMatch.value) return 0
  return ((currentMatch.value.currentQuestionIndex + 1) / currentMatch.value.questions.length) * 100
})

const handleAnswer = (answerIndex: number) => {
  if (showResult.value || !currentMatch.value) return

  selectedAnswer.value = answerIndex
  friendStore.submitAnswer(currentMatch.value.currentQuestionIndex, answerIndex)
  showResult.value = true

  // 等待对手回答
  setTimeout(() => {
    opponentAnswered.value = true
  }, 1000)
}

const handleNext = () => {
  if (!currentMatch.value) return

  if (currentMatch.value.currentQuestionIndex < currentMatch.value.questions.length - 1) {
    friendStore.nextQuestion()
    selectedAnswer.value = null
    showResult.value = false
    opponentAnswered.value = false
  } else {
    friendStore.finishMatch()
  }
}

const handleFinish = () => {
  friendStore.resetMatch()
  router.push('/friends')
}

const isWinner = computed(() => {
  if (!currentMatch.value || currentMatch.value.status !== 'finished') return null
  return currentMatch.value.myScore > currentMatch.value.opponentScore
})

onMounted(() => {
  if (!currentMatch.value) {
    router.push('/friends')
  }
})

onUnmounted(() => {
  // 如果离开页面时对战未完成，可以选择保存状态或重置
})
</script>

<template>
  <div v-if="currentMatch" class="space-y-8">
    <!-- 头部信息 -->
    <div
      class="bg-gradient-to-r from-amber-50 via-orange-50 to-red-50 rounded-3xl shadow-xl p-6 border border-amber-100"
    >
      <div class="flex items-center justify-between mb-4">
        <h1 class="text-3xl font-bold text-gray-800">历史知识PK</h1>
        <div class="text-sm text-gray-600">
          题目 {{ currentMatch.currentQuestionIndex + 1 }} / {{ currentMatch.questions.length }}
        </div>
      </div>

      <!-- 双方分数 -->
      <div class="grid grid-cols-2 gap-4 mt-4">
        <div class="bg-white rounded-xl p-4 text-center">
          <div class="text-sm text-gray-600 mb-1">你</div>
          <div class="text-3xl font-bold text-amber-600">{{ currentMatch.myScore }}</div>
        </div>
        <div class="bg-white rounded-xl p-4 text-center">
          <div class="text-sm text-gray-600 mb-1">{{ currentMatch.opponentName }}</div>
          <div class="text-3xl font-bold text-blue-600">{{ currentMatch.opponentScore }}</div>
        </div>
      </div>

      <!-- 进度条 -->
      <div class="mt-4">
        <div class="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div
            class="bg-gradient-to-r from-amber-500 to-orange-500 h-3 rounded-full transition-all duration-500"
            :style="{ width: `${progress}%` }"
          ></div>
        </div>
      </div>
    </div>

    <!-- 等待开始 -->
    <div v-if="currentMatch.status === 'waiting'" class="text-center py-12">
      <div class="text-6xl mb-4 animate-bounce">⚔️</div>
      <h2 class="text-2xl font-bold text-gray-800 mb-2">准备开始PK</h2>
      <p class="text-gray-600 mb-6">对手：{{ currentMatch.opponentName }}</p>
      <button
        @click="friendStore.nextQuestion()"
        class="px-8 py-4 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-xl font-bold text-lg hover:from-amber-600 hover:to-orange-600 transition-all shadow-lg hover:shadow-xl"
      >
        开始对战
      </button>
    </div>

    <!-- 答题界面 -->
    <div v-else-if="currentMatch.status === 'in-progress' && currentQuestion" class="space-y-6">
      <!-- 题目 -->
      <div class="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
        <h2 class="text-2xl md:text-3xl font-bold text-gray-800 mb-6 leading-relaxed">
          {{ currentQuestion.question }}
        </h2>

        <!-- 选项 -->
        <div class="space-y-4">
          <button
            v-for="(option, index) in currentQuestion.options"
            :key="index"
            @click="handleAnswer(index)"
            :disabled="showResult"
            :class="[
              'w-full text-left p-5 rounded-xl border-2 transition-all transform',
              selectedAnswer === index
                ? currentQuestion.myAnswer === currentQuestion.correctAnswer
                  ? 'border-green-500 bg-gradient-to-r from-green-50 to-emerald-50 shadow-lg scale-105'
                  : 'border-red-500 bg-gradient-to-r from-red-50 to-pink-50 shadow-lg scale-105'
                : showResult && index === currentQuestion.correctAnswer
                  ? 'border-green-500 bg-gradient-to-r from-green-50 to-emerald-50 shadow-lg'
                  : 'border-gray-200 hover:border-amber-400 hover:bg-gradient-to-r hover:from-amber-50 hover:to-orange-50 hover:shadow-md hover:scale-[1.02]',
              showResult ? 'cursor-not-allowed' : 'cursor-pointer',
            ]"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div
                  :class="[
                    'w-8 h-8 rounded-lg flex items-center justify-center font-bold text-sm',
                    selectedAnswer === index
                      ? currentQuestion.myAnswer === currentQuestion.correctAnswer
                        ? 'bg-green-500 text-white'
                        : 'bg-red-500 text-white'
                      : showResult && index === currentQuestion.correctAnswer
                        ? 'bg-green-500 text-white'
                        : 'bg-gray-100 text-gray-600',
                  ]"
                >
                  {{ String.fromCharCode(65 + index) }}
                </div>
                <span class="font-medium text-gray-800 text-lg">{{ option }}</span>
              </div>
              <div v-if="showResult">
                <span
                  v-if="
                    selectedAnswer === index &&
                    currentQuestion.myAnswer === currentQuestion.correctAnswer
                  "
                  class="text-3xl animate-bounce"
                  >✓</span
                >
                <span
                  v-else-if="
                    selectedAnswer === index &&
                    currentQuestion.myAnswer !== currentQuestion.correctAnswer
                  "
                  class="text-3xl animate-bounce"
                  >✗</span
                >
                <span
                  v-else-if="index === currentQuestion.correctAnswer"
                  class="text-3xl text-green-600"
                  >✓</span
                >
              </div>
            </div>
          </button>
        </div>

        <!-- 对手状态 -->
        <div v-if="showResult" class="mt-6 pt-6 border-t border-gray-200">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <div v-if="!opponentAnswered" class="flex items-center gap-2 text-gray-600">
                <div class="w-2 h-2 bg-amber-500 rounded-full animate-bounce"></div>
                <span class="text-sm">等待对手回答...</span>
              </div>
              <div v-else class="flex items-center gap-2 text-green-600">
                <span class="text-sm">✓ 对手已回答</span>
              </div>
            </div>
            <div class="text-sm text-gray-600">
              {{
                currentQuestion.myAnswer === currentQuestion.correctAnswer
                  ? '你答对了！+1分'
                  : '你答错了'
              }}
            </div>
          </div>
        </div>
      </div>

      <!-- 下一题按钮 -->
      <div v-if="showResult && opponentAnswered" class="flex justify-center">
        <button
          @click="handleNext"
          class="px-8 py-4 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-xl font-bold text-lg hover:from-amber-600 hover:to-orange-600 transition-all shadow-lg hover:shadow-xl transform hover:scale-105"
        >
          {{
            currentMatch.currentQuestionIndex < currentMatch.questions.length - 1
              ? '下一题'
              : '查看结果'
          }}
        </button>
      </div>
    </div>

    <!-- 结果界面 -->
    <div v-else-if="currentMatch.status === 'finished'" class="text-center space-y-8">
      <div class="text-8xl mb-4">{{ isWinner ? '🎉' : isWinner === false ? '😊' : '🤝' }}</div>
      <h2 class="text-4xl font-bold text-gray-800 mb-2">
        {{ isWinner ? '恭喜获胜！' : isWinner === false ? '再接再厉！' : '平局！' }}
      </h2>
      <p class="text-xl text-gray-600 mb-8">
        {{
          isWinner
            ? '你的历史知识更胜一筹！'
            : isWinner === false
              ? '继续学习，下次一定能赢！'
              : '势均力敌，都很棒！'
        }}
      </p>

      <!-- 最终分数 -->
      <div class="bg-white rounded-2xl shadow-xl p-8 max-w-md mx-auto">
        <div class="grid grid-cols-2 gap-6 mb-6">
          <div>
            <div class="text-sm text-gray-600 mb-2">你的得分</div>
            <div class="text-4xl font-bold text-amber-600">{{ currentMatch.myScore }}</div>
          </div>
          <div>
            <div class="text-sm text-gray-600 mb-2">{{ currentMatch.opponentName }}的得分</div>
            <div class="text-4xl font-bold text-blue-600">{{ currentMatch.opponentScore }}</div>
          </div>
        </div>
        <div class="text-sm text-gray-500">
          共 {{ currentMatch.questions.length }} 题，正确率：
          {{ Math.round((currentMatch.myScore / currentMatch.questions.length) * 100) }}%
        </div>
      </div>

      <button
        @click="handleFinish"
        class="px-8 py-4 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-xl font-bold text-lg hover:from-amber-600 hover:to-orange-600 transition-all shadow-lg hover:shadow-xl"
      >
        返回好友列表
      </button>
    </div>
  </div>

  <div v-else class="text-center py-12">
    <p class="text-gray-600">没有进行中的对战</p>
    <router-link
      to="/friends"
      class="mt-4 inline-block px-6 py-3 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-xl font-bold hover:from-amber-600 hover:to-orange-600 transition-all"
    >
      去添加好友
    </router-link>
  </div>
</template>
