import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import HomeTest from '@/views/HomeTest.vue'
import Projects from '@/views/Projects.vue'
import About from '@/views/About.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: 'DIY智能助手' }
  },
  {
    path: '/home-original',
    name: 'HomeOriginal', 
    component: () => import('@/views/Home.vue'),
    meta: { title: 'DIY智能助手 - Original' }
  },
  {
    path: '/projects',
    name: 'Projects',
    component: Projects,
    meta: { title: '我的项目' }
  },
  {
    path: '/about',
    name: 'About',
    component: About,
    meta: { title: '关于' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title} - DIY智能助手` || 'DIY智能助手'
  next()
})

export default router