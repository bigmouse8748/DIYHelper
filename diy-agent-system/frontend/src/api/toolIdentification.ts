/**
 * Tool Identification API Service
 */
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8002'

// Create axios instance with auth interceptor
const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add auth token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Handle auth errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_info')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

/**
 * Identify tool from image
 */
export async function identifyToolAPI(
  imageFile: File,
  includeAlternatives: boolean = true
): Promise<any> {
  const formData = new FormData()
  formData.append('image', imageFile)
  formData.append('include_alternatives', String(includeAlternatives))

  const response = await apiClient.post('/api/identify-tool', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  return response.data
}

/**
 * Get identification history
 */
export async function getIdentificationHistory(limit: number = 10): Promise<any> {
  const response = await apiClient.get('/api/identification-history', {
    params: { limit }
  })
  return response.data
}

/**
 * Delete identification from history
 */
export async function deleteIdentification(identificationId: string): Promise<any> {
  const response = await apiClient.delete(`/api/identification-history/${identificationId}`)
  return response.data
}

/**
 * User authentication APIs
 */
export async function register(email: string, username: string, password: string): Promise<any> {
  const response = await apiClient.post('/api/auth/register', {
    email,
    username,
    password
  })
  return response.data
}

export async function login(username: string, password: string): Promise<any> {
  const formData = new FormData()
  formData.append('username', username)
  formData.append('password', password)

  const response = await apiClient.post('/api/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  })
  return response.data
}

export async function getCurrentUser(): Promise<any> {
  const response = await apiClient.get('/api/auth/me')
  return response.data
}

/**
 * Membership APIs
 */
export async function upgradeMembership(level: 'premium' | 'pro'): Promise<any> {
  const formData = new FormData()
  formData.append('level', level)
  
  const response = await apiClient.post('/api/membership/upgrade', formData)
  return response.data
}

export default apiClient