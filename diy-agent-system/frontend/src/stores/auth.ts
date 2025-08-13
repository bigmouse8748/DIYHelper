/**
 * Authentication Store
 */
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { login, register, getCurrentUser } from '@/api/toolIdentification'

export interface User {
  username: string
  email: string
  membership_level: 'free' | 'premium' | 'pro'
  dailyUsed?: number
  dailyLimit?: number
}

export interface AuthState {
  user: User | null
  token: string | null
  isLoading: boolean
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const isLoading = ref(false)

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const currentUser = computed(() => user.value)
  const membershipLevel = computed(() => user.value?.membership_level || 'free')

  // Actions
  async function loginUser(username: string, password: string) {
    isLoading.value = true
    try {
      const response = await login(username, password)
      
      // Save token and user info
      token.value = response.access_token
      user.value = response.user_info
      
      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('user_info', JSON.stringify(response.user_info))
      
      return response
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Login failed')
    } finally {
      isLoading.value = false
    }
  }

  async function registerUser(email: string, username: string, password: string) {
    isLoading.value = true
    try {
      const response = await register(email, username, password)
      
      // Save token and user info
      token.value = response.access_token
      user.value = response.user_info
      
      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('user_info', JSON.stringify(response.user_info))
      
      return response
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Registration failed')
    } finally {
      isLoading.value = false
    }
  }

  async function loadCurrentUser() {
    if (!token.value) return
    
    isLoading.value = true
    try {
      const userData = await getCurrentUser()
      user.value = userData
      localStorage.setItem('user_info', JSON.stringify(userData))
    } catch (error) {
      console.error('Failed to load current user:', error)
      logout()
    } finally {
      isLoading.value = false
    }
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_info')
  }

  function initializeAuth() {
    const storedToken = localStorage.getItem('access_token')
    const storedUser = localStorage.getItem('user_info')
    
    if (storedToken && storedUser) {
      token.value = storedToken
      try {
        user.value = JSON.parse(storedUser)
        // Refresh user data
        loadCurrentUser()
      } catch (error) {
        console.error('Failed to parse stored user data:', error)
        logout()
      }
    }
  }

  function updateQuota(quotaInfo: { used: number; limit: number; membership: string }) {
    if (user.value) {
      user.value.dailyUsed = quotaInfo.used
      user.value.dailyLimit = quotaInfo.limit
      user.value.membership_level = quotaInfo.membership as 'free' | 'premium' | 'pro'
      localStorage.setItem('user_info', JSON.stringify(user.value))
    }
  }

  return {
    // State
    user,
    token,
    isLoading,
    // Getters
    isAuthenticated,
    currentUser,
    membershipLevel,
    // Actions
    loginUser,
    registerUser,
    loadCurrentUser,
    logout,
    initializeAuth,
    updateQuota
  }
})