<template>
  <div class="product-recommendation">
    <div class="page-header">
      <h1 class="page-title">Product Recommendation</h1>
      <p class="page-subtitle">Get smart product recommendations for your projects</p>
    </div>

    <el-row :gutter="20">
      <!-- Input Form -->
      <el-col :xs="24" :lg="8">
        <el-card class="form-card">
          <template #header>
            <h3>Project Details</h3>
          </template>
          
          <el-form
            ref="formRef"
            :model="projectForm"
            :rules="rules"
            label-position="top"
            size="large"
          >
            <el-form-item label="Project Type" prop="projectType">
              <el-select v-model="projectForm.projectType" style="width: 100%">
                <el-option
                  v-for="(label, value) in projectTypes"
                  :key="value"
                  :label="label"
                  :value="value"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="Budget Range" prop="budgetRange">
              <el-select v-model="projectForm.budgetRange" style="width: 100%">
                <el-option
                  v-for="(label, value) in budgetRanges"
                  :key="value"
                  :label="label"
                  :value="value"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="Skill Level" prop="skillLevel">
              <el-select v-model="projectForm.skillLevel" style="width: 100%">
                <el-option
                  v-for="(label, value) in skillLevels"
                  :key="value"
                  :label="label"
                  :value="value"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="Materials Needed">
              <el-input
                v-model="projectForm.materials"
                type="textarea"
                :rows="3"
                placeholder="List materials you need for your project..."
              />
            </el-form-item>
            
            <el-form-item label="Tools Needed">
              <el-input
                v-model="projectForm.toolsNeeded"
                type="textarea"
                :rows="3"
                placeholder="List tools you need for your project..."
              />
            </el-form-item>
            
            <el-form-item>
              <el-button
                type="primary"
                size="large"
                style="width: 100%"
                :loading="loading"
                @click="getRecommendations"
              >
                <el-icon><ShoppingBag /></el-icon>
                Get Recommendations
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      
      <!-- Results -->
      <el-col :xs="24" :lg="16">
        <div v-if="!recommendationResult && !loading" class="empty-state">
          <el-card>
            <div class="empty-content">
              <el-icon class="empty-icon"><ShoppingBag /></el-icon>
              <h3>Ready to Get Recommendations?</h3>
              <p>Fill out the project details on the left to get personalized product recommendations for your DIY project.</p>
            </div>
          </el-card>
        </div>
        
        <div v-if="loading" class="loading-state">
          <el-card>
            <div class="loading-content">
              <el-icon class="loading-icon"><Loading /></el-icon>
              <h3>Analyzing Your Project...</h3>
              <p>Our AI is finding the best products for your project. This will just take a moment.</p>
            </div>
          </el-card>
        </div>
        
        <!-- Recommendations Results -->
        <div v-if="recommendationResult" class="results-section">
          <!-- Summary -->
          <el-card class="summary-card">
            <template #header>
              <h3>Recommendation Summary</h3>
            </template>
            
            <el-row :gutter="16">
              <el-col :span="8">
                <div class="summary-item">
                  <div class="summary-number">{{ recommendationResult.recommendations.length }}</div>
                  <div class="summary-label">Products Found</div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="summary-item">
                  <div class="summary-number">${{ recommendationResult.total_estimated_cost?.total || 0 }}</div>
                  <div class="summary-label">Total Cost</div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="summary-item">
                  <div class="summary-number">{{ recommendationResult.retailers_suggested?.length || 0 }}</div>
                  <div class="summary-label">Retailers</div>
                </div>
              </el-col>
            </el-row>
          </el-card>
          
          <!-- Recommendations -->
          <el-card class="recommendations-card">
            <template #header>
              <h3>Product Recommendations</h3>
            </template>
            
            <el-row :gutter="16">
              <el-col 
                :xs="24" :sm="12" :lg="8"
                v-for="(item, index) in recommendationResult.recommendations" 
                :key="index"
              >
                <div class="recommendation-item">
                  <div class="item-header">
                    <h4>{{ item.name }}</h4>
                    <el-tag :type="getPriorityColor(item.priority)">
                      {{ item.priority }}
                    </el-tag>
                  </div>
                  
                  <div class="item-details">
                    <p v-if="item.brand"><strong>Brand:</strong> {{ item.brand }}</p>
                    <p><strong>Category:</strong> {{ item.category }}</p>
                    <p v-if="item.quantity"><strong>Quantity:</strong> {{ item.quantity }}</p>
                    <p class="price"><strong>Price:</strong> ${{ item.estimated_price }}</p>
                    <p v-if="item.reason" class="reason">{{ item.reason }}</p>
                    <p v-if="item.tips" class="tips">💡 {{ item.tips }}</p>
                  </div>
                  
                  <div v-if="item.alternatives && item.alternatives.length > 0" class="alternatives">
                    <el-popover placement="top" :width="300" trigger="hover">
                      <template #reference>
                        <el-button size="small" text>
                          View Alternatives ({{ item.alternatives.length }})
                        </el-button>
                      </template>
                      <div class="alternatives-content">
                        <div v-for="alt in item.alternatives" :key="alt.brand" class="alt-item">
                          <strong>{{ alt.brand }} {{ alt.model }}</strong>
                          <span class="alt-price">{{ alt.price_difference }}</span>
                        </div>
                      </div>
                    </el-popover>
                  </div>
                </div>
              </el-col>
            </el-row>
          </el-card>
          
          <!-- Shopping Tips -->
          <el-card class="tips-card">
            <template #header>
              <h3>Shopping Tips</h3>
            </template>
            
            <ul class="tips-list">
              <li v-for="tip in recommendationResult.shopping_tips" :key="tip">
                <el-icon><InfoFilled /></el-icon>
                {{ tip }}
              </li>
            </ul>
          </el-card>
          
          <!-- Cost Breakdown -->
          <el-card v-if="recommendationResult.total_estimated_cost" class="cost-card">
            <template #header>
              <h3>Cost Breakdown</h3>
            </template>
            
            <el-descriptions :column="2" border>
              <el-descriptions-item label="Subtotal">
                ${{ recommendationResult.total_estimated_cost.subtotal }}
              </el-descriptions-item>
              <el-descriptions-item label="Est. Tax">
                ${{ recommendationResult.total_estimated_cost.tax_estimate }}
              </el-descriptions-item>
              <el-descriptions-item label="Total">
                <span class="total-price">
                  ${{ recommendationResult.total_estimated_cost.total }}
                </span>
              </el-descriptions-item>
              <el-descriptions-item label="Potential Savings">
                <span class="savings">
                  ${{ recommendationResult.total_estimated_cost.savings_potential }}
                </span>
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed } from 'vue'
import { ElMessage, type FormRules } from 'element-plus'
import { ShoppingBag, Loading, InfoFilled } from '@element-plus/icons-vue'
import api, { AGENT_ENDPOINTS } from '@/utils/api'

interface RecommendationResult {
  recommendations: Array<{
    name: string
    brand?: string
    category: string
    estimated_price: number
    priority: string
    reason?: string
    tips?: string
    quantity?: string
    alternatives?: Array<{
      brand: string
      model: string
      price_difference: string
    }>
  }>
  shopping_tips: string[]
  total_estimated_cost?: {
    subtotal: number
    tax_estimate: number
    total: number
    savings_potential: number
  }
  retailers_suggested?: string[]
}

const formRef = ref()
const loading = ref(false)
const recommendationResult = ref<RecommendationResult | null>(null)

const projectForm = reactive({
  projectType: 'general',
  budgetRange: 'medium',
  skillLevel: 'intermediate',
  materials: '',
  toolsNeeded: ''
})

const projectTypes = computed(() => ({
  general: 'General DIY',
  woodworking: 'Woodworking',
  electronics: 'Electronics',
  plumbing: 'Plumbing',
  painting: 'Painting'
}))

const budgetRanges = computed(() => ({
  low: 'Under $100',
  medium: '$100 - $500',
  high: 'Over $500'
}))

const skillLevels = computed(() => ({
  beginner: 'Beginner',
  intermediate: 'Intermediate',
  expert: 'Expert'
}))

const rules: FormRules = {
  projectType: [
    { required: true, message: 'Please select a project type', trigger: 'change' }
  ],
  budgetRange: [
    { required: true, message: 'Please select a budget range', trigger: 'change' }
  ],
  skillLevel: [
    { required: true, message: 'Please select your skill level', trigger: 'change' }
  ]
}

const getRecommendations = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    loading.value = true
    
    const formData = new FormData()
    formData.append('project_type', projectForm.projectType)
    formData.append('budget_range', projectForm.budgetRange)
    formData.append('skill_level', projectForm.skillLevel)
    if (projectForm.materials) {
      formData.append('materials', projectForm.materials)
    }
    if (projectForm.toolsNeeded) {
      formData.append('tools_needed', projectForm.toolsNeeded)
    }

    const response = await api.post(AGENT_ENDPOINTS.PRODUCT_RECOMMENDATION, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    if (response.data.success) {
      recommendationResult.value = response.data.data
      ElMessage.success('Recommendations generated successfully!')
    } else {
      ElMessage.error('Failed to generate recommendations')
    }
  } catch (error: any) {
    console.error('Recommendation error:', error)
    ElMessage.error(error.response?.data?.detail || 'Failed to generate recommendations')
  } finally {
    loading.value = false
  }
}

const getPriorityColor = (priority: string) => {
  switch (priority) {
    case 'essential': return 'danger'
    case 'recommended': return 'warning'
    case 'optional': return 'info'
    default: return 'primary'
  }
}
</script>

<style scoped>
.product-recommendation {
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

.form-card {
  position: sticky;
  top: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.empty-state, .loading-state {
  margin-bottom: 20px;
}

.empty-content, .loading-content {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.empty-icon, .loading-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.loading-icon {
  animation: spin 2s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.results-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.summary-card, .recommendations-card, .tips-card, .cost-card {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.summary-item {
  text-align: center;
  padding: 20px;
}

.summary-number {
  font-size: 32px;
  font-weight: 700;
  color: #667eea;
  line-height: 1;
}

.summary-label {
  font-size: 14px;
  color: #606266;
  margin-top: 8px;
}

.recommendation-item {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  transition: all 0.3s ease;
}

.recommendation-item:hover {
  border-color: #667eea;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.item-header h4 {
  margin: 0;
  color: #303133;
  font-size: 16px;
  line-height: 1.4;
}

.item-details p {
  margin: 4px 0;
  font-size: 14px;
  color: #606266;
}

.price {
  color: #67c23a !important;
  font-weight: 600;
}

.reason {
  font-style: italic;
  color: #909399 !important;
}

.tips {
  color: #e6a23c !important;
  font-size: 13px;
}

.alternatives {
  margin-top: 12px;
}

.alternatives-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.alt-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 4px;
}

.alt-price {
  font-weight: 600;
  color: #e6a23c;
}

.tips-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.tips-list li {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 12px;
  line-height: 1.6;
}

.tips-list .el-icon {
  color: #e6a23c;
  margin-top: 2px;
  flex-shrink: 0;
}

.total-price {
  font-size: 18px;
  font-weight: 700;
  color: #67c23a;
}

.savings {
  font-weight: 600;
  color: #e6a23c;
}

/* Responsive Design */
@media (max-width: 768px) {
  .form-card {
    position: static;
  }
  
  .summary-item {
    padding: 16px;
  }
  
  .summary-number {
    font-size: 24px;
  }
}
</style>