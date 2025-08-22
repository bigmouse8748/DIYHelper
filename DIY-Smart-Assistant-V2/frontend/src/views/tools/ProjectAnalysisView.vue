<template>
  <div class="project-analysis">
    <div class="page-header">
      <h1 class="page-title">Project Analysis</h1>
      <p class="page-subtitle">Complete analysis of your DIY projects with step-by-step guidance</p>
    </div>

    <el-row :gutter="20">
      <!-- Upload Section -->
      <el-col :xs="24" :lg="12">
        <el-card class="upload-card">
          <template #header>
            <h3>Upload Project Images</h3>
          </template>
          
          <el-upload
            ref="uploadRef"
            class="upload-dragger"
            drag
            multiple
            :auto-upload="false"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            :before-upload="beforeUpload"
            accept="image/*"
            :limit="5"
            :file-list="fileList"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              Drop multiple images here or click to upload
            </div>
            <template #tip>
              <div class="el-upload__tip">
                jpg/png files with size less than 10MB each. Maximum 5 images.
              </div>
            </template>
          </el-upload>
          
          <!-- Project Details Form -->
          <el-form
            v-if="fileList.length > 0"
            ref="formRef"
            :model="projectForm"
            label-position="top"
            style="margin-top: 20px"
          >
            <el-form-item label="Project Description (Optional)">
              <el-input
                v-model="projectForm.description"
                type="textarea"
                :rows="3"
                placeholder="Describe your project goals and any specific requirements..."
              />
            </el-form-item>
            
            <el-form-item label="Project Type">
              <el-select v-model="projectForm.projectType" style="width: 100%">
                <el-option label="General" value="general" />
                <el-option label="Woodworking" value="woodworking" />
                <el-option label="Electronics" value="electronics" />
                <el-option label="Plumbing" value="plumbing" />
                <el-option label="Painting" value="painting" />
                <el-option label="Home Renovation" value="renovation" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="Budget Range">
              <el-select v-model="projectForm.budgetRange" style="width: 100%">
                <el-option label="Under $100" value="low" />
                <el-option label="$100 - $500" value="medium" />
                <el-option label="$500 - $1000" value="high" />
                <el-option label="Over $1000" value="premium" />
              </el-select>
            </el-form-item>
          </el-form>
          
          <div class="upload-actions" v-if="fileList.length > 0">
            <el-button 
              type="primary" 
              size="large"
              :loading="loading"
              @click="analyzeProject"
              style="width: 100%"
              :disabled="loading"
            >
              <el-icon><DataAnalysis /></el-icon>
              {{ loading ? 'Analyzing Project...' : 'Analyze Project' }}
            </el-button>
            
            <!-- Fancy Progress Bar -->
            <div v-if="loading" class="fancy-progress-container" style="margin-top: 16px;">
              <div class="progress-header">
                <div class="progress-icon">
                  <el-icon class="spinning-icon"><Loading /></el-icon>
                </div>
                <div class="progress-text">
                  <div class="progress-title">AI Analysis in Progress</div>
                  <div class="progress-status">{{ analysisStatus }}</div>
                </div>
              </div>
              
              <div class="custom-progress-bar">
                <div class="progress-track">
                  <div 
                    class="progress-fill" 
                    :style="{ width: Math.round(analysisProgress) + '%' }"
                  ></div>
                  <div class="progress-glow"></div>
                </div>
                <div class="progress-dots">
                  <div 
                    v-for="(n, index) in [1, 2, 3, 4, 5]" 
                    :key="`dot-${index}`" 
                    class="progress-dot"
                    :class="{ active: Math.round(analysisProgress) >= n * 20 }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <!-- Preview Section -->
      <el-col :xs="24" :lg="12" v-if="fileList.length > 0">
        <el-card class="preview-card">
          <template #header>
            <h3>Image Previews ({{ fileList.length }})</h3>
          </template>
          
          <div class="image-gallery">
            <div 
              v-for="(file, index) in fileList" 
              :key="`file-${index}`"
              class="preview-item"
            >
              <el-image 
                :src="getPreviewUrl(file)" 
                fit="contain" 
                class="preview-image"
                :preview-src-list="previewList"
                :lazy="true"
              />
              <div class="image-name">{{ file.name }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Results Section -->
    <div v-if="analysisResult" class="results-section">
      <h2 class="section-title">Analysis Results</h2>
      
      <!-- Project Overview -->
      <el-card class="overview-card">
        <template #header>
          <h3>Project Overview</h3>
        </template>
        
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Project Name">
            {{ analysisResult.comprehensive_analysis.project_name }}
          </el-descriptions-item>
          <el-descriptions-item label="Project Type">
            {{ analysisResult.comprehensive_analysis.project_type }}
          </el-descriptions-item>
          <el-descriptions-item label="Difficulty Level">
            <el-tag :type="getDifficultyColor(analysisResult.comprehensive_analysis.difficulty_level)">
              {{ analysisResult.comprehensive_analysis.difficulty_level?.toUpperCase() }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Estimated Time">
            {{ analysisResult.comprehensive_analysis.estimated_time }}
          </el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">
            {{ analysisResult.comprehensive_analysis.description }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
      
      <el-row :gutter="20">
        <!-- Tool Identification Results -->
        <el-col :xs="24" :lg="12" v-if="analysisResult.tool_identification">
          <el-card class="result-card">
            <template #header>
              <h3>Tool Identification</h3>
            </template>
            
            <div class="tool-info">
              <h4>{{ analysisResult.tool_identification.tool_info.name }}</h4>
              <p><strong>Brand:</strong> {{ analysisResult.tool_identification.tool_info.brand || 'Unknown' }}</p>
              <p><strong>Model:</strong> {{ analysisResult.tool_identification.tool_info.model || 'Unknown' }}</p>
              <p><strong>Category:</strong> {{ analysisResult.tool_identification.tool_info.category }}</p>
              
              <div class="confidence-meter">
                <span>Confidence: </span>
                <el-progress 
                  :percentage="Math.round(analysisResult.tool_identification.tool_info.confidence * 100)"
                  :color="getConfidenceColor(analysisResult.tool_identification.tool_info.confidence)"
                />
              </div>
              
              <div v-if="analysisResult.tool_identification.shopping_links" class="shopping-links">
                <h5>Shopping Options:</h5>
                <div class="link-list">
                  <div 
                    v-for="(link, index) in analysisResult.tool_identification.shopping_links.slice(0, 3)" 
                    :key="`link-${index}`"
                    class="shopping-link"
                  >
                    <span class="retailer">{{ link.retailer }}</span>
                    <span class="price">${{ link.price }}</span>
                    <el-button size="small" text @click="openLink(link.url)">
                      View
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <!-- Materials & Tools Summary -->
        <el-col :xs="24" :lg="12" v-if="analysisResult.comprehensive_analysis">
          <el-card class="result-card">
            <template #header>
              <h3>Materials & Tools</h3>
            </template>
            
            <div class="materials-section">
              <h5>Materials Needed:</h5>
              <div v-for="(material, index) in analysisResult.comprehensive_analysis.materials.slice(0, 3)" 
                   :key="`material-${index}`" class="material-item">
                <div class="material-header">
                  <span class="material-name">{{ material.name }}</span>
                  <span class="material-price">{{ material.estimated_price_range }}</span>
                </div>
                <div class="material-details">
                  <span class="material-spec">{{ material.specification }}</span>
                  <span class="material-qty">Qty: {{ material.quantity }}</span>
                </div>
              </div>
            </div>
            
            <div class="tools-section" style="margin-top: 20px;">
              <h5>Tools Required:</h5>
              <div v-for="(tool, index) in analysisResult.comprehensive_analysis.tools.slice(0, 4)" 
                   :key="`tool-${index}`" class="tool-item">
                <span class="tool-name">{{ tool.name }}</span>
                <el-tag :type="tool.necessity === 'Essential' ? 'danger' : 'warning'" size="small">
                  {{ tool.necessity }}
                </el-tag>
              </div>
            </div>
            
            <div v-if="analysisResult.product_recommendations?.overall_recommendations?.shopping_tips" class="shopping-tips">
              <h5>Shopping Tips:</h5>
              <ul>
                <li v-for="(tip, index) in analysisResult.product_recommendations.overall_recommendations.shopping_tips.slice(0, 3)" :key="`tip-${index}`">
                  {{ tip }}
                </li>
              </ul>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- Safety Notes -->
      <el-card v-if="analysisResult.comprehensive_analysis?.safety_notes" class="safety-card">
        <template #header>
          <h3>
            <el-icon style="color: #f56c6c;"><WarningFilled /></el-icon>
            Safety Notes
          </h3>
        </template>
        
        <el-alert
          v-for="(note, index) in analysisResult.comprehensive_analysis.safety_notes"
          :key="`note-${index}`"
          :title="note"
          type="warning"
          :closable="false"
          style="margin-bottom: 12px;"
        />
      </el-card>
      
      <!-- Build Steps -->
      <el-card v-if="analysisResult.comprehensive_analysis?.steps" class="steps-card">
        <template #header>
          <h3>Build Steps</h3>
        </template>
        
        <el-steps 
          :active="analysisResult.comprehensive_analysis.steps.length" 
          direction="vertical"
        >
          <el-step 
            v-for="(step, index) in analysisResult.comprehensive_analysis.steps"
            :key="`step-${index}`"
            :title="`Step ${index + 1}`"
            :description="step"
          />
        </el-steps>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage, type UploadProps, type UploadUserFile } from 'element-plus'
import { UploadFilled, DataAnalysis, WarningFilled, Loading } from '@element-plus/icons-vue'
import api, { AGENT_ENDPOINTS } from '@/utils/api'

interface ProjectAnalysisResult {
  comprehensive_analysis: {
    project_name: string
    project_type: string
    description: string
    materials: Array<{
      name: string
      specification: string
      quantity: string
      estimated_price_range: string
    }>
    tools: Array<{
      name: string
      necessity: string
    }>
    difficulty_level: string
    estimated_time: string
    safety_notes: string[]
    steps: string[]
  }
  tool_identification?: {
    tool_info: {
      name: string
      brand?: string
      model?: string
      category: string
      confidence: number
    }
    shopping_links?: Array<{
      retailer: string
      price: number
      url: string
    }>
  }
  product_recommendations?: {
    assessed_results: Array<{
      material: string
      category: string
      products: Array<{
        title: string
        price: string
        platform: string
        rating: number
        quality_score: number
        product_url: string
      }>
    }>
    overall_recommendations: {
      total_products_assessed: number
      average_quality_score: number
      shopping_tips: string[]
      budget_breakdown: {
        estimated_total: string
      }
    }
  }
}

const uploadRef = ref()
const formRef = ref()
const fileList = ref<UploadUserFile[]>([])
const loading = ref(false)
const analysisResult = ref<ProjectAnalysisResult | null>(null)
const analysisProgress = ref(0)
const analysisStatus = ref('')

const projectForm = ref({
  description: '',
  projectType: 'general',
  budgetRange: 'medium'
})

const previewList = computed(() => 
  fileList.value.map(file => getPreviewUrl(file)).filter(Boolean) as string[]
)

const handleFileChange: UploadProps['onChange'] = (uploadFile: UploadUserFile, uploadFiles: UploadUserFile[]) => {
  fileList.value = uploadFiles.filter(file => file.status !== 'fail')
  
  // Generate preview URL for the uploaded file if it doesn't have one
  fileList.value.forEach(file => {
    if (file.raw && !file.url) {
      const reader = new FileReader()
      reader.onload = (e) => {
        file.url = e.target?.result as string
      }
      reader.readAsDataURL(file.raw)
    }
  })
}

const handleFileRemove: UploadProps['onRemove'] = (file: UploadUserFile) => {
  const index = fileList.value.indexOf(file)
  if (index > -1) {
    fileList.value.splice(index, 1)
  }
}

const beforeUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isImage) {
    ElMessage.error('Please upload image files only!')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('Image size must be less than 10MB!')
    return false
  }
  return true
}

const analyzeProject = async () => {
  if (fileList.value.length === 0) {
    ElMessage.error('Please upload at least one image')
    return
  }

  // Reset progress
  loading.value = true
  analysisProgress.value = 0
  analysisStatus.value = 'Preparing images for analysis...'
  
  console.log('Starting project analysis...')
  console.log('Files to upload:', fileList.value.length)
  console.log('Project form:', projectForm.value)
  
  try {
    // Progress: 10% - Preparing data
    analysisProgress.value = 10
    analysisStatus.value = 'Processing images...'
    
    const formData = new FormData()
    
    // Add images
    let imageCount = 0
    fileList.value.forEach((file, index) => {
      console.log(`Processing file ${index + 1}:`, file)
      if (file.raw) {
        formData.append('images', file.raw)
        imageCount++
        console.log(`Added image ${index + 1}: ${file.name}, size: ${file.raw.size} bytes`)
      } else {
        console.log(`Skipping file ${index + 1}: no raw file data`)
      }
    })
    
    console.log(`Total images added to FormData: ${imageCount}`)
    
    // Progress: 25% - Images processed
    analysisProgress.value = 25
    analysisStatus.value = 'Uploading to AI analysis service...'
    
    // Add project details
    formData.append('description', projectForm.value.description || '')
    formData.append('project_type', projectForm.value.projectType)
    formData.append('budget_range', projectForm.value.budgetRange)
    
    console.log('Making API call to:', AGENT_ENDPOINTS.PROJECT_ANALYSIS)
    console.log('FormData contents:')
    for (let [key, value] of formData.entries()) {
      if (value instanceof File) {
        console.log(`${key}: File - ${value.name}, size: ${value.size}, type: ${value.type}`)
      } else {
        console.log(`${key}: ${value}`)
      }
    }
    
    console.log('About to make axios POST request...')
    console.log('Total image files to send:', imageCount)
    
    // Progress: 40% - Starting API call
    analysisProgress.value = 40
    analysisStatus.value = 'AI is analyzing your project...'

    // Create a progress simulation for long-running analysis
    const progressInterval = setInterval(() => {
      if (analysisProgress.value < 85) {
        analysisProgress.value = Math.min(85, analysisProgress.value + Math.floor(Math.random() * 8) + 2)
        const messages = [
          'Identifying materials and tools...',
          'Calculating project difficulty...',
          'Finding product recommendations...',
          'Generating safety guidelines...',
          'Creating step-by-step instructions...'
        ]
        analysisStatus.value = messages[Math.floor(Math.random() * messages.length)]
      }
    }, 2000)

    const response = await api.post(AGENT_ENDPOINTS.PROJECT_ANALYSIS, formData, {
      // Let browser set Content-Type with boundary for multipart/form-data
      // Use global timeout of 120 seconds from api.ts for AI analysis
    })

    // Clear progress interval
    clearInterval(progressInterval)
    
    // Progress: 95% - Processing response
    analysisProgress.value = 95
    analysisStatus.value = 'Finalizing results...'

    console.log('API Response:', response)

    if (response.data.success) {
      // Progress: 100% - Complete
      analysisProgress.value = 100
      analysisStatus.value = 'Analysis complete!'
      
      setTimeout(() => {
        // Deep clone to avoid any reactive issues with complex nested data
        analysisResult.value = JSON.parse(JSON.stringify(response.data.data))
        console.log('Analysis result:', response.data.data)
        // ElMessage.success('Project analysis completed successfully!')
        console.log('Project analysis completed successfully!')
      }, 500)
    } else {
      clearInterval(progressInterval)
      console.error('Analysis failed:', response.data)
      // ElMessage.error('Analysis failed')
      alert('Analysis failed')
    }
  } catch (error: any) {
    // Clear progress interval on error
    if (typeof progressInterval !== 'undefined') {
      clearInterval(progressInterval)
    }
    
    console.error('Analysis error:', error)
    console.error('Error response:', error.response)
    console.error('Error status:', error.response?.status)
    console.error('Error data:', error.response?.data)
    console.error('Error code:', error.code)
    console.error('Error config:', error.config)
    
    analysisProgress.value = 0
    analysisStatus.value = ''
    
    // Provide specific error messages based on error type
    let errorMessage = 'Analysis failed'
    if (error.code === 'ECONNABORTED') {
      errorMessage = 'Analysis timed out. Please try with smaller images or try again later.'
    } else if (error.response?.status === 422) {
      errorMessage = 'Invalid request format. Please check your images and try again.'
    } else if (error.response?.status === 500) {
      errorMessage = 'Server error. Please try again later.'
    } else if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail
    } else if (error.message) {
      errorMessage = error.message
    }
    
    // Temporarily use alert instead of ElMessage to avoid setAttribute error
    alert(errorMessage)
    console.error('Error message:', errorMessage)
  } finally {
    setTimeout(() => {
      loading.value = false
      analysisProgress.value = 0
      analysisStatus.value = ''
    }, 1000) // Keep progress visible briefly after completion
  }
}

const getDifficultyColor = (difficulty: string) => {
  switch (difficulty?.toLowerCase()) {
    case 'easy': return 'success'
    case 'medium': case 'intermediate': return 'warning'
    case 'hard': case 'difficult': return 'danger'
    default: return 'info'
  }
}

const getConfidenceColor = (confidence: number) => {
  if (confidence >= 0.8) return '#67c23a'
  if (confidence >= 0.6) return '#e6a23c'
  return '#f56c6c'
}

const getPriorityColor = (priority: string) => {
  switch (priority?.toLowerCase()) {
    case 'essential': return 'danger'
    case 'recommended': return 'warning'
    case 'optional': return 'info'
    default: return 'primary'
  }
}

const getPreviewUrl = (file: UploadUserFile): string => {
  if (file.url) {
    return file.url
  }
  
  if (file.raw) {
    try {
      // Check if URL.createObjectURL is available (most modern browsers)
      if (typeof window !== 'undefined' && window.URL && window.URL.createObjectURL) {
        return window.URL.createObjectURL(file.raw)
      } else if (typeof URL !== 'undefined' && URL.createObjectURL) {
        return URL.createObjectURL(file.raw)
      } else {
        console.warn('URL.createObjectURL not available, using FileReader fallback')
        // This won't work for immediate display, but will set the URL asynchronously
        if (!file._readerInProgress) {
          file._readerInProgress = true
          const reader = new FileReader()
          reader.onload = (e) => {
            file.url = e.target?.result as string
            file._readerInProgress = false
          }
          reader.onerror = () => {
            file._readerInProgress = false
          }
          reader.readAsDataURL(file.raw)
        }
        return '' // Return empty string while loading
      }
    } catch (error) {
      console.warn('Failed to create preview URL:', error)
      return ''
    }
  }
  
  return ''
}

const openLink = (url: string) => {
  window.open(url, '_blank')
}
</script>

<style scoped>
.project-analysis {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: #303133;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 16px;
  color: #606266;
  margin: 0;
}

.upload-card, .preview-card, .overview-card, .result-card, .safety-card {
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.upload-dragger {
  width: 100%;
}

.upload-actions {
  margin-top: 20px;
}

.image-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
}

.preview-item {
  display: flex;
  flex-direction: column;
  padding: 8px;
  border-radius: 8px;
  background: #fafbfc;
}

.preview-image {
  width: 100%;
  height: 150px;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.image-name {
  font-size: 12px;
  color: #909399;
  text-align: center;
  margin-top: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.results-section {
  margin-top: 30px;
}

.section-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 20px 0;
}

.tool-info {
  padding: 16px 0;
}

.tool-info h4 {
  margin: 0 0 12px 0;
  color: #303133;
}

.tool-info p {
  margin: 4px 0;
  color: #606266;
}

.confidence-meter {
  margin: 16px 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.shopping-links h5, .shopping-tips h5 {
  margin: 16px 0 8px 0;
  color: #303133;
}

.link-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.shopping-link {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 6px;
}

.retailer {
  font-weight: 600;
  color: #303133;
}

.price {
  color: #67c23a;
  font-weight: 600;
}

.recommendations-summary {
  margin-bottom: 16px;
}

.recommendations-summary p {
  margin: 4px 0;
  color: #606266;
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.recommendation-item {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
}

.rec-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.rec-name {
  font-weight: 600;
  color: #303133;
}

.rec-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.rec-price {
  color: #67c23a;
  font-weight: 600;
}

.rec-category {
  color: #909399;
  font-size: 12px;
}

.shopping-tips ul {
  margin: 0;
  padding-left: 16px;
}

.shopping-tips li {
  margin: 4px 0;
  color: #606266;
  font-size: 14px;
}

.materials-section h5, .tools-section h5 {
  margin: 16px 0 8px 0;
  color: #303133;
  font-weight: 600;
}

.material-item, .tool-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 6px;
  margin-bottom: 8px;
}

.material-header, .material-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.material-name, .tool-name {
  font-weight: 600;
  color: #303133;
}

.material-price {
  color: #67c23a;
  font-size: 12px;
  font-weight: 600;
}

.material-spec, .material-qty {
  color: #909399;
  font-size: 12px;
}

.tool-item {
  background: #f0f9ff;
  border-left: 3px solid #409eff;
}

.safety-card :deep(.el-card__header) {
  background: #fef0f0;
  border-bottom: 1px solid #fbc4c4;
}

.steps-card {
  margin-top: 20px;
}

/* Fancy Progress Bar Styles */
.fancy-progress-container {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
  color: white;
  position: relative;
  overflow: hidden;
}

.fancy-progress-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { left: -100%; }
  100% { left: 100%; }
}

.progress-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.progress-icon {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
}

.spinning-icon {
  font-size: 20px;
  animation: spin 2s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.progress-text {
  flex: 1;
}

.progress-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
}

.progress-status {
  font-size: 14px;
  opacity: 0.9;
  font-weight: 400;
}

.custom-progress-bar {
  position: relative;
}

.progress-track {
  height: 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  position: relative;
  overflow: hidden;
  margin-bottom: 12px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #00f5ff, #00d4ff, #0099ff);
  border-radius: 4px;
  transition: width 0.3s ease;
  position: relative;
  box-shadow: 0 0 10px rgba(0, 149, 255, 0.5);
}

.progress-fill::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 20px;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.6));
  animation: progress-glow 1.5s ease-in-out infinite alternate;
}

@keyframes progress-glow {
  from { opacity: 0.5; }
  to { opacity: 1; }
}

.progress-dots {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
}

.progress-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
  position: relative;
}

.progress-dot.active {
  background: #00f5ff;
  box-shadow: 0 0 15px rgba(0, 245, 255, 0.7);
  transform: scale(1.2);
}

.progress-dot.active::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  border-radius: 50%;
  border: 2px solid rgba(0, 245, 255, 0.3);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(0.8); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.5; }
}

/* Responsive Design */
@media (max-width: 768px) {
  .image-gallery {
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  }
  
  .shopping-link {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .rec-header, .rec-details {
    flex-direction: column;
    align-items: stretch;
    gap: 4px;
  }
}
</style>