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
            >
              <el-icon><DataAnalysis /></el-icon>
              {{ loading ? 'Analyzing Project...' : 'Analyze Project' }}
            </el-button>
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
              v-for="file in fileList" 
              :key="file.uid"
              class="preview-item"
            >
              <el-image 
                :src="file.url" 
                fit="cover" 
                class="preview-image"
                :preview-src-list="previewList"
              />
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
            {{ analysisResult.project_name }}
          </el-descriptions-item>
          <el-descriptions-item label="Images Analyzed">
            {{ analysisResult.images_analyzed }}
          </el-descriptions-item>
          <el-descriptions-item label="Difficulty Level">
            <el-tag :type="getDifficultyColor(analysisResult.estimated_difficulty)">
              {{ analysisResult.estimated_difficulty?.toUpperCase() }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Estimated Time">
            {{ analysisResult.estimated_time }}
          </el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">
            {{ analysisResult.description }}
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
                    v-for="link in analysisResult.tool_identification.shopping_links.slice(0, 3)" 
                    :key="link.url"
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
        
        <!-- Product Recommendations -->
        <el-col :xs="24" :lg="12" v-if="analysisResult.product_recommendations">
          <el-card class="result-card">
            <template #header>
              <h3>Product Recommendations</h3>
            </template>
            
            <div class="recommendations-summary">
              <p><strong>Total Products:</strong> {{ analysisResult.product_recommendations.recommendations?.length || 0 }}</p>
              <p v-if="analysisResult.product_recommendations.total_estimated_cost">
                <strong>Estimated Cost:</strong> 
                ${{ analysisResult.product_recommendations.total_estimated_cost.total }}
              </p>
            </div>
            
            <div v-if="analysisResult.product_recommendations.recommendations" class="recommendations-list">
              <div 
                v-for="(rec, index) in analysisResult.product_recommendations.recommendations.slice(0, 3)" 
                :key="index"
                class="recommendation-item"
              >
                <div class="rec-header">
                  <span class="rec-name">{{ rec.name }}</span>
                  <el-tag :type="getPriorityColor(rec.priority)" size="small">
                    {{ rec.priority }}
                  </el-tag>
                </div>
                <div class="rec-details">
                  <span class="rec-price">${{ rec.estimated_price }}</span>
                  <span class="rec-category">{{ rec.category }}</span>
                </div>
              </div>
            </div>
            
            <div v-if="analysisResult.product_recommendations.shopping_tips" class="shopping-tips">
              <h5>Shopping Tips:</h5>
              <ul>
                <li v-for="tip in analysisResult.product_recommendations.shopping_tips.slice(0, 3)" :key="tip">
                  {{ tip }}
                </li>
              </ul>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- Safety Notes -->
      <el-card v-if="analysisResult.safety_notes" class="safety-card">
        <template #header>
          <h3>
            <el-icon style="color: #f56c6c;"><WarningFilled /></el-icon>
            Safety Notes
          </h3>
        </template>
        
        <el-alert
          v-for="note in analysisResult.safety_notes"
          :key="note"
          :title="note"
          type="warning"
          :closable="false"
          style="margin-bottom: 12px;"
        />
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage, type UploadProps, type UploadUserFile } from 'element-plus'
import { UploadFilled, DataAnalysis, WarningFilled } from '@element-plus/icons-vue'
import api, { AGENT_ENDPOINTS } from '@/utils/api'

interface ProjectAnalysisResult {
  project_name: string
  description: string
  images_analyzed: number
  estimated_difficulty: string
  estimated_time: string
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
    recommendations?: Array<{
      name: string
      category: string
      estimated_price: number
      priority: string
    }>
    total_estimated_cost?: {
      total: number
    }
    shopping_tips?: string[]
  }
  safety_notes?: string[]
}

const uploadRef = ref()
const formRef = ref()
const fileList = ref<UploadUserFile[]>([])
const loading = ref(false)
const analysisResult = ref<ProjectAnalysisResult | null>(null)

const projectForm = ref({
  description: '',
  projectType: 'general',
  budgetRange: 'medium'
})

const previewList = computed(() => 
  fileList.value.map(file => file.url).filter(Boolean) as string[]
)

const handleFileChange: UploadProps['onChange'] = (uploadFile: UploadUserFile, uploadFiles: UploadUserFile[]) => {
  fileList.value = uploadFiles.filter(file => file.status !== 'fail')
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

  loading.value = true
  try {
    const formData = new FormData()
    
    // Add images
    fileList.value.forEach(file => {
      if (file.raw) {
        formData.append('images', file.raw)
      }
    })
    
    // Add project details
    formData.append('description', projectForm.value.description)
    formData.append('project_type', projectForm.value.projectType)
    formData.append('budget_range', projectForm.value.budgetRange)

    const response = await api.post(AGENT_ENDPOINTS.PROJECT_ANALYSIS, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    if (response.data.success) {
      analysisResult.value = response.data.data
      ElMessage.success('Project analysis completed successfully!')
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
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
}

.preview-image {
  width: 100%;
  height: 100%;
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

.safety-card :deep(.el-card__header) {
  background: #fef0f0;
  border-bottom: 1px solid #fbc4c4;
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