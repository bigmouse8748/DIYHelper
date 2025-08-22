/**
 * Debug API calls for authentication testing
 */

import axios from 'axios'
import { useCognitoAuthStore } from '@/stores/cognitoAuth'

const API_BASE_URL = 'http://localhost:8001'

// Create axios instance with auth interceptor
const debugApi = axios.create({
  baseURL: API_BASE_URL,
})

// Add auth token to requests
debugApi.interceptors.request.use(async (config) => {
  const authStore = useCognitoAuthStore()
  const token = await authStore.getIdToken()
  
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  
  console.log('🔗 Making API request:', {
    url: config.url,
    method: config.method,
    hasToken: !!token,
    tokenPreview: token ? token.substring(0, 50) + '...' : null
  })
  
  return config
})

// Debug auth endpoint
export const debugAuth = async () => {
  try {
    console.log('🐛 Calling debug auth endpoint...')
    const response = await debugApi.get('/api/auth/debug')
    console.log('✅ Debug auth response:', response.data)
    return response.data
  } catch (error: any) {
    console.error('❌ Debug auth failed:', error.response?.data || error.message)
    throw error
  }
}