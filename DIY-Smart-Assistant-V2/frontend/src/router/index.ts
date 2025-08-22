import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // Landing/Home page
    {
      path: '/',
      name: 'landing',
      component: () => import('../views/LandingView.vue'),
      meta: { requiresAuth: false }
    },
    
    // Dashboard for authenticated users
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('../views/DashboardView.vue'),
      meta: { requiresAuth: true, layout: 'main' }
    },
    
    // Authentication routes
    {
      path: '/auth',
      component: () => import('../layouts/AuthLayout.vue'),
      children: [
        {
          path: 'login',
          name: 'login',
          component: () => import('../views/auth/LoginView.vue'),
          meta: { requiresAuth: false, requiresGuest: true }
        },
        {
          path: 'register',
          name: 'register',
          component: () => import('../views/auth/RegisterView.vue'),
          meta: { requiresAuth: false, requiresGuest: true }
        }
      ]
    },
    
    // Tool-related routes
    {
      path: '/tools',
      component: () => import('../layouts/MainLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          redirect: '/tools/identification'
        },
        {
          path: 'identification',
          name: 'tool-identification',
          component: () => import('../views/tools/ToolIdentificationView.vue')
        },
        {
          path: 'smart-finder',
          name: 'smart-tool-finder',
          component: () => import('../views/tools/SmartToolFinderView.vue')
        },
        {
          path: 'recommendation',
          name: 'product-recommendation',
          component: () => import('../views/tools/ProductRecommendationView.vue')
        },
        {
          path: 'analysis',
          name: 'project-analysis',
          component: () => import('../views/tools/ProjectAnalysisMinimal.vue')
        }
      ]
    },
    
    // Shopping/Products routes
    {
      path: '/products',
      component: () => import('../layouts/MainLayout.vue'),
      meta: { requiresAuth: false },
      children: [
        {
          path: 'our-picks',
          name: 'our-picks',
          component: () => import('../views/products/OurPicksView.vue')
        }
      ]
    },
    
    // Admin routes
    {
      path: '/admin',
      component: () => import('../layouts/AdminLayout.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
      children: [
        {
          path: '',
          redirect: '/admin/dashboard'
        },
        {
          path: 'dashboard',
          name: 'admin-dashboard',
          component: () => import('../views/admin/AdminDashboardView.vue')
        },
        {
          path: 'users',
          name: 'admin-users',
          component: () => import('../views/admin/UserManagementView.vue')
        },
        {
          path: 'products',
          name: 'admin-products',
          component: () => import('../views/admin/ProductManagementView.vue')
        }
      ]
    },
    
    // User profile
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue'),
      meta: { requiresAuth: true, layout: 'main' }
    },
    
    // Email verification
    {
      path: '/verify-email',
      name: 'verify-email',
      component: () => import('../views/auth/VerifyEmailView.vue'),
      meta: { requiresAuth: false }
    },
    
    // Development/Testing routes
    {
      path: '/test',
      name: 'test',
      component: () => import('../views/TestView.vue'),
      meta: { requiresAuth: false }
    },
    
    // 404 Not Found
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('../views/NotFoundView.vue')
    }
  ],
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Initialize auth state on first visit
  if (!authStore.user && authStore.accessToken) {
    await authStore.initialize()
  }

  // Check authentication requirements
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login' })
    return
  }

  // Redirect authenticated users away from guest pages
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next({ name: 'dashboard' })
    return
  }

  // Check admin requirements
  if (to.meta.requiresAdmin && (!authStore.isAuthenticated || !authStore.isAdmin)) {
    next({ name: 'dashboard' })
    return
  }

  next()
})

export default router
