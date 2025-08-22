/**
 * Tool Identification API Service - Cognito Version
 */
import axios from 'axios'
import { useCognitoAuthStore } from '@/stores/cognitoAuth'

// Use Cognito backend for tool identification (now with fixed AUTH)
const API_BASE = import.meta.env.PROD ? 
  (import.meta.env.VITE_API_URL || 'http://localhost:8001') : 
  'http://localhost:8001' // Cognito backend on port 8001

// Create axios instance 
const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add Cognito ID token to requests (optional)
apiClient.interceptors.request.use(
  async (config) => {
    try {
      const authStore = useCognitoAuthStore()
      
      // Only add token if user is authenticated
      if (authStore.isAuthenticated) {
        const token = await authStore.getIdToken()
        
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
          console.log('🔗 API Request with authentication:', config.url)
        } else {
          console.log('⚠️ Authenticated user but no token available:', config.url)
        }
      } else {
        console.log('📱 API Request as guest user:', config.url)
      }
    } catch (error) {
      console.error('Failed to get auth token, proceeding as guest:', error)
      // Continue without token - backend supports guest access
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Handle auth errors
apiClient.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', {
      url: response.config.url,
      status: response.status
    })
    return response
  },
  (error) => {
    console.error('❌ API Error:', {
      status: error.response?.status,
      url: error.config?.url,
      message: error.response?.data?.detail || error.message
    })
    
    if (error.response?.status === 401) {
      console.log('🚫 401 Unauthorized - token may be expired, but backend supports guest access')
      // For Tool Identification, 401 errors shouldn't happen with optional auth
      // This indicates a backend configuration issue
    }
    return Promise.reject(error)
  }
)

/**
 * Identify tool from image using Cognito backend
 */
export async function identifyToolAPI(
  imageFile: File,
  includeAlternatives: boolean = true
): Promise<any> {
  console.log('🔍 Starting tool identification...')
  const formData = new FormData()
  formData.append('images', imageFile)  // Backend expects 'images' not 'image'
  
  const response = await apiClient.post('/api/tool-identification/analyze', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  return response.data
}

/**
 * Get identification history from Cognito backend
 */
export async function getIdentificationHistory(limit: number = 10): Promise<any> {
  console.log('📚 Fetching identification history...')
  const response = await apiClient.get('/api/tool-identification/history', {
    params: { limit }
  })
  return response.data
}

/**
 * Delete identification from history
 */
export async function deleteIdentification(identificationId: string): Promise<any> {
  console.log('🗑️ Deleting identification:', identificationId)
  const response = await apiClient.delete(`/api/tool-identification/history/${identificationId}`)
  return response.data
}

export default apiClient