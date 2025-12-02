<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { toast } from 'vue3-toastify'

const router = useRouter()
const userStore = useUserStore()

const email = ref('')
const password = ref('')
const username = ref('')
const isLogin = ref(true)
const errorMessage = ref('')
const isLoading = ref(false)
const successMessage = ref('')

// 输入框焦点状态
const emailFocused = ref(false)
const passwordFocused = ref(false)
const usernameFocused = ref(false)

// 密码可见性
const showPassword = ref(false)

// 表单验证
const isEmailValid = computed(() => {
  if (!email.value) return true
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)
})

const isPasswordValid = computed(() => {
  if (!password.value) return true
  return password.value.length >= 6
})

const isFormValid = computed(() => {
  if (isLogin.value) {
    return email.value && password.value && isEmailValid.value && isPasswordValid.value
  } else {
    return (
      email.value && password.value && username.value && isEmailValid.value && isPasswordValid.value
    )
  }
})

const handleSubmit = async () => {
  errorMessage.value = ''
  successMessage.value = ''

  if (!isFormValid.value) {
    errorMessage.value = '请填写完整的表单信息'
    return
  }

  isLoading.value = true

  try {
    if (isLogin.value) {
      // 登录
      const { error } = await userStore.login(email.value, password.value)
      if (error) {
        errorMessage.value = error instanceof Error ? error.message : '登录失败，请检查邮箱和密码'
        toast.error('登录失败，请检查邮箱和密码', {
          theme: 'auto',
          transition: 'slide',
          dangerouslyHTMLString: true,
        })
        return
      }

      successMessage.value = '登录成功！'
      toast.success('登录成功!', {
        theme: 'auto',
        transition: 'slide',
        dangerouslyHTMLString: true,
      })
      setTimeout(() => {
        router.push('/')
      }, 1000)
    } else {
      // 注册
      const { error } = await userStore.register(
        email.value,
        password.value,
        username.value || undefined,
      )

      if (error) {
        errorMessage.value = error instanceof Error ? error.message : '注册失败，请重试'
        return
      }

      successMessage.value = '注册成功！正在跳转...'
      toast.success('注册成功! 请前往邮箱进行验证', {
        theme: 'auto',
        transition: 'slide',
        dangerouslyHTMLString: true,
      })
      setTimeout(() => {
        router.push('/')
      }, 2000)
    }
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '操作失败，请重试'
    toast.error('操作失败', {
      theme: 'auto',
      transition: 'slide',
      dangerouslyHTMLString: true,
    })
  } finally {
    isLoading.value = false
  }
}

const toggleMode = () => {
  isLogin.value = !isLogin.value
  errorMessage.value = ''
  successMessage.value = ''
  email.value = ''
  password.value = ''
  username.value = ''
  showPassword.value = false
}

const handleGuestLogin = () => {
  userStore.loginAsGuest()
  router.push('/')
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
  <div
    class="min-h-screen flex items-center justify-center bg-gradient-to-br from-amber-50 via-orange-50 to-red-50 py-12 px-4 relative overflow-hidden"
  >
    <!-- 背景动画装饰 -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div
        class="absolute top-1/4 left-1/4 w-64 h-64 bg-amber-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"
      ></div>
      <div
        class="absolute top-1/3 right-1/4 w-64 h-64 bg-orange-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"
      ></div>
      <div
        class="absolute bottom-1/4 left-1/3 w-64 h-64 bg-red-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"
      ></div>
    </div>

    <div
      class="max-w-md w-full relative z-10 transition-all duration-700"
      :class="pageLoaded ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'"
    >
      <!-- Logo和标题 -->
      <div class="text-center mb-8">
        <div class="inline-block mb-4 transform transition-transform duration-300 hover:scale-110">
          <img
            class="text-6xl inline-block animate-bounce w-72 h-72"
            :class="isLogin ? 'animate-bounce' : 'animate-pulse'"
            src="../../public/images/history_logo.png"
          />
        </div>
        <h1
          class="text-4xl font-bold bg-gradient-to-r from-amber-600 via-orange-500 to-red-500 bg-clip-text text-transparent mb-2 transition-all duration-300"
        >
          HistoriaQuest
        </h1>
        <p class="text-gray-600 transition-all duration-300">
          {{ isLogin ? '欢迎回来' : '创建新账户' }}
        </p>
      </div>

      <!-- 登录/注册卡片 -->
      <div
        class="bg-white/80 backdrop-blur-sm rounded-3xl shadow-2xl p-8 border border-gray-100 transition-all duration-500 hover:shadow-3xl"
      >
        <Transition name="slide-fade" mode="out-in">
          <form
            :key="isLogin ? 'login' : 'register'"
            @submit.prevent="handleSubmit"
            class="space-y-6"
          >
            <!-- 用户名（仅注册时显示） -->
            <Transition name="slide-down">
              <div v-if="!isLogin" class="relative">
                <label
                  for="username"
                  class="block text-sm font-semibold text-gray-700 mb-2 transition-colors"
                  :class="usernameFocused ? 'text-amber-600' : ''"
                >
                  用户名
                </label>
                <div class="relative">
                  <input
                    id="username"
                    v-model="username"
                    type="text"
                    placeholder="请输入用户名"
                    @focus="usernameFocused = true"
                    @blur="usernameFocused = false"
                    class="w-full px-4 py-3 rounded-xl border-2 transition-all duration-300 outline-none"
                    :class="
                      usernameFocused
                        ? 'border-amber-500 ring-4 ring-amber-200 shadow-lg'
                        : 'border-gray-200 hover:border-amber-300'
                    "
                    required
                  />
                  <span
                    class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400"
                    v-if="username"
                  >
                    ✨
                  </span>
                </div>
              </div>
            </Transition>

            <!-- Email -->
            <div class="relative">
              <label
                for="email"
                class="block text-sm font-semibold text-gray-700 mb-2 transition-colors"
                :class="emailFocused ? 'text-amber-600' : ''"
              >
                邮箱
                <span v-if="email && !isEmailValid" class="text-red-500 text-xs ml-2">
                  (格式不正确)
                </span>
              </label>
              <div class="relative">
                <input
                  id="email"
                  v-model="email"
                  type="email"
                  placeholder="请输入邮箱"
                  @focus="emailFocused = true"
                  @blur="emailFocused = false"
                  class="w-full px-4 py-3 rounded-xl border-2 transition-all duration-300 outline-none"
                  :class="
                    emailFocused
                      ? 'border-amber-500 ring-4 ring-amber-200 shadow-lg'
                      : email && !isEmailValid
                        ? 'border-red-300'
                        : 'border-gray-200 hover:border-amber-300'
                  "
                  required
                />
                <span
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 transition-transform duration-300"
                  :class="emailFocused ? 'scale-110' : ''"
                  v-if="email"
                >
                  📧
                </span>
              </div>
            </div>

            <!-- 密码 -->
            <div class="relative">
              <label
                for="password"
                class="block text-sm font-semibold text-gray-700 mb-2 transition-colors"
                :class="passwordFocused ? 'text-amber-600' : ''"
              >
                密码
                <span v-if="password && !isPasswordValid" class="text-red-500 text-xs ml-2">
                  (至少6位)
                </span>
              </label>
              <div class="relative">
                <input
                  id="password"
                  v-model="password"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="请输入密码"
                  @focus="passwordFocused = true"
                  @blur="passwordFocused = false"
                  class="w-full px-4 py-3 pr-12 rounded-xl border-2 transition-all duration-300 outline-none"
                  :class="
                    passwordFocused
                      ? 'border-amber-500 ring-4 ring-amber-200 shadow-lg'
                      : password && !isPasswordValid
                        ? 'border-red-300'
                        : 'border-gray-200 hover:border-amber-300'
                  "
                  required
                />
                <button
                  type="button"
                  @click="showPassword = !showPassword"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-amber-600 transition-colors"
                >
                  {{ showPassword ? '👁️' : '👁️‍🗨️' }}
                </button>
              </div>
            </div>

            <!-- 错误提示 -->
            <Transition name="slide-down">
              <div
                v-if="errorMessage"
                class="bg-red-50 border-l-4 border-red-500 p-4 rounded-lg flex items-center space-x-2 animate-shake"
              >
                <span class="text-red-500 text-xl">⚠️</span>
                <p class="text-sm text-red-700 flex-1">{{ errorMessage }}</p>
              </div>
            </Transition>

            <!-- 成功提示 -->
            <Transition name="slide-down">
              <div
                v-if="successMessage"
                class="bg-green-50 border-l-4 border-green-500 p-4 rounded-lg flex items-center space-x-2"
              >
                <span class="text-green-500 text-xl">✅</span>
                <p class="text-sm text-green-700 flex-1">{{ successMessage }}</p>
              </div>
            </Transition>

            <!-- 提交按钮 -->
            <button
              type="submit"
              :disabled="!isFormValid || isLoading"
              class="w-full py-4 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-xl font-bold text-lg transition-all duration-300 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed relative overflow-hidden group"
              :class="
                isFormValid && !isLoading
                  ? 'hover:from-amber-600 hover:to-orange-600 hover:shadow-xl hover:-translate-y-1 active:scale-95'
                  : ''
              "
            >
              <span
                class="relative z-10 flex items-center justify-center space-x-2"
                v-if="!isLoading"
              >
                <span>{{ isLogin ? '登录' : '注册' }}</span>
                <span class="transition-transform duration-300 group-hover:translate-x-1"> → </span>
              </span>
              <span class="relative z-10 flex items-center justify-center space-x-2" v-else>
                <svg
                  class="animate-spin h-5 w-5 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    class="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    stroke-width="4"
                  ></circle>
                  <path
                    class="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                <span>处理中...</span>
              </span>
              <!-- 按钮光效 -->
              <span
                class="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"
              ></span>
            </button>
          </form>
        </Transition>

        <!-- 切换登录/注册 -->
        <div class="mt-6 text-center">
          <p class="text-gray-600 text-sm">
            {{ isLogin ? '还没有账户？' : '已有账户？' }}
            <button
              @click="toggleMode"
              class="text-amber-600 hover:text-amber-700 font-semibold transition-all duration-300 hover:underline"
            >
              {{ isLogin ? '立即注册' : '立即登录' }}
            </button>
          </p>
        </div>

        <!-- 快速体验 -->
        <div class="mt-6 pt-6 border-t border-gray-200">
          <button
            @click="handleGuestLogin"
            class="w-full py-3 bg-gray-100 text-gray-700 rounded-xl font-semibold hover:bg-gray-200 transition-all duration-300 hover:shadow-md active:scale-95"
          >
            游客模式（无需登录）
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 背景动画 */
@keyframes blob {
  0% {
    transform: translate(0px, 0px) scale(1);
  }
  33% {
    transform: translate(30px, -50px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.9);
  }
  100% {
    transform: translate(0px, 0px) scale(1);
  }
}

.animate-blob {
  animation: blob 7s infinite;
}

.animation-delay-2000 {
  animation-delay: 2s;
}

.animation-delay-4000 {
  animation-delay: 4s;
}

/* 摇动动画 */
@keyframes shake {
  0%,
  100% {
    transform: translateX(0);
  }
  10%,
  30%,
  50%,
  70%,
  90% {
    transform: translateX(-5px);
  }
  20%,
  40%,
  60%,
  80% {
    transform: translateX(5px);
  }
}

.animate-shake {
  animation: shake 0.5s;
}

/* 过渡动画 */
.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.2s ease-in;
}

.slide-fade-enter-from {
  transform: translateX(20px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateX(-20px);
  opacity: 0;
}

.slide-down-enter-active {
  transition: all 0.3s ease-out;
}

.slide-down-leave-active {
  transition: all 0.2s ease-in;
}

.slide-down-enter-from {
  transform: translateY(-10px);
  opacity: 0;
  max-height: 0;
}

.slide-down-leave-to {
  transform: translateY(-10px);
  opacity: 0;
  max-height: 0;
}
</style>
