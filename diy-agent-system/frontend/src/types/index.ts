// 分析请求类型
export interface AnalysisRequest {
  images: File[]
  description?: string
  projectType?: string
  budgetRange?: string
}

// 材料/工具项目
export interface MaterialItem {
  name: string
  specification?: string
  quantity?: string
  estimated_price_range?: string
  necessity?: string
}

// 图像分析结果
export interface ImageAnalysisResult {
  project_name: string
  description: string
  materials: MaterialItem[]
  tools: MaterialItem[]
  difficulty_level: string
  estimated_time: string
  safety_notes: string[]
  steps: string[]
}

// 产品信息
export interface Product {
  title: string
  price: string
  image_url?: string
  product_url: string
  platform: string
  rating?: number
  quality_score?: number
  quality_reasons?: string[]
  price_value_ratio?: number
  recommendation_level?: string
}

// 产品推荐组
export interface ProductGroup {
  material: string
  products: Product[]
  total_assessed: number
  avg_quality_score?: number
}

// 总体推荐
export interface OverallRecommendations {
  total_products_assessed: number
  average_quality_score: number
  best_products: {
    material: string
    product: Product
  }[]
  shopping_tips: string[]
  quality_distribution: Record<string, number>
}

// 完整的分析结果
export interface AnalysisResult {
  success: boolean
  imageAnalysis: {
    comprehensive_analysis: ImageAnalysisResult
    materials: MaterialItem[]
    tools: MaterialItem[]
    difficulty_level: string
    estimated_time: string
    safety_notes: string[]
  } | null
  productRecommendations: ProductGroup[]
  overallRecommendations: OverallRecommendations | null
  metadata: {
    totalTime: number
    agentsUsed: string[]
  }
}

// Agent状态
export interface AgentStatus {
  name: string
  is_running: boolean
  tasks_completed: number
  config: Record<string, any>
}

// 质量等级配置
export interface QualityLevel {
  level: string
  score_range: [number, number]
  color: string
}