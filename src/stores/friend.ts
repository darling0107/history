import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface Friend {
  id: string
  username: string
  avatar: string
  status: 'online' | 'offline' | 'in-game'
  level: number
  winCount: number
  totalMatches: number
  lastActive: Date
}

export interface PKMatch {
  id: string
  opponentId: string
  opponentName: string
  status: 'waiting' | 'in-progress' | 'finished'
  myScore: number
  opponentScore: number
  questions: Array<{
    id: string
    question: string
    options: string[]
    correctAnswer: number
    myAnswer?: number
    opponentAnswer?: number
  }>
  currentQuestionIndex: number
  startTime?: Date
  endTime?: Date
}

export const useFriendStore = defineStore('friend', () => {
  // 好友列表
  const friends = ref<Friend[]>([
    {
      id: 'friend-1',
      username: '历史达人',
      avatar: '👨‍🎓',
      status: 'online',
      level: 5,
      winCount: 12,
      totalMatches: 20,
      lastActive: new Date(),
    },
    {
      id: 'friend-2',
      username: '考古学家',
      avatar: '🔍',
      status: 'offline',
      level: 8,
      winCount: 25,
      totalMatches: 35,
      lastActive: new Date(Date.now() - 3600000),
    },
    {
      id: 'friend-3',
      username: '时间旅行者',
      avatar: '⏰',
      status: 'in-game',
      level: 3,
      winCount: 5,
      totalMatches: 10,
      lastActive: new Date(),
    },
  ])

  // 当前PK对战
  const currentMatch = ref<PKMatch | null>(null)

  // 在线好友
  const onlineFriends = computed(() => {
    return friends.value.filter((f) => f.status === 'online' || f.status === 'in-game')
  })

  // 添加好友
  const addFriend = (friend: Friend) => {
    if (!friends.value.find((f) => f.id === friend.id)) {
      friends.value.push(friend)
    }
  }

  // 删除好友
  const removeFriend = (friendId: string) => {
    const index = friends.value.findIndex((f) => f.id === friendId)
    if (index > -1) {
      friends.value.splice(index, 1)
    }
  }

  // 开始PK
  const startPK = (opponent: Friend) => {
    // 生成PK题目（从课程中随机选择）
    const questions = generatePKQuestions(5)

    currentMatch.value = {
      id: `match-${Date.now()}`,
      opponentId: opponent.id,
      opponentName: opponent.username,
      status: 'waiting',
      myScore: 0,
      opponentScore: 0,
      questions,
      currentQuestionIndex: 0,
    }
  }

  // 提交答案
  const submitAnswer = (questionIndex: number, answer: number) => {
    if (!currentMatch.value) return

    const question = currentMatch.value.questions[questionIndex]
    if (!question) return

    question.myAnswer = answer

    if (answer === question.correctAnswer) {
      currentMatch.value.myScore++
    }

    // 模拟对手答案（实际应该从服务器获取）
    setTimeout(() => {
      if (currentMatch.value) {
        const q = currentMatch.value.questions[questionIndex]
        if (q) {
          const randomAnswer = Math.floor(Math.random() * 4)
          q.opponentAnswer = randomAnswer
          if (randomAnswer === q.correctAnswer) {
            currentMatch.value.opponentScore++
          }
        }
      }
    }, 1000)
  }

  // 下一题
  const nextQuestion = () => {
    if (!currentMatch.value) return

    if (currentMatch.value.status === 'waiting') {
      currentMatch.value.status = 'in-progress'
      currentMatch.value.startTime = new Date()
    }

    currentMatch.value.currentQuestionIndex++

    if (currentMatch.value.currentQuestionIndex >= currentMatch.value.questions.length) {
      finishMatch()
    }
  }

  // 完成对战
  const finishMatch = () => {
    if (!currentMatch.value) return

    currentMatch.value.status = 'finished'
    currentMatch.value.endTime = new Date()

    // 更新好友战绩（模拟）
    const opponent = friends.value.find((f) => f.id === currentMatch.value!.opponentId)
    if (opponent) {
      opponent.totalMatches++
      if (currentMatch.value.myScore < currentMatch.value.opponentScore) {
        opponent.winCount++
      }
    }
  }

  // 重置对战
  const resetMatch = () => {
    currentMatch.value = null
  }

  // 生成PK题目
  const generatePKQuestions = (count: number) => {
    // 这里应该从实际的课程数据中随机选择题目
    // 为了演示，使用模拟数据
    const sampleQuestions = [
      {
        id: 'pk-1',
        question: '中国历史上第一个统一的封建王朝是？',
        options: ['夏朝', '商朝', '秦朝', '汉朝'],
        correctAnswer: 2,
      },
      {
        id: 'pk-2',
        question: '《蒙娜丽莎》的作者是？',
        options: ['达芬奇', '米开朗基罗', '拉斐尔', '梵高'],
        correctAnswer: 0,
      },
      {
        id: 'pk-3',
        question: '第一次世界大战爆发的年份是？',
        options: ['1912年', '1914年', '1916年', '1918年'],
        correctAnswer: 1,
      },
      {
        id: 'pk-4',
        question: '丝绸之路的开拓者是？',
        options: ['张骞', '班超', '玄奘', '郑和'],
        correctAnswer: 0,
      },
      {
        id: 'pk-5',
        question: '法国大革命爆发的年份是？',
        options: ['1787年', '1789年', '1791年', '1793年'],
        correctAnswer: 1,
      },
    ]

    return sampleQuestions.slice(0, count)
  }

  return {
    friends,
    currentMatch,
    onlineFriends,
    addFriend,
    removeFriend,
    startPK,
    submitAnswer,
    nextQuestion,
    finishMatch,
    resetMatch,
  }
})
