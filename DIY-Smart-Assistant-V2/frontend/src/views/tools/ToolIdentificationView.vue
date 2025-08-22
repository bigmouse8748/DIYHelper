<template>
  <div class="tool-identification">
    <div class="page-header">
      <h1 class="page-title">Tool Identification</h1>
      <p class="page-subtitle">Upload an image to identify any tool instantly</p>
    </div>

    <el-row :gutter="20">
      <!-- Upload Section -->
      <el-col :xs="24" :lg="12">
        <el-card class="upload-card">
          <template #header>
            <h3>Upload Tool Image</h3>
          </template>
          
          <el-upload
            ref="uploadRef"
            class="upload-dragger"
            drag
            :auto-upload="false"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            :on-exceed="handleFileExceed"
            :before-upload="beforeUpload"
            accept="image/*"
            :limit="1"
            :show-file-list="true"
            list-type="picture"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text" v-if="!selectedFile">
              Drop image here or <em>click to upload</em>
            </div>
            <div class="el-upload__text" v-else style="color: #409eff;">
              Drop new image to <em>replace current one</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                JPG, PNG files up to 10MB<br/>
                <small style="color: #909399;">New images will automatically replace the current one</small>
              </div>
            </template>
          </el-upload>
          
          <div class="upload-actions" v-if="selectedFile">
            <el-button 
              type="primary" 
              size="large"
              :loading="loading"
              @click="analyzeImage"
              style="width: 100%; margin-bottom: 8px;"
              :disabled="loading"
            >
              <el-icon><Search /></el-icon>
              {{ loading ? 'Analyzing Tool...' : 'Identify Tool' }}
            </el-button>
            
            <!-- Help text for slow analysis -->
            <el-alert
              v-if="!loading && !analysisResult"
              title="AI Analysis Tips"
              type="info"
              :closable="false"
              show-icon
              style="margin-top: 8px;"
            >
              <template #default>
                <div style="font-size: 13px;">
                  <p>• Analysis may take 1-2 minutes for high accuracy</p>
                  <p>• Clear, well-lit images work best</p>
                  <p>• If timeout occurs, try a smaller image or retry</p>
                </div>
              </template>
            </el-alert>
            
            <!-- Fancy Progress Bar -->
            <div v-if="loading" class="fancy-progress-container" style="margin-top: 16px;">
              <div class="progress-header">
                <div class="progress-icon">
                  <el-icon class="spinning-icon"><Loading /></el-icon>
                </div>
                <div class="progress-text">
                  <div class="progress-title">AI Tool Identification</div>
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
                    v-for="n in 5" 
                    :key="n" 
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
      <el-col :xs="24" :lg="12" v-if="selectedFile">
        <el-card class="preview-card">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <h3>Image Preview</h3>
              <el-tooltip content="Drag and drop or click upload area to replace image">
                <el-tag size="small" type="info">Auto-replace enabled</el-tag>
              </el-tooltip>
            </div>
          </template>
          
          <div class="image-preview">
            <el-image 
              :src="imagePreview" 
              fit="cover" 
              class="preview-image"
              :preview-src-list="[imagePreview]"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Results Section -->
    <div v-if="analysisResult" class="results-section">
      <h2 class="section-title">Analysis Results</h2>
      
      <el-row :gutter="20">
        <!-- Tool Information -->
        <el-col :xs="24" :lg="12">
          <el-card class="result-card">
            <template #header>
              <h3>Tool Information</h3>
            </template>
            
            <el-descriptions :column="1" border>
              <el-descriptions-item label="Tool Name">
                {{ analysisResult.tool_info.name }}
              </el-descriptions-item>
              <el-descriptions-item label="Brand" v-if="analysisResult.tool_info.brand">
                {{ analysisResult.tool_info.brand }}
              </el-descriptions-item>
              <el-descriptions-item label="Model" v-if="analysisResult.tool_info.model">
                {{ analysisResult.tool_info.model }}
              </el-descriptions-item>
              <el-descriptions-item label="Category">
                <el-tag>{{ analysisResult.tool_info.category }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="Confidence">
                <el-progress 
                  :percentage="Math.round(analysisResult.tool_info.confidence * 100)"
                  :color="getConfidenceColor(analysisResult.tool_info.confidence)"
                />
              </el-descriptions-item>
            </el-descriptions>
            
            <!-- Specifications -->
            <div v-if="Object.keys(analysisResult.tool_info.specifications).length > 0" class="specifications">
              <h4>Specifications</h4>
              <el-tag 
                v-for="(value, key) in analysisResult.tool_info.specifications" 
                :key="key"
                class="spec-tag"
              >
                {{ key }}: {{ value }}
              </el-tag>
            </div>
          </el-card>
        </el-col>
        
        <!-- Shopping Links -->
        <el-col :xs="24" :lg="12">
          <el-card class="result-card">
            <template #header>
              <h3>Where to Buy</h3>
            </template>
            
            <div class="shopping-links">
              <div 
                v-for="link in analysisResult.shopping_links" 
                :key="link.url"
                class="shopping-item"
              >
                <div class="shopping-info">
                  <div class="shopping-header">
                    <span class="retailer">{{ link.retailer }}</span>
                    <el-tag v-if="link.is_exact_match" type="success" size="small">
                      Exact Match
                    </el-tag>
                  </div>
                  <div class="product-title">{{ link.title }}</div>
                  <div class="product-details">
                    <span class="price">${{ link.price }}</span>
                    <el-tag 
                      v-if="link.in_stock" 
                      type="success" 
                      size="small"
                    >
                      In Stock
                    </el-tag>
                  </div>
                </div>
                <el-button 
                  type="primary" 
                  size="small"
                  @click="openShoppingLink(link.url)"
                >
                  View Product
                </el-button>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- Alternatives -->
      <div v-if="analysisResult.alternatives && analysisResult.alternatives.length > 0" class="alternatives-section">
        <el-card class="result-card">
          <template #header>
            <h3>Alternative Tools</h3>
          </template>
          
          <el-row :gutter="16">
            <el-col 
              :xs="24" :sm="12" :md="8" 
              v-for="alternative in analysisResult.alternatives" 
              :key="alternative.name"
            >
              <div class="alternative-item">
                <h4>{{ alternative.name }}</h4>
                <p><strong>Model:</strong> {{ alternative.model }}</p>
                <p><strong>Price Range:</strong> {{ alternative.price_range }}</p>
                <p class="reason">{{ alternative.reason }}</p>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage, type UploadProps, type UploadUserFile } from 'element-plus'
import { UploadFilled, Search, Loading } from '@element-plus/icons-vue'
import api, { AGENT_ENDPOINTS } from '@/utils/api'

interface AnalysisResult {
  tool_info: {
    name: string
    brand?: string
    model?: string
    category: string
    confidence: number
    specifications: Record<string, any>
  }
  shopping_links: Array<{
    retailer: string
    title: string
    price: number
    url: string
    image_url: string
    in_stock: boolean
    is_exact_match: boolean
  }>
  alternatives?: Array<{
    name: string
    model: string
    price_range: string
    reason: string
  }>
}

const uploadRef = ref()
const selectedFile = ref<File | null>(null)
const imagePreview = ref<string>('')
const loading = ref(false)
const analysisResult = ref<AnalysisResult | null>(null)
const analysisProgress = ref(0)
const analysisStatus = ref('')

const handleFileChange: UploadProps['onChange'] = (uploadFile: UploadUserFile) => {
  if (uploadFile.raw) {
    // Clear previous results when new file is selected
    analysisResult.value = null
    selectedFile.value = uploadFile.raw
    
    // Create preview URL
    const reader = new FileReader()
    reader.onload = (e) => {
      imagePreview.value = e.target?.result as string
    }
    reader.readAsDataURL(uploadFile.raw)
    
    ElMessage.success('Image uploaded successfully! Click "Identify Tool" to analyze.')
  }
}

const handleFileRemove = () => {
  selectedFile.value = null
  imagePreview.value = ''
  analysisResult.value = null
}

const handleFileExceed: UploadProps['onExceed'] = (files) => {
  // When user tries to upload a new file while one exists, replace the old one
  uploadRef.value?.clearFiles()
  const newFile = files[0]
  
  // Validate the new file first
  if (beforeUpload(newFile)) {
    // Clear previous results
    analysisResult.value = null
    selectedFile.value = newFile
    
    // Create preview URL
    const reader = new FileReader()
    reader.onload = (e) => {
      imagePreview.value = e.target?.result as string
    }
    reader.readAsDataURL(newFile)
    
    // Add the new file to the upload component
    uploadRef.value?.handleStart(newFile)
    
    ElMessage.success('Image replaced successfully! Click "Identify Tool" to analyze.')
  }
}

const beforeUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isImage) {
    ElMessage.error('Please upload an image file!')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('Image size must be less than 10MB!')
    return false
  }
  return true
}

const analyzeImage = async () => {
  if (!selectedFile.value) {
    ElMessage.error('Please select an image first')
    return
  }

  // Reset progress
  loading.value = true
  analysisProgress.value = 0
  analysisStatus.value = 'Preparing image for analysis...'
  
  try {
    // Progress: 10% - Preparing data
    analysisProgress.value = 10
    analysisStatus.value = 'Processing image...'
    
    const formData = new FormData()
    formData.append('image', selectedFile.value)
    formData.append('include_alternatives', 'true')

    // Progress: 25% - Image processed
    analysisProgress.value = 25
    analysisStatus.value = 'Uploading to AI identification service...'
    
    // Progress: 40% - Starting API call
    analysisProgress.value = 40
    analysisStatus.value = 'AI is identifying your tool...'

    // Create a progress simulation for tool identification
    const progressInterval = setInterval(() => {
      if (analysisProgress.value < 85) {
        analysisProgress.value = Math.min(85, analysisProgress.value + Math.floor(Math.random() * 8) + 2)
        const messages = [
          'Analyzing tool shape and features...',
          'Comparing with tool database...',
          'Identifying brand and model...',
          'Finding shopping options...',
          'Generating recommendations...'
        ]
        analysisStatus.value = messages[Math.floor(Math.random() * messages.length)]
      }
    }, 1500)

    const response = await api.post(AGENT_ENDPOINTS.TOOL_IDENTIFICATION, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 120000, // 2 minutes timeout for AI analysis
      onUploadProgress: (progressEvent) => {
        // Update progress for file upload (first 40% of progress)
        if (progressEvent.total) {
          const uploadProgress = Math.round((progressEvent.loaded * 40) / progressEvent.total)
          if (uploadProgress > analysisProgress.value) {
            analysisProgress.value = Math.min(40, uploadProgress)
            analysisStatus.value = 'Uploading image...'
          }
        }
      }
    })

    // Clear progress interval
    clearInterval(progressInterval)
    
    // Progress: 95% - Processing response
    analysisProgress.value = 95
    analysisStatus.value = 'Finalizing results...'

    if (response.data.success) {
      // Progress: 100% - Complete
      analysisProgress.value = 100
      analysisStatus.value = 'Identification complete!'
      
      setTimeout(() => {
        analysisResult.value = response.data.data
        ElMessage.success('Tool identification completed successfully!')
      }, 500)
    } else {
      clearInterval(progressInterval)
      ElMessage.error('Analysis failed')
    }
  } catch (error: any) {
    // Clear progress interval on error
    if (typeof progressInterval !== 'undefined') {
      clearInterval(progressInterval)
    }
    
    console.error('Analysis error:', error)
    
    analysisProgress.value = 0
    analysisStatus.value = ''
    
    // Better error handling based on error type
    if (error.code === 'ECONNABORTED' || error.response?.status === 408) {
      ElMessage.error({
        message: 'AI analysis timed out. The service may be experiencing high load. Please try again with a smaller image.',
        duration: 10000,
        showClose: true
      })
    } else if (error.response?.status === 413) {
      ElMessage.error({
        message: 'Image file is too large. Please compress your image to under 10MB and try again.',
        duration: 6000,
        showClose: true
      })
    } else if (error.response?.status === 429) {
      ElMessage.error({
        message: 'AI service rate limit exceeded. Please wait a few minutes and try again.',
        duration: 8000,
        showClose: true
      })
    } else if (error.response?.status >= 500) {
      ElMessage.error({
        message: 'AI service temporarily unavailable. Please try again in a few minutes.',
        duration: 6000,
        showClose: true
      })
    } else {
      ElMessage.error({
        message: error.response?.data?.detail || error.message || 'Analysis failed. Please check your image and try again.',
        duration: 5000,
        showClose: true
      })
    }
  } finally {
    setTimeout(() => {
      loading.value = false
      analysisProgress.value = 0
      analysisStatus.value = ''
    }, 1000) // Keep progress visible briefly after completion
  }
}

const getConfidenceColor = (confidence: number) => {
  if (confidence >= 0.8) return '#67c23a'
  if (confidence >= 0.6) return '#e6a23c'
  return '#f56c6c'
}

const openShoppingLink = (url: string) => {
  window.open(url, '_blank')
}
</script>

<style scoped>
.tool-identification {
  max-width: 1200px;
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

.upload-card, .preview-card, .result-card {
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.upload-dragger {
  width: 100%;
}

.upload-actions {
  margin-top: 20px;
}

.image-preview {
  text-align: center;
}

.preview-image {
  width: 100%;
  max-width: 400px;
  height: 300px;
  border-radius: 8px;
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

.specifications {
  margin-top: 20px;
}

.specifications h4 {
  margin: 0 0 12px 0;
  color: #303133;
}

.spec-tag {
  margin: 0 8px 8px 0;
}

.shopping-links {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.shopping-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.shopping-item:hover {
  border-color: #667eea;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
}

.shopping-info {
  flex: 1;
  margin-right: 16px;
}

.shopping-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.retailer {
  font-weight: 600;
  color: #303133;
}

.product-title {
  font-size: 14px;
  color: #606266;
  margin-bottom: 4px;
}

.product-details {
  display: flex;
  align-items: center;
  gap: 8px;
}

.price {
  font-weight: 600;
  color: #67c23a;
  font-size: 16px;
}

.alternatives-section {
  margin-top: 20px;
}

.alternative-item {
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: #fafafa;
}

.alternative-item h4 {
  margin: 0 0 8px 0;
  color: #303133;
}

.alternative-item p {
  margin: 4px 0;
  font-size: 14px;
  color: #606266;
}

.alternative-item .reason {
  font-style: italic;
  color: #909399;
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
  .shopping-item {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .shopping-info {
    margin-right: 0;
  }
}
</style>