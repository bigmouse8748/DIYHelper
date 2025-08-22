import axios from 'axios'
import type { AnalysisResult, AnalysisRequest } from '@/types'

// Use backend URL directly since proxy isn't working on port 3003
const API_BASE_URL = import.meta.env.DEV ? 'http://localhost:8001' : (import.meta.env.VITE_API_URL || 'http://localhost:8001')

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5分钟超时，因为AI分析需要时间
  headers: {
    'Content-Type': 'multipart/form-data',
  },
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    console.log('发起API请求:', config.url)
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    console.log('API响应:', response.data)
    return response
  },
  (error) => {
    console.error('API错误:', error)
    return Promise.reject(error)
  }
)

export const analyzeProject = async (request: AnalysisRequest): Promise<AnalysisResult> => {
  const formData = new FormData()
  
  // 添加图片文件
  request.images.forEach((image, index) => {
    formData.append('images', image, `image_${index}.jpg`)
  })
  
  // 添加其他参数
  formData.append('description', request.description || '')
  formData.append('project_type', request.projectType || '')
  formData.append('budget_range', request.budgetRange || '')
  
  const response = await apiClient.post('/analyze-project', formData)
  
  // 处理响应数据，转换为前端需要的格式
  const data = response.data
  
  if (!data.success) {
    throw new Error(data.error || '分析失败')
  }
  
  // 转换后端结果为前端格式
  const results = data.results || []
  const imageAnalysis = results.find((r: any) => r.data?.comprehensive_analysis)
  const productSearch = results.find((r: any) => r.data?.search_results)
  const qualityAssessment = results.find((r: any) => r.data?.assessed_results)
  
  return {
    success: true,
    imageAnalysis: imageAnalysis?.data || null,
    productRecommendations: qualityAssessment?.data?.assessed_results || [],
    overallRecommendations: qualityAssessment?.data?.overall_recommendations || null,
    metadata: {
      totalTime: results.reduce((sum: number, r: any) => sum + (r.execution_time || 0), 0),
      agentsUsed: results.map((r: any) => r.agent_name || 'unknown').filter(Boolean)
    }
  }
}

export const getAgentStatus = async () => {
  const response = await apiClient.get('/agents/status')
  return response.data
}

export const getAnalysisHistory = async () => {
  // 这里可以实现分析历史的获取
  // 目前返回空数组
  return []
}