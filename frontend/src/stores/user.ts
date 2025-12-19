import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserProgress } from '../data/mockData'
import { mockBadges } from '../data/mockData'
import { supabase } from '../services/supabase'
import { getUserProfile } from '../services/database'
import { lessonApi, userApi } from '../services/api'
import type { User, Session } from '@supabase/supabase-js'

export const useUserStore = defineStore('user', () => {
  // 用户信息
  const userId = ref<string>('user-001')
  const username = ref<string>('历史学习者')
  const isLoggedIn = ref<boolean>(false)
  const user = ref<User | null>(null)
  const session = ref<Session | null>(null)
  const loading = ref<boolean>(false)

  // 用户进度
  const progress = ref<UserProgress>({
    userId: 'user-001',
    completedLessons: [],
    badges: [],
    totalStudyTime: 0,
    correctRate: 0,
    currentStreak: 0,
  })

  // 已解锁的勋章
  const unlockedBadges = computed(() => {
    return mockBadges.filter((badge) => progress.value.badges.includes(badge.id))
  })

  // 从数据库加载用户数据
  const loadUserData = async (uid: string) => {
    try {
      // 加载用户资料
      const profile = await getUserProfile(uid)
      if (profile?.username) {
        username.value = profile.username
      }

      // 通过后端 API 加载学习进度
      try {
        const progressResponse = await lessonApi.getAllProgress()
        const progressData = progressResponse.data
        // 确保 progressData 是数组
        if (Array.isArray(progressData)) {
          const completedLessonIds = progressData
            .filter((p: { completed: boolean }) => p.completed)
            .map((p: { lesson_id: string }) => p.lesson_id)
          progress.value.completedLessons = completedLessonIds
        }

        // 通过后端 API 加载用户统计和勋章
        const statsResponse = await userApi.getStats()
        const statsData = statsResponse.data
        if (statsData) {
          progress.value.badges = statsData.badges || []
          progress.value.totalStudyTime = statsData.total_study_time || 0
          progress.value.correctRate = statsData.correct_rate || 0
          progress.value.currentStreak = statsData.current_streak || 0
        }
      } catch (apiError) {
        console.warn('后端 API 暂不可用，使用本地数据:', apiError)
      }

      progress.value.userId = uid
    } catch (error) {
      console.error('加载用户数据失败:', error)
    }
  }

  // 刷新用户数据（从后端同步最新状态）
  const refreshUserData = async () => {
    if (!isLoggedIn.value || userId.value === 'guest') return

    try {
      // 获取课程进度
      const progressResponse = await lessonApi.getAllProgress()
      const progressData = progressResponse.data
      // 确保 progressData 是数组
      if (Array.isArray(progressData)) {
        const completedLessonIds = progressData
          .filter((p: { completed: boolean }) => p.completed)
          .map((p: { lesson_id: string }) => p.lesson_id)
        progress.value.completedLessons = completedLessonIds
      }

      // 获取用户统计和勋章
      const statsResponse = await userApi.getStats()
      const statsData = statsResponse.data
      if (statsData) {
        progress.value.badges = statsData.badges || []
        progress.value.totalStudyTime = statsData.total_study_time || 0
        progress.value.correctRate = statsData.correct_rate || 0
        progress.value.currentStreak = statsData.current_streak || 0
      }
    } catch (error) {
      console.error('刷新用户数据失败:', error)
    }
  }

  // 完成课程（通过后端 API）
  const completeLesson = async (
    lessonId: string,
    correctCount: number = 0,
    totalCount: number = 0,
    score: number = 0,
  ) => {
    // 先更新本地状态（乐观更新）
    if (!progress.value.completedLessons.includes(lessonId)) {
      progress.value.completedLessons.push(lessonId)
    }

    // 如果用户已登录，通过后端 API 同步
    if (isLoggedIn.value && userId.value !== 'guest') {
      try {
        const response = await lessonApi.complete({
          lesson_id: lessonId,
          correct_count: correctCount,
          total_count: totalCount,
          score: score,
        })

        // 从后端响应更新勋章
        const data = response.data
        if (data.all_badges) {
          progress.value.badges = data.all_badges
        }

        // 如果有新勋章解锁，可以触发通知
        if (data.new_badges && data.new_badges.length > 0) {
          console.log('🎉 新勋章解锁:', data.new_badges)
          // 可以在这里触发全局通知或事件
        }
      } catch (error) {
        console.error('同步课程完成状态失败:', error)
        // 即使后端失败，本地状态已更新
      }
    } else {
      // 游客模式，只更新本地状态
      checkBadgeUnlock()
    }
  }

  // 添加学习时间（通过后端 API）
  const addStudyTime = async (minutes: number) => {
    progress.value.totalStudyTime += minutes

    // 如果用户已登录，同步到后端
    if (isLoggedIn.value && userId.value !== 'guest') {
      try {
        await userApi.addStudyTime(minutes)
      } catch (error) {
        console.error('同步学习时长失败:', error)
      }
    }

    checkBadgeUnlock()
  }

  // 更新正确率
  const updateCorrectRate = (correct: number, total: number) => {
    const rate = correct / total
    progress.value.correctRate = rate
    if (rate === 1) {
      // 完美答题，检查是否解锁相关勋章
      checkBadgeUnlock()
    }
  }

  // 检查并解锁勋章
  const checkBadgeUnlock = () => {
    const { completedLessons, totalStudyTime, correctRate } = progress.value

    // 历史初学者
    if (completedLessons.length >= 1 && !progress.value.badges.includes('badge-1')) {
      progress.value.badges.push('badge-1')
    }

    // 完美答题者
    if (correctRate === 1 && !progress.value.badges.includes('badge-3')) {
      progress.value.badges.push('badge-3')
    }

    // 时间旅行者
    if (totalStudyTime >= 600 && !progress.value.badges.includes('badge-6')) {
      progress.value.badges.push('badge-6')
    }

    // 历史大师
    if (completedLessons.length >= 14 && !progress.value.badges.includes('badge-5')) {
      progress.value.badges.push('badge-5')
    }
  }

  // 注册
  const register = async (email: string, password: string, displayName?: string) => {
    loading.value = true
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            username: displayName || email.split('@')[0],
          },
        },
      })

      if (error) throw error

      if (data.user) {
        user.value = data.user
        session.value = data.session
        userId.value = data.user.id
        const userMetadata = data.user.user_metadata as { username?: string } | undefined
        const emailPrefix = email.split('@')[0] || '用户'
        username.value = userMetadata?.username || emailPrefix
        isLoggedIn.value = true

        // 加载用户数据
        await loadUserData(data.user.id)
      }

      return { data, error: null }
    } catch (error) {
      return { data: null, error: error as Error }
    } finally {
      loading.value = false
    }
  }

  // 登录
  const login = async (email: string, password: string) => {
    loading.value = true
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      })

      if (error) throw error

      if (data.user && data.session) {
        user.value = data.user
        session.value = data.session
        userId.value = data.user.id
        const userMetadata = data.user.user_metadata as { username?: string } | undefined
        username.value = userMetadata?.username || email.split('@')[0] || '历史学习者'
        isLoggedIn.value = true

        // 加载用户数据
        await loadUserData(data.user.id)
      }

      return { data, error: null }
    } catch (error) {
      return { data: null, error: error as Error }
    } finally {
      loading.value = false
    }
  }

  // 游客模式登录
  const loginAsGuest = () => {
    userId.value = 'guest'
    username.value = '游客'
    isLoggedIn.value = true
  }

  // 登出
  const logout = async () => {
    loading.value = true
    try {
      const { error } = await supabase.auth.signOut()
      if (error) throw error

      user.value = null
      session.value = null
      userId.value = 'user-001'
      username.value = '历史学习者'
      isLoggedIn.value = false

      // 重置进度
      progress.value = {
        userId: 'user-001',
        completedLessons: [],
        badges: [],
        totalStudyTime: 0,
        correctRate: 0,
        currentStreak: 0,
      }
    } catch (error) {
      console.error('登出错误:', error)
    } finally {
      loading.value = false
    }
  }

  // 初始化（检查 Supabase 会话）
  const init = async () => {
    loading.value = true
    try {
      const {
        data: { session: currentSession },
      } = await supabase.auth.getSession()

      if (currentSession?.user) {
        user.value = currentSession.user
        session.value = currentSession
        userId.value = currentSession.user.id
        username.value =
          (currentSession.user.user_metadata?.username as string) ||
          currentSession.user.email?.split('@')[0] ||
          '历史学习者'
        isLoggedIn.value = true

        // 加载用户数据
        await loadUserData(currentSession.user.id)
      }

      // 监听认证状态变化
      supabase.auth.onAuthStateChange(async (_event, authSession) => {
        if (authSession?.user) {
          user.value = authSession.user
          session.value = authSession
          userId.value = authSession.user.id
          const userMetadata = authSession.user.user_metadata as { username?: string } | undefined
          username.value =
            userMetadata?.username || authSession.user.email?.split('@')[0] || '历史学习者'
          isLoggedIn.value = true

          // 加载用户数据
          await loadUserData(authSession.user.id)
        } else {
          user.value = null
          session.value = null
          userId.value = 'user-001'
          username.value = '历史学习者'
          isLoggedIn.value = false
        }
      })
    } catch (error) {
      console.error('初始化用户状态错误:', error)
    } finally {
      loading.value = false
    }
  }

  // 初始化
  init()

  return {
    userId,
    username,
    isLoggedIn,
    user,
    session,
    loading,
    progress,
    unlockedBadges,
    completeLesson,
    addStudyTime,
    updateCorrectRate,
    register,
    login,
    loginAsGuest,
    logout,
    init,
    loadUserData,
    refreshUserData,
  }
})
