import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Lesson, Question } from '../data/mockData'
import { mockLessons } from '../data/mockData'

export const useLessonStore = defineStore('lesson', () => {
  const lessons = ref<Lesson[]>(mockLessons)
  const currentLesson = ref<Lesson | null>(null)
  const currentQuestionIndex = ref<number>(0)
  const userAnswers = ref<Record<string, number>>({})
  const isQuizCompleted = ref<boolean>(false)

  // 获取所有课程
  const getAllLessons = () => {
    return lessons.value
  }

  // 根据ID获取课程
  const getLessonById = (id: string): Lesson | undefined => {
    return lessons.value.find((lesson) => lesson.id === id)
  }

  // 设置当前课程
  const setCurrentLesson = (lessonId: string) => {
    const lesson = getLessonById(lessonId)
    if (lesson) {
      currentLesson.value = lesson
      currentQuestionIndex.value = 0
      userAnswers.value = {}
      isQuizCompleted.value = false
    }
  }

  // 获取当前问题
  const getCurrentQuestion = (): Question | null => {
    if (!currentLesson.value) return null
    return currentLesson.value.questions[currentQuestionIndex.value] || null
  }

  // 提交答案
  const submitAnswer = (questionId: string, answer: number) => {
    userAnswers.value[questionId] = answer
  }

  // 下一题
  const nextQuestion = () => {
    if (!currentLesson.value) return
    if (currentQuestionIndex.value < currentLesson.value.questions.length - 1) {
      currentQuestionIndex.value++
    } else {
      isQuizCompleted.value = true
    }
  }

  // 上一题
  const previousQuestion = () => {
    if (currentQuestionIndex.value > 0) {
      currentQuestionIndex.value--
    }
  }

  // 计算答题结果
  const calculateResult = () => {
    if (!currentLesson.value) return { correct: 0, total: 0, rate: 0 }

    const total = currentLesson.value.questions.length
    let correct = 0

    currentLesson.value.questions.forEach((question) => {
      if (userAnswers.value[question.id] === question.answer) {
        correct++
      }
    })

    const rate = correct / total
    return { correct, total, rate }
  }

  // 设置完成状态
  const setQuizCompleted = (completed: boolean) => {
    isQuizCompleted.value = completed
  }

  // 重置课程状态
  const resetLesson = () => {
    currentLesson.value = null
    currentQuestionIndex.value = 0
    userAnswers.value = {}
    isQuizCompleted.value = false
  }

  return {
    lessons,
    currentLesson,
    currentQuestionIndex,
    userAnswers,
    isQuizCompleted,
    getAllLessons,
    getLessonById,
    setCurrentLesson,
    getCurrentQuestion,
    submitAnswer,
    nextQuestion,
    previousQuestion,
    calculateResult,
    setQuizCompleted,
    resetLesson,
  }
})
