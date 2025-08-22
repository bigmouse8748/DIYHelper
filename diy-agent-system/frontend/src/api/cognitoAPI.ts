/**
 * API Client for Cognito-authenticated backend
 */
import axios from 'axios'
import { useCognitoAuthStore } from '@/stores/cognitoAuth'

// Backend URL - using new Cognito-enabled backend on port 8001
const API_BASE = import.meta.env.PROD ? 
  (import.meta.env.VITE_API_URL || 'http://localhost:8001') : 
  'http://localhost:8001'

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 30000
})

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  async (config) => {
    const authStore = useCognitoAuthStore()
    
    // Try to get ID token for API authentication
    const idToken = await authStore.getIdToken()
    
    if (idToken) {
      config.headers.Authorization = `Bearer ${idToken}`
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle auth errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      const authStore = useCognitoAuthStore()
      await authStore.logout()
    }
    return Promise.reject(error)
  }
)

// ============================================
// DIY Assistant APIs
// ============================================

/**
 * Analyze DIY project from images
 */
export async function analyzeProject(
  images: File[],
  description?: string,
  projectType?: string,
  budgetRange?: string
): Promise<any> {
  const formData = new FormData()
  
  images.forEach(image => {
    formData.append('images', image)
  })
  
  if (description) formData.append('description', description)
  if (projectType) formData.append('project_type', projectType)
  if (budgetRange) formData.append('budget_range', budgetRange)

  const response = await apiClient.post('/analyze-project', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  
  return response.data
}

// ============================================
// Tool Identification APIs
// ============================================

/**
 * Analyze tools from uploaded images
 */
export async function analyzeTools(images: File[]): Promise<any> {
  const formData = new FormData()
  
  images.forEach(image => {
    formData.append('images', image)
  })

  const response = await apiClient.post('/api/tool-identification/analyze', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  
  return response.data
}

// ============================================
// User Management APIs
// ============================================

/**
 * Get current user information
 */
export async function getCurrentUser(): Promise<any> {
  const response = await apiClient.get('/api/auth/me')
  return response.data
}

// ============================================
// Admin APIs
// ============================================

/**
 * Upgrade user to a different group (admin only)
 */
export async function upgradeUserGroup(email: string, newGroup: string): Promise<any> {
  const formData = new FormData()
  formData.append('email', email)
  formData.append('new_group', newGroup)

  const response = await apiClient.post('/api/admin/upgrade-user', formData)
  return response.data
}

/**
 * List all users (admin only)
 */
export async function listAllUsers(limit: number = 50): Promise<any> {
  const response = await apiClient.get('/api/admin/users', {
    params: { limit }
  })
  return response.data
}

/**
 * Get system statistics (admin only)
 */
export async function getSystemStats(): Promise<any> {
  const response = await apiClient.get('/api/admin/stats')
  return response.data
}

// ============================================
// Health Check APIs
// ============================================

/**
 * Test API connectivity
 */
export async function testAPI(): Promise<any> {
  const response = await apiClient.get('/api/test')
  return response.data
}

/**
 * Health check
 */
export async function healthCheck(): Promise<any> {
  const response = await apiClient.get('/api/health')
  return response.data
}

export default apiClient