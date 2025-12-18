import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/components/Layout.vue'
import Home from '@/views/Home.vue'
import Lessons from '@/views/Lessons.vue'
import LessonDetail from '@/views/LessonDetail.vue'
import Badges from '@/views/Badges.vue'
import Timeline from '@/views/Timeline.vue'
import Stats from '@/views/Stats.vue'
import Museums from '@/views/Museums.vue'
import MuseumDetail from '@/views/MuseumDetail.vue'
import Login from '@/views/Login.vue'
import Friends from '@/views/Friends.vue'
import PK from '@/views/PK.vue'
import HistoryStudy from '@/views/HistoryStudy.vue'
import HistoricalFigures from '@/views/HistoricalFigures.vue'
import FigureChat from '@/views/FigureChat.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: Login,
    },
    {
      path: '/',
      component: Layout,
      children: [
        {
          path: '',
          name: 'Home',
          component: Home,
        },
        {
          path: 'lessons',
          name: 'Lessons',
          component: Lessons,
        },
        {
          path: 'lessons/:id',
          name: 'LessonDetail',
          component: LessonDetail,
        },
        {
          path: 'badges',
          name: 'Badges',
          component: Badges,
        },
        {
          path: 'timeline',
          name: 'Timeline',
          component: Timeline,
        },
        {
          path: 'stats',
          name: 'Stats',
          component: Stats,
        },
        {
          path: 'museums',
          name: 'Museums',
          component: Museums,
        },
        {
          path: 'museums/:id',
          name: 'MuseumDetail',
          component: MuseumDetail,
        },
        {
          path: 'friends',
          name: 'Friends',
          component: Friends,
        },
        {
          path: 'pk',
          name: 'PK',
          component: PK,
        },
        {
          path: 'history-study',
          name: 'HistoryStudy',
          component: HistoryStudy,
        },
        {
          path: 'figures',
          name: 'HistoricalFigures',
          component: HistoricalFigures,
        },
        {
          path: 'figures/:id',
          name: 'FigureChat',
          component: FigureChat,
        },
      ],
    },
  ],
})

export default router
