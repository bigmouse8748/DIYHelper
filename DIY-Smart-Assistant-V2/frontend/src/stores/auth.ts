import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api, { AUTH_ENDPOINTS } from '@/utils/api'

export interface User {
  id: string
  username: string
  email: string
  user_type: 'free' | 'pro' | 'premium' | 'admin'
  created_at: string
  is_active: boolean
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterCredentials {
  username: string
  email: string
  password: string
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))
  const loading = ref(false)

  // Computed
  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)
  const isAdmin = computed(() => user.value?.user_type === 'admin')
  const isPremium = computed(() => ['premium', 'admin'].includes(user.value?.user_type || ''))
  const isPro = computed(() => ['pro', 'premium', 'admin'].includes(user.value?.user_type || ''))

  // Actions
  const setTokens = (access: string, refresh: string) => {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
  }

  const clearTokens = () => {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  const login = async (credentials: LoginCredentials) => {
    loading.value = true
    try {
      const response = await api.post(AUTH_ENDPOINTS.LOGIN, {
        email: credentials.email,
        password: credentials.password
      })

      const { access_token, refresh_token, user: userData } = response.data
      setTokens(access_token, refresh_token)
      user.value = userData

      return { success: true, user: userData }
    } catch (error: any) {
      clearTokens()
      throw new Error(error.response?.data?.detail || 'Login failed')
    } finally {
      loading.value = false
    }
  }

  const register = async (credentials: RegisterCredentials) => {
    loading.value = true
    try {
      const response = await api.post(AUTH_ENDPOINTS.REGISTER, credentials)
      
      const { access_token, refresh_token, user: userData } = response.data
      setTokens(access_token, refresh_token)
      user.value = userData

      return { success: true, user: userData }
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Registration failed')
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    loading.value = true
    try {
      if (refreshToken.value) {
        await api.post(AUTH_ENDPOINTS.LOGOUT, {
          refresh_token: refreshToken.value
        })
      }
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      clearTokens()
      loading.value = false
    }
  }

  const refreshAccessToken = async () => {
    if (!refreshToken.value) {
      throw new Error('No refresh token available')
    }

    try {
      const response = await api.post(AUTH_ENDPOINTS.REFRESH, {
        refresh_token: refreshToken.value
      })

      const { access_token, refresh_token: newRefreshToken } = response.data
      setTokens(access_token, newRefreshToken)

      return access_token
    } catch (error) {
      clearTokens()
      throw error
    }
  }

  const loadUserProfile = async () => {
    if (!accessToken.value) return

    try {
      const response = await api.get(AUTH_ENDPOINTS.PROFILE)
      user.value = response.data
    } catch (error: any) {
      if (error.response?.status === 401) {
        // Try to refresh token
        try {
          await refreshAccessToken()
          const response = await api.get(AUTH_ENDPOINTS.PROFILE)
          user.value = response.data
        } catch (refreshError) {
          clearTokens()
        }
      } else {
        console.error('Failed to load user profile:', error)
      }
    }
  }

  // Initialize auth state
  const initialize = async () => {
    if (accessToken.value) {
      await loadUserProfile()
    }
  }

  return {
    // State
    user,
    accessToken,
    refreshToken,
    loading,
    
    // Computed
    isAuthenticated,
    isAdmin,
    isPremium,
    isPro,
    
    // Actions
    login,
    register,
    logout,
    refreshAccessToken,
    loadUserProfile,
    initialize,
    clearTokens
  }
})