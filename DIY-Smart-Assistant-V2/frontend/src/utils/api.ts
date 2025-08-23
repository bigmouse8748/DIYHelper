import axios from 'axios'
import type { AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'

// Get API URL from environment variable or use default for local development  
const API_BASE_URL = 'https://api.cheasydiy.com' // Temporary hardcode for production deployment fix

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // Increase timeout to 2 minutes for AI analysis
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Add auth token if available
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

// Response interceptor
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          // Token expired or invalid
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          ElMessage.error('Session expired. Please login again.')
          // Redirect to login page
          window.location.href = '/auth/login'
          break
        case 403:
          ElMessage.error('Access denied')
          break
        case 404:
          ElMessage.error('Resource not found')
          break
        case 500:
          ElMessage.error('Internal server error')
          break
        default:
          ElMessage.error(data?.detail || 'An error occurred')
      }
    } else if (error.request) {
      ElMessage.error('Network error. Please check your connection.')
    } else {
      ElMessage.error('Request failed')
    }
    
    return Promise.reject(error)
  }
)

export default api

// API endpoints
export const AUTH_ENDPOINTS = {
  LOGIN: '/api/v1/auth/login',
  REGISTER: '/api/v1/auth/register',
  REFRESH: '/api/v1/auth/refresh',
  LOGOUT: '/api/v1/auth/logout',
  PROFILE: '/api/v1/users/profile'
}

export const AGENT_ENDPOINTS = {
  TOOL_IDENTIFICATION: '/api/v1/agents/tool-identification/analyze',
  PRODUCT_RECOMMENDATION: '/api/v1/agents/product-recommendation/analyze',
  PROJECT_ANALYSIS: '/api/v1/agents/project/analyze',
  AGENT_STATUS: '/api/v1/agents/status',
  AVAILABLE_AGENTS: '/api/v1/agents/available'
}