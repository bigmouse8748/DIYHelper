import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
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
    path: '/diy-assistant',
    name: 'DIYAssistant',
    component: () => import('@/views/DIYAssistant.vue'),
    meta: { title: 'DIY智能助手', requiresAuth: true }
  },
  {
    path: '/tool-identification',
    name: 'ToolIdentification',
    component: () => import('@/views/ToolIdentification.vue'),
    meta: { title: '工具识别助手', requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', hideNav: true }
  },
  {
    path: '/register',
    name: 'Register', 
    component: () => import('@/views/Register.vue'),
    meta: { title: '注册', hideNav: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: '个人中心', requiresAuth: true }
  },
  {
    path: '/admin/products',
    name: 'AdminProductManagement',
    component: () => import('@/views/AdminProductManagement.vue'),
    meta: { title: '产品推荐管理', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/products',
    name: 'ProductRecommendations',
    component: () => import('@/views/ProductRecommendations.vue'),
    meta: { title: '产品推荐' }
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
  
  // Check if route requires authentication
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('access_token')
    if (!token) {
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
    
    // Check if route requires admin access
    if (to.meta.requiresAdmin) {
      const userInfoStr = localStorage.getItem('user_info')
      if (userInfoStr) {
        const userInfo = JSON.parse(userInfoStr)
        if (userInfo.membership_level !== 'admin') {
          // Redirect non-admin users to dashboard
          next({ name: 'Dashboard' })
          return
        }
      } else {
        // No user info, redirect to login
        next({ name: 'Login', query: { redirect: to.fullPath } })
        return
      }
    }
  }
  
  next()
})

export default router