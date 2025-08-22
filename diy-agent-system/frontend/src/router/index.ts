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
    component: () => import('@/views/CognitoLogin.vue'),
    meta: { title: '登录', hideNav: true }
  },
  {
    path: '/register',
    name: 'Register', 
    component: () => import('@/views/CognitoRegister.vue'),
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
    path: '/admin/users',
    name: 'AdminUserManagement',
    component: () => import('@/views/CognitoUserManagement.vue'),
    meta: { title: '用户管理', requiresAuth: true, requiresAdmin: true }
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
  },
  {
    path: '/auth-test',
    name: 'AuthTest',
    component: () => import('@/views/AuthTest.vue'),
    meta: { title: '认证测试' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

import { useCognitoAuthStore } from '@/stores/cognitoAuth'

// Track if auth has been initialized globally
let authInitialized = false

router.beforeEach(async (to, from, next) => {
  document.title = `${to.meta.title} - DIY智能助手` || 'DIY智能助手'
  
  console.log(`🛡️ Router guard: ${from.name || 'none'} -> ${to.name}`)
  
  const authStore = useCognitoAuthStore()
  
  // Initialize auth once globally
  if (!authInitialized && !authStore.isLoading) {
    console.log('🔄 Initializing auth for first time...')
    authInitialized = true
    try {
      await authStore.initializeAuth()
      console.log('✅ Auth initialization completed')
    } catch (error) {
      console.error('❌ Auth initialization failed:', error)
      authInitialized = false // Reset flag so we can try again
    }
  }
  
  // Wait for any ongoing auth loading to complete
  let waitCount = 0
  const maxWait = 30 // 3 seconds max
  while (authStore.isLoading && waitCount < maxWait) {
    console.log('⏳ Waiting for auth to complete...', waitCount)
    await new Promise(resolve => setTimeout(resolve, 100))
    waitCount++
  }
  
  console.log('🛡️ Auth state check:', {
    route: to.name,
    isAuthenticated: authStore.isAuthenticated,
    isAdmin: authStore.isAdmin,
    userGroups: authStore.userGroups,
    currentUser: authStore.currentUser?.username,
    requiresAuth: to.meta.requiresAuth,
    requiresAdmin: to.meta.requiresAdmin,
    isLoading: authStore.isLoading
  })
  
  // Handle authentication requirements
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      console.log('🚫 Redirecting to login - authentication required')
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
    
    // Handle admin requirements
    if (to.meta.requiresAdmin && !authStore.isAdmin) {
      console.log('🚫 Redirecting to dashboard - admin access required')
      next({ name: 'Dashboard' })
      return
    }
  }
  
  console.log('✅ Access granted to:', to.name)
  next()
})

export default router