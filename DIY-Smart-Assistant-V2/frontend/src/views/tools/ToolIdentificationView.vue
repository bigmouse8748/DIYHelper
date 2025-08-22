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
            :before-upload="beforeUpload"
            accept="image/*"
            :limit="1"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              Text
            </div>
            <template #tip>
              <div class="el-upload__tip">
                Text
              </div>
            </template>
          </el-upload>
          
          <div class="upload-actions" v-if="selectedFile">
            <el-button 
              type="primary" 
              size="large"
              :loading="loading"
              @click="analyzeImage"
              style="width: 100%"
            >
              <el-icon><Search /></el-icon>
              {{ loading ? "Text" : "Text" }}
            </el-button>
          </div>
        </el-card>
      </el-col>
      
      <!-- Preview Section -->
      <el-col :xs="24" :lg="12" v-if="selectedFile">
        <el-card class="preview-card">
          <template #header>
            <h3>Image Preview</h3>
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
      <h2 class="section-title">Text</h2>
      
      <el-row :gutter="20">
        <!-- Tool Information -->
        <el-col :xs="24" :lg="12">
          <el-card class="result-card">
            <template #header>
              <h3>Text</h3>
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
              <el-descriptions-item :label=""Text"">
                <el-progress 
                  :percentage="Math.round(analysisResult.tool_info.confidence * 100)"
                  :color="getConfidenceColor(analysisResult.tool_info.confidence)"
                />
              </el-descriptions-item>
            </el-descriptions>
            
            <!-- Specifications -->
            <div v-if="Object.keys(analysisResult.tool_info.specifications).length > 0" class="specifications">
              <h4>Text</h4>
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
              <h3>Text</h3>
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
                      Text
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
                      Text
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
            <h3>Text</h3>
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
import { UploadFilled, Search } from '@element-plus/icons-vue'
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

const handleFileChange: UploadProps['onChange'] = (uploadFile: UploadUserFile) => {
  if (uploadFile.raw) {
    selectedFile.value = uploadFile.raw
    
    // Create preview URL
    const reader = new FileReader()
    reader.onload = (e) => {
      imagePreview.value = e.target?.result as string
    }
    reader.readAsDataURL(uploadFile.raw)
  }
}

const handleFileRemove = () => {
  selectedFile.value = null
  imagePreview.value = ''
  analysisResult.value = null
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

  loading.value = true
  try {
    const formData = new FormData()
    formData.append('image', selectedFile.value)
    formData.append('include_alternatives', 'true')

    const response = await api.post(AGENT_ENDPOINTS.TOOL_IDENTIFICATION, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    if (response.data.success) {
      analysisResult.value = response.data.data
      ElMessage.success('Analysis completed successfully!')
    } else {
      ElMessage.error('Analysis failed')
    }
  } catch (error: any) {
    console.error('Analysis error:', error)
    ElMessage.error(error.response?.data?.detail || 'Analysis failed')
  } finally {
    loading.value = false
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