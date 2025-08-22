<template>
  <div class="project-analysis">
    <div class="page-header">
      <h1 class="page-title">Project Analysis</h1>
      <p class="page-subtitle">Upload project images for comprehensive DIY analysis</p>
    </div>

    <el-row :gutter="20">
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
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              Drop images here or <em>click to upload</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                Upload 1-5 project images (JPG/PNG, max 10MB each)
              </div>
            </template>
          </el-upload>

          <div class="form-section">
            <el-form :model="projectForm" label-position="top">
              <el-form-item label="Project Description (optional)">
                <el-input
                  v-model="projectForm.description"
                  type="textarea"
                  :rows="3"
                  placeholder="Describe your project..."
                />
              </el-form-item>
              
              <el-form-item label="Project Type">
                <el-select v-model="projectForm.projectType" placeholder="Select type">
                  <el-option label="General" value="general" />
                  <el-option label="Woodworking" value="woodworking" />
                  <el-option label="Electronics" value="electronics" />
                  <el-option label="Metalworking" value="metalworking" />
                  <el-option label="Crafts" value="crafts" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="Budget Range">
                <el-select v-model="projectForm.budgetRange" placeholder="Select budget">
                  <el-option label="Under $50" value="under50" />
                  <el-option label="$50-150" value="50to150" />
                  <el-option label="$150-300" value="150to300" />
                  <el-option label="$300+" value="300plus" />
                </el-select>
              </el-form-item>
            </el-form>
          </div>

          <el-button 
            type="primary" 
            size="large" 
            @click="analyzeProject"
            :loading="loading"
            :disabled="fileList.length === 0"
            class="analyze-button"
          >
            <el-icon v-if="!loading"><search /></el-icon>
            {{ loading ? 'Analyzing Project...' : 'Analyze Project' }}
          </el-button>
          
          <!-- Progress Bar -->
          <div v-if="loading" class="fancy-progress-container" style="margin-top: 16px;">
            <div class="progress-header">
              <div class="progress-icon">
                <el-icon class="spinning-icon"><loading /></el-icon>
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
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="12">
        <!-- Uploaded Images Preview -->
        <el-card v-if="fileList.length > 0" class="preview-card" style="margin-bottom: 20px;">
          <template #header>
            <h3>📷 Uploaded Images ({{ fileList.length }})</h3>
          </template>
          
          <div class="image-gallery">
            <div 
              v-for="(file, index) in fileList" 
              :key="`preview-${index}`"
              class="preview-item"
            >
              <img 
                :src="getPreviewUrl(file)" 
                :alt="`Preview ${index + 1}`"
                class="preview-image"
              />
              <div class="preview-name">{{ file.name }}</div>
            </div>
          </div>
        </el-card>
        
        <div v-if="result" class="results-section">
          <!-- Project Overview -->
          <el-card class="overview-card">
            <template #header>
              <h3>Project Overview</h3>
            </template>
            
            <el-descriptions :column="2" border v-if="result.comprehensive_analysis">
              <el-descriptions-item label="Project Name">
                {{ result.comprehensive_analysis.project_name }}
              </el-descriptions-item>
              <el-descriptions-item label="Project Type">
                {{ result.comprehensive_analysis.project_type }}
              </el-descriptions-item>
              <el-descriptions-item label="Difficulty Level">
                <el-tag :type="getDifficultyColor(result.comprehensive_analysis.difficulty_level)">
                  {{ result.comprehensive_analysis.difficulty_level?.toUpperCase() }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="Estimated Time">
                {{ result.comprehensive_analysis.estimated_time }}
              </el-descriptions-item>
              <el-descriptions-item label="Description" :span="2">
                {{ result.comprehensive_analysis.description }}
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
          
          <!-- Materials & Tools -->
          <el-card class="result-card" style="margin-top: 20px;" v-if="result.comprehensive_analysis">
            <template #header>
              <h3>Materials & Tools Required</h3>
            </template>
            
            <div class="tab-hint">
              <el-alert 
                title="💡 Click on the tabs below to explore different sections" 
                type="info" 
                show-icon 
                :closable="false"
                style="margin-bottom: 16px;"
              />
            </div>
            
            <el-tabs model-value="materials" class="clickable-tabs">
              <el-tab-pane name="materials">
                <template #label>
                  <span class="tab-label">
                    📦 Materials <el-badge :value="result.comprehensive_analysis.materials?.length || 0" />
                  </span>
                </template>
                <div class="material-list">
                  <div 
                    v-for="(material, index) in result.comprehensive_analysis.materials" 
                    :key="`material-${index}`"
                    class="material-item"
                  >
                    <div class="material-info">
                      <h4>{{ material.name }}</h4>
                      <p><strong>Specification:</strong> {{ material.specification }}</p>
                      <p><strong>Quantity:</strong> {{ material.quantity }}</p>
                      <p><strong>Price Range:</strong> {{ material.estimated_price_range }}</p>
                    </div>
                  </div>
                </div>
              </el-tab-pane>
              
              <el-tab-pane name="tools">
                <template #label>
                  <span class="tab-label">
                    🔧 Tools <el-badge :value="result.comprehensive_analysis.tools?.length || 0" />
                  </span>
                </template>
                <div class="tool-list">
                  <div 
                    v-for="(tool, index) in result.comprehensive_analysis.tools" 
                    :key="`tool-${index}`"
                    class="tool-item"
                  >
                    <div class="tool-info">
                      <h4>{{ tool.name }}</h4>
                      <el-tag :type="tool.necessity === 'Essential' ? 'danger' : 'warning'">
                        {{ tool.necessity }}
                      </el-tag>
                    </div>
                  </div>
                </div>
              </el-tab-pane>
              
              <el-tab-pane name="safety">
                <template #label>
                  <span class="tab-label">
                    ⚠️ Safety <el-badge :value="result.comprehensive_analysis.safety_notes?.length || 0" />
                  </span>
                </template>
                <div class="safety-list">
                  <div 
                    v-for="(note, index) in result.comprehensive_analysis.safety_notes" 
                    :key="`safety-${index}`"
                    class="safety-item"
                  >
                    <el-alert :title="note" type="warning" show-icon :closable="false" />
                  </div>
                </div>
              </el-tab-pane>
              
              <el-tab-pane name="steps">
                <template #label>
                  <span class="tab-label">
                    📋 Steps <el-badge :value="result.comprehensive_analysis.steps?.length || 0" />
                  </span>
                </template>
                <div class="steps-list">
                  <el-steps direction="vertical">
                    <el-step 
                      v-for="(step, index) in result.comprehensive_analysis.steps" 
                      :key="`step-${index}`"
                      :title="`Step ${index + 1}`"
                      :description="step"
                      status="wait"
                    />
                  </el-steps>
                </div>
              </el-tab-pane>
            </el-tabs>
          </el-card>
          
          <!-- Product Recommendations -->
          <el-card class="result-card" style="margin-top: 20px;" v-if="result.product_recommendations">
            <template #header>
              <h3>🛒 Product Recommendations</h3>
            </template>
            
            <div class="tab-hint">
              <el-alert 
                title="🛒 Explore product recommendations, shopping tips, and budget analysis below" 
                type="success" 
                show-icon 
                :closable="false"
                style="margin-bottom: 16px;"
              />
            </div>
            
            <el-tabs model-value="products" class="clickable-tabs">
              <el-tab-pane name="products">
                <template #label>
                  <span class="tab-label">
                    🛒 Products <el-badge :value="result.product_recommendations.assessed_results?.length || 0" />
                  </span>
                </template>
                <div 
                  v-for="(category, index) in result.product_recommendations.assessed_results" 
                  :key="`category-${index}`"
                  class="product-category"
                >
                  <h4>{{ category.material }}</h4>
                  <div class="products-grid">
                    <div 
                      v-for="(product, pIndex) in category.products.slice(0, 3)" 
                      :key="`product-${pIndex}`"
                      class="product-card"
                    >
                      <div class="product-header">
                        <img :src="product.image_url" :alt="product.title" class="product-image" />
                        <div class="product-info">
                          <h5>{{ product.title }}</h5>
                          <p class="product-description">{{ product.description }}</p>
                          <div class="product-details">
                            <span class="price">${{ product.price }}</span>
                            <span class="platform">{{ product.platform }}</span>
                            <el-rate v-model="product.rating" disabled show-score text-color="#ff9900" />
                          </div>
                        </div>
                      </div>
                      <div class="product-footer">
                        <el-tag :type="getRecommendationColor(product.recommendation_level)">
                          {{ product.recommendation_level }}
                        </el-tag>
                        <el-button type="primary" size="small" @click="openProductLink(product.product_url)">
                          View Product
                        </el-button>
                      </div>
                    </div>
                  </div>
                </div>
              </el-tab-pane>
              
              <el-tab-pane name="tips">
                <template #label>
                  <span class="tab-label">
                    💡 Tips <el-badge :value="result.product_recommendations.overall_recommendations.shopping_tips?.length || 0" />
                  </span>
                </template>
                <div class="shopping-tips">
                  <div 
                    v-for="(tip, index) in result.product_recommendations.overall_recommendations.shopping_tips" 
                    :key="`tip-${index}`"
                    class="tip-item"
                  >
                    <el-alert :title="tip" type="info" show-icon :closable="false" />
                  </div>
                </div>
              </el-tab-pane>
              
              <el-tab-pane name="budget">
                <template #label>
                  <span class="tab-label">
                    💰 Budget Analysis
                  </span>
                </template>
                <div class="budget-info" v-if="result.product_recommendations.overall_recommendations.budget_breakdown">
                  <el-descriptions :column="2" border>
                    <el-descriptions-item label="Estimated Total Cost">
                      {{ result.product_recommendations.overall_recommendations.budget_breakdown.estimated_total }}
                    </el-descriptions-item>
                    <el-descriptions-item label="Products Assessed">
                      {{ result.product_recommendations.overall_recommendations.total_products_assessed }}
                    </el-descriptions-item>
                    <el-descriptions-item label="Average Quality Score">
                      <el-rate :model-value="result.product_recommendations.overall_recommendations.average_quality_score" disabled />
                    </el-descriptions-item>
                  </el-descriptions>
                  
                  <div class="cost-optimization" style="margin-top: 20px;">
                    <h4>💡 Cost Optimization Tips:</h4>
                    <ul>
                      <li 
                        v-for="(tip, index) in result.product_recommendations.overall_recommendations.budget_breakdown.cost_optimization_tips" 
                        :key="`cost-tip-${index}`"
                      >
                        {{ tip }}
                      </li>
                    </ul>
                  </div>
                </div>
              </el-tab-pane>
            </el-tabs>
          </el-card>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { UploadProps, UploadUserFile } from 'element-plus'
import { UploadFilled, Search, Loading } from '@element-plus/icons-vue'
import api from '@/utils/api'

const uploadRef = ref()
const fileList = ref<UploadUserFile[]>([])
const loading = ref(false)
const result = ref(null)
const analysisProgress = ref(0)
const analysisStatus = ref('')

const projectForm = ref({
  description: '',
  projectType: 'general',
  budgetRange: '50to150'
})

const beforeUpload: UploadProps['beforeUpload'] = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isImage) {
    console.error('Please upload image files only!')
    return false
  }
  if (!isLt10M) {
    console.error('Image size must be less than 10MB!')
    return false
  }
  return true
}

const handleFileChange: UploadProps['onChange'] = (uploadFile, uploadFiles) => {
  fileList.value = uploadFiles
}

const handleFileRemove: UploadProps['onRemove'] = (uploadFile, uploadFiles) => {
  fileList.value = uploadFiles
}

const getDifficultyColor = (level: string) => {
  switch (level?.toLowerCase()) {
    case 'easy': return 'success'
    case 'medium': case 'intermediate': return 'warning'
    case 'hard': case 'expert': return 'danger'
    default: return 'info'
  }
}

const getRecommendationColor = (level: string) => {
  switch (level?.toLowerCase()) {
    case 'best value': return 'success'
    case 'highly recommended': return 'primary'
    case 'professional choice': return 'warning'
    case 'good choice': return 'info'
    default: return 'info'
  }
}

const openProductLink = (url: string) => {
  window.open(url, '_blank')
}

const getPreviewUrl = (file: UploadUserFile): string => {
  if (file.url) {
    return file.url
  }
  if (file.raw) {
    return URL.createObjectURL(file.raw)
  }
  return ''
}

const analyzeProject = async () => {
  if (fileList.value.length === 0) {
    console.error('Please upload at least one image')
    return
  }

  loading.value = true
  result.value = null
  analysisProgress.value = 0
  analysisStatus.value = 'Preparing images...'
  
  try {
    console.log('Starting analysis with files:', fileList.value.length)
    
    const formData = new FormData()
    
    // Progress: 10%
    analysisProgress.value = 10
    analysisStatus.value = 'Processing images...'
    
    for (let i = 0; i < fileList.value.length; i++) {
      const file = fileList.value[i]
      if (file.raw) {
        formData.append('images', file.raw)
        console.log(`Added file ${i}: ${file.name}`)
      }
    }
    
    formData.append('description', projectForm.value.description || '')
    formData.append('project_type', projectForm.value.projectType)
    formData.append('budget_range', projectForm.value.budgetRange)
    
    // Progress: 25%
    analysisProgress.value = 25
    analysisStatus.value = 'Uploading to AI analysis service...'
    
    // Progress: 40%
    analysisProgress.value = 40
    analysisStatus.value = 'AI is analyzing your project...'

    // Create a progress simulation
    const progressInterval = setInterval(() => {
      if (analysisProgress.value < 85) {
        analysisProgress.value = Math.min(85, analysisProgress.value + Math.floor(Math.random() * 8) + 2)
        const messages = [
          'Analyzing project structure...',
          'Identifying materials needed...',
          'Finding tool requirements...',
          'Generating safety recommendations...',
          'Creating step-by-step guide...',
          'Searching for product recommendations...'
        ]
        analysisStatus.value = messages[Math.floor(Math.random() * messages.length)]
      }
    }, 1500)
    
    console.log('Making API call...')
    
    const response = await api.post('/api/v1/agents/project/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 120000
    })
    
    // Clear progress interval
    clearInterval(progressInterval)
    
    // Progress: 95%
    analysisProgress.value = 95
    analysisStatus.value = 'Processing results...'
    
    console.log('Response:', response)
    
    if (response.data && response.data.success) {
      // Progress: 100%
      analysisProgress.value = 100
      analysisStatus.value = 'Analysis completed!'
      
      result.value = response.data.data
      console.log('Analysis completed successfully!')
    } else {
      throw new Error('Analysis failed')
    }
    
  } catch (error: any) {
    console.error('Analysis error:', error)
    console.error('Error response:', error.response)
    
    if (error.response?.data?.detail) {
      console.error('API Error:', error.response.data.detail)
    } else if (error.response?.status === 422) {
      console.error('422 Error: Invalid request')
    } else {
      console.error('Error:', error.message || 'Analysis failed')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.project-analysis {
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-title {
  font-size: 32px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 10px 0;
}

.page-subtitle {
  font-size: 16px;
  color: #909399;
  margin: 0;
}

.upload-card {
  margin-bottom: 20px;
}

.form-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.analyze-button {
  width: 100%;
  margin-top: 20px;
}

.result-card {
  margin-bottom: 20px;
}

.result-content {
  max-height: 600px;
  overflow-y: auto;
}

.result-content pre {
  font-size: 12px;
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
}

/* Progress Bar Styles */
.fancy-progress-container {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e4e7ed;
}

.progress-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.progress-icon {
  margin-right: 12px;
}

.spinning-icon {
  animation: spin 2s linear infinite;
  font-size: 20px;
  color: #409eff;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.progress-text {
  flex: 1;
}

.progress-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.progress-status {
  font-size: 14px;
  color: #606266;
}

.custom-progress-bar {
  position: relative;
}

.progress-track {
  height: 8px;
  background: #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #409eff, #67c23a);
  border-radius: 4px;
  transition: width 0.6s ease;
  position: relative;
}

.progress-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
  animation: glow 2s ease-in-out infinite;
}

@keyframes glow {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.progress-dots {
  display: flex;
  justify-content: space-between;
  margin-top: 12px;
  padding: 0 4px;
}

.progress-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #e4e7ed;
  transition: all 0.3s ease;
}

.progress-dot.active {
  background: #409eff;
  transform: scale(1.2);
}

/* Result Display Styles */
.overview-card {
  margin-bottom: 20px;
}

.material-item, .tool-item {
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  margin-bottom: 12px;
}

.material-item h4, .tool-item h4 {
  margin: 0 0 8px 0;
  color: #303133;
}

.tool-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.safety-item {
  margin-bottom: 12px;
}

.steps-list {
  padding: 20px 0;
}

/* Product Recommendations Styles */
.product-category {
  margin-bottom: 30px;
}

.product-category h4 {
  color: #303133;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #409eff;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.product-card {
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  padding: 16px;
  background: #fafbfc;
  transition: all 0.3s ease;
}

.product-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.product-header {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.product-image {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 8px;
  flex-shrink: 0;
}

.product-info {
  flex: 1;
}

.product-info h5 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #303133;
  font-weight: 600;
}

.product-description {
  font-size: 12px;
  color: #606266;
  margin: 0 0 8px 0;
}

.product-details {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.price {
  font-weight: 600;
  color: #f56c6c;
  font-size: 16px;
}

.platform {
  font-size: 12px;
  color: #909399;
  background: #f0f9ff;
  padding: 2px 6px;
  border-radius: 4px;
}

.product-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e4e7ed;
}

.shopping-tips .tip-item {
  margin-bottom: 12px;
}

.cost-optimization ul {
  margin: 8px 0;
  padding-left: 20px;
}

.cost-optimization li {
  margin-bottom: 8px;
  color: #606266;
}

/* Tab Enhancement Styles */
.clickable-tabs .el-tabs__nav-wrap {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 8px;
  padding: 4px;
}

.clickable-tabs .el-tabs__item {
  transition: all 0.3s ease;
  border-radius: 6px;
  margin: 2px;
  font-weight: 500;
}

.clickable-tabs .el-tabs__item:hover {
  background: rgba(64, 158, 255, 0.1);
  color: #409eff;
  transform: translateY(-1px);
}

.clickable-tabs .el-tabs__item.is-active {
  background: #409eff;
  color: white;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.tab-hint {
  margin-bottom: 16px;
}

/* Preview Images Styles */
.image-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 16px;
}

.preview-item {
  text-align: center;
}

.preview-image {
  width: 100%;
  height: 100px;
  object-fit: cover;
  border-radius: 8px;
  border: 2px solid #e4e7ed;
  transition: all 0.3s ease;
}

.preview-image:hover {
  border-color: #409eff;
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.preview-name {
  font-size: 12px;
  color: #606266;
  margin-top: 8px;
  word-break: break-all;
}

.preview-card {
  background: linear-gradient(135deg, #fafbfc 0%, #f0f9ff 100%);
}
</style>