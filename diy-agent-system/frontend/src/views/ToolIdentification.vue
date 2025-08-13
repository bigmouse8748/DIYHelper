<template>
  <div class="tool-identification">
    <!-- Header -->
    <div class="page-header">
      <h1>{{ $t('toolIdentification.title') }}</h1>
      <p class="subtitle">{{ $t('toolIdentification.subtitle') }}</p>
    </div>

    <!-- Login prompt if not authenticated -->
    <div v-if="!isAuthenticated" class="login-prompt">
      <el-card>
        <div class="prompt-content">
          <el-icon :size="48"><Lock /></el-icon>
          <h3>{{ $t('toolIdentification.loginRequired') }}</h3>
          <p>{{ $t('toolIdentification.loginPrompt') }}</p>
          <div class="button-group">
            <el-button type="primary" @click="goToLogin">{{ $t('auth.login') }}</el-button>
            <el-button @click="goToRegister">{{ $t('auth.register') }}</el-button>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Main content for authenticated users -->
    <div v-else class="identification-content">
      <!-- User status bar -->
      <div class="user-status">
        <el-card>
          <div class="status-content">
            <div class="user-info">
              <el-icon><User /></el-icon>
              <span>{{ currentUser.username }}</span>
              <el-tag :type="getMembershipType(currentUser.membership)">
                {{ $t(`membership.${currentUser.membership}`) }}
              </el-tag>
            </div>
            <div class="usage-info">
              <span>{{ $t('toolIdentification.dailyUsage') }}:</span>
              <el-progress
                :percentage="usagePercentage"
                :stroke-width="10"
                :color="getProgressColor"
                style="width: 200px"
              >
                <span>{{ currentUser.dailyUsed }}/{{ currentUser.dailyLimit }}</span>
              </el-progress>
            </div>
          </div>
        </el-card>
      </div>

      <!-- Upload section -->
      <el-card class="upload-section">
        <template #header>
          <div class="card-header">
            <el-icon><Camera /></el-icon>
            <span>{{ $t('toolIdentification.uploadImage') }}</span>
          </div>
        </template>

        <el-upload
          class="tool-uploader"
          :drag="true"
          :auto-upload="false"
          :show-file-list="false"
          :on-change="handleImageChange"
          :before-upload="beforeUpload"
          accept="image/*"
        >
          <div v-if="!imagePreview" class="upload-placeholder">
            <div class="upload-icon-wrapper">
              <el-icon class="upload-icon"><Camera /></el-icon>
            </div>
            <div class="upload-content">
              <h3>{{ $t('toolIdentification.dragOrClick') }}</h3>
              <p class="upload-subtitle">{{ $t('toolIdentification.uploadHint') }}</p>
              <div class="upload-formats">
                <el-tag size="small" type="info">JPG</el-tag>
                <el-tag size="small" type="info">PNG</el-tag>
                <el-tag size="small" type="info">WebP</el-tag>
                <span class="format-size">Max 10MB</span>
              </div>
              <div class="upload-examples">
                <p>{{ $t('toolIdentification.examples') }}:</p>
                <div class="example-tags">
                  <el-tag size="small">{{ $t('toolIdentification.example1') }}</el-tag>
                  <el-tag size="small">{{ $t('toolIdentification.example2') }}</el-tag>
                  <el-tag size="small">{{ $t('toolIdentification.example3') }}</el-tag>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="image-preview">
            <img :src="imagePreview" alt="Tool preview" />
            <div class="preview-overlay">
              <div class="preview-actions">
                <el-button 
                  @click.stop="clearImage" 
                  :icon="Delete" 
                  circle 
                  size="large"
                  type="danger"
                />
                <el-button 
                  @click.stop="rotateImage" 
                  :icon="Refresh" 
                  circle 
                  size="large"
                />
              </div>
              <div class="image-info">
                <el-tag type="success" size="small">
                  {{ $t('common.ready') }}
                </el-tag>
              </div>
            </div>
          </div>
        </el-upload>

        <div class="identify-options">
          <div class="option-card">
            <el-switch 
              v-model="includeAlternatives" 
              :active-text="$t('toolIdentification.includeAlternatives')"
              :inactive-text="$t('toolIdentification.exactOnly')"
              inline-prompt
            />
            <p class="option-description">
              {{ includeAlternatives ? $t('toolIdentification.alternativesDesc') : $t('toolIdentification.exactDesc') }}
            </p>
          </div>
          
          <div class="option-card">
            <el-switch 
              v-model="highAccuracy" 
              :active-text="$t('toolIdentification.highAccuracy')"
              :inactive-text="$t('toolIdentification.fastMode')"
              inline-prompt
            />
            <p class="option-description">
              {{ highAccuracy ? $t('toolIdentification.highAccuracyDesc') : $t('toolIdentification.fastModeDesc') }}
            </p>
          </div>
        </div>

        <div class="action-buttons">
          <el-button
            type="primary"
            size="large"
            :icon="Search"
            :loading="isIdentifying"
            :disabled="!imageFile || (currentUser?.dailyUsed >= currentUser?.dailyLimit)"
            @click="identifyTool"
            class="identify-button"
          >
            <template v-if="isIdentifying">
              <span>{{ identifyingStage }}...</span>
            </template>
            <template v-else>
              {{ $t('toolIdentification.identify') }}
            </template>
          </el-button>
          
          <div v-if="currentUser?.dailyUsed >= currentUser?.dailyLimit" class="quota-warning">
            <el-alert
              type="warning"
              :title="$t('toolIdentification.quotaExceeded')"
              :description="$t('toolIdentification.upgradePrompt')"
              show-icon
              :closable="false"
            >
              <template #default>
                <el-button size="small" type="warning" @click="showUpgradeDialog = true">
                  {{ $t('membership.upgrade') }}
                </el-button>
              </template>
            </el-alert>
          </div>
        </div>
      </el-card>

      <!-- Results section -->
      <div v-if="identificationResult" class="results-section">
        <!-- Tool information -->
        <el-card class="tool-info-card">
          <template #header>
            <div class="card-header">
              <el-icon><Tools /></el-icon>
              <span>{{ $t('toolIdentification.toolInfo') }}</span>
              <el-tag type="success" style="margin-left: auto">
                {{ $t('toolIdentification.confidence') }}: {{ (identificationResult.tool_info.confidence * 100).toFixed(0) }}%
              </el-tag>
            </div>
          </template>

          <el-descriptions :column="2" border>
            <el-descriptions-item :label="$t('toolIdentification.toolName')">
              {{ identificationResult.tool_info.name }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('toolIdentification.brand')">
              {{ identificationResult.tool_info.brand || '-' }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('toolIdentification.model')">
              {{ identificationResult.tool_info.model || '-' }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('toolIdentification.category')">
              {{ $t(`toolCategory.${identificationResult.tool_info.category}`) }}
            </el-descriptions-item>
          </el-descriptions>

          <div v-if="identificationResult.tool_info.specifications" class="specifications">
            <h4>{{ $t('toolIdentification.specifications') }}</h4>
            <el-tag
              v-for="(value, key) in identificationResult.tool_info.specifications"
              :key="key"
              style="margin: 4px"
            >
              {{ key }}: {{ value }}
            </el-tag>
          </div>
        </el-card>

        <!-- Exact matches -->
        <el-card v-if="identificationResult.exact_matches.length > 0" class="matches-card">
          <template #header>
            <div class="card-header">
              <el-icon><ShoppingCart /></el-icon>
              <span>{{ $t('toolIdentification.exactMatches') }}</span>
            </div>
          </template>

          <div class="product-grid">
            <div
              v-for="product in identificationResult.exact_matches"
              :key="`${product.retailer}-${product.title}`"
              class="product-card"
            >
              <div class="retailer-badge">{{ product.retailer }}</div>
              <img :src="product.image_url" :alt="product.title" />
              <div class="product-info">
                <h4>{{ product.title }}</h4>
                <div class="price">${{ product.price.toFixed(2) }}</div>
                <el-tag :type="product.in_stock ? 'success' : 'danger'" size="small">
                  {{ product.in_stock ? $t('common.inStock') : $t('common.outOfStock') }}
                </el-tag>
                <el-button
                  type="primary"
                  size="small"
                  :icon="Link"
                  @click="openProductLink(product.url)"
                >
                  {{ $t('common.viewProduct') }}
                </el-button>
              </div>
            </div>
          </div>
        </el-card>

        <!-- Alternative products -->
        <el-card v-if="identificationResult.alternatives.length > 0" class="alternatives-card">
          <template #header>
            <div class="card-header">
              <el-icon><Grid /></el-icon>
              <span>{{ $t('toolIdentification.alternatives') }}</span>
            </div>
          </template>

          <div class="product-grid">
            <div
              v-for="product in identificationResult.alternatives"
              :key="`alt-${product.retailer}-${product.title}`"
              class="product-card alternative"
            >
              <div class="retailer-badge">{{ product.retailer }}</div>
              <img :src="product.image_url" :alt="product.title" />
              <div class="product-info">
                <h4>{{ product.title }}</h4>
                <div class="price">${{ product.price.toFixed(2) }}</div>
                <el-button
                  size="small"
                  :icon="Link"
                  @click="openProductLink(product.url)"
                >
                  {{ $t('common.viewProduct') }}
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- History section -->
      <el-card class="history-section" v-if="identificationHistory.length > 0">
        <template #header>
          <div class="card-header">
            <el-icon><Clock /></el-icon>
            <span>{{ $t('toolIdentification.recentHistory') }}</span>
            <el-button
              text
              :icon="View"
              style="margin-left: auto"
              @click="showFullHistory"
            >
              {{ $t('common.viewAll') }}
            </el-button>
          </div>
        </template>

        <el-timeline>
          <el-timeline-item
            v-for="item in identificationHistory.slice(0, 3)"
            :key="item.id"
            :timestamp="formatDate(item.search_timestamp)"
          >
            <div class="history-item">
              <strong>{{ item.tool_info.name }}</strong>
              <span v-if="item.tool_info.brand"> - {{ item.tool_info.brand }} {{ item.tool_info.model }}</span>
              <el-button
                size="small"
                text
                :icon="Refresh"
                @click="loadHistoryItem(item)"
              >
                {{ $t('common.viewDetails') }}
              </el-button>
            </div>
          </el-timeline-item>
        </el-timeline>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import {
  Camera,
  Upload,
  Delete,
  Search,
  Tools,
  ShoppingCart,
  Grid,
  Link,
  Clock,
  View,
  Refresh,
  User,
  Lock
} from '@element-plus/icons-vue'
import { identifyToolAPI, getIdentificationHistory } from '@/api/toolIdentification'
import { useAuthStore } from '@/stores/auth'

const { t } = useI18n()
const router = useRouter()
const authStore = useAuthStore()

// Auth state
const isAuthenticated = computed(() => authStore.isAuthenticated)
const currentUser = computed(() => authStore.currentUser)

// Upload state
const imageFile = ref<File | null>(null)
const imagePreview = ref<string>('')
const includeAlternatives = ref(true)
const highAccuracy = ref(false)
const isIdentifying = ref(false)
const identifyingStage = ref('')
const showUpgradeDialog = ref(false)

// Results state
const identificationResult = ref<any>(null)
const identificationHistory = ref<any[]>([])

// Computed
const usagePercentage = computed(() => {
  if (!currentUser.value) return 0
  return (currentUser.value.dailyUsed / currentUser.value.dailyLimit) * 100
})

const getProgressColor = computed(() => {
  const percentage = usagePercentage.value
  if (percentage < 50) return '#67c23a'
  if (percentage < 80) return '#e6a23c'
  return '#f56c6c'
})

// Methods
const getMembershipType = (level: string) => {
  switch (level) {
    case 'pro': return 'danger'
    case 'premium': return 'warning'
    default: return 'info'
  }
}

const beforeUpload = (file: File) => {
  const isValidType = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'].includes(file.type)
  const isValidSize = file.size / 1024 / 1024 < 10
  
  if (!isValidType) {
    ElMessage.error(t('toolIdentification.invalidFormat'))
    return false
  }
  if (!isValidSize) {
    ElMessage.error(t('toolIdentification.fileTooLarge'))
    return false
  }
  return false // Prevent auto upload
}

const handleImageChange = (file: any) => {
  imageFile.value = file.raw
  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreview.value = e.target?.result as string
  }
  reader.readAsDataURL(file.raw)
}

const clearImage = () => {
  imageFile.value = null
  imagePreview.value = ''
  identificationResult.value = null
}

const rotateImage = () => {
  // Placeholder for image rotation functionality
  ElMessage.info(t('toolIdentification.rotateNotImplemented'))
}

const identifyTool = async () => {
  if (!imageFile.value) {
    ElMessage.warning(t('toolIdentification.selectImage'))
    return
  }

  if (currentUser.value?.dailyUsed >= currentUser.value?.dailyLimit) {
    ElMessage.error(t('toolIdentification.quotaExceeded'))
    return
  }

  isIdentifying.value = true
  const stages = [
    t('toolIdentification.stage1'),
    t('toolIdentification.stage2'),
    t('toolIdentification.stage3'),
    t('toolIdentification.stage4')
  ]
  
  try {
    // Show identification stages
    for (let i = 0; i < stages.length; i++) {
      identifyingStage.value = stages[i]
      await new Promise(resolve => setTimeout(resolve, highAccuracy.value ? 1000 : 500))
    }
    
    const result = await identifyToolAPI(imageFile.value, includeAlternatives.value)
    identificationResult.value = result
    
    // Update user quota
    authStore.updateQuota(result.user_quota)
    
    // Refresh history
    await loadHistory()
    
    // Success message with confidence
    const confidence = (result.tool_info.confidence * 100).toFixed(0)
    ElMessage.success(
      `${t('toolIdentification.identifySuccess')} (${t('toolIdentification.confidence')}: ${confidence}%)`
    )
  } catch (error: any) {
    ElMessage.error(error.message || t('toolIdentification.identifyFailed'))
  } finally {
    isIdentifying.value = false
    identifyingStage.value = ''
  }
}

const openProductLink = (url: string) => {
  window.open(url, '_blank')
}

const loadHistory = async () => {
  try {
    const history = await getIdentificationHistory()
    identificationHistory.value = history.history
  } catch (error) {
    console.error('Failed to load history:', error)
  }
}

const loadHistoryItem = (item: any) => {
  identificationResult.value = item
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const showFullHistory = () => {
  router.push('/dashboard')
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString()
}

const goToLogin = () => {
  router.push('/login')
}

const goToRegister = () => {
  router.push('/register')
}

// Lifecycle
onMounted(() => {
  if (isAuthenticated.value) {
    loadHistory()
  }
})
</script>

<style scoped>
.tool-identification {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
}

@media (max-width: 768px) {
  .tool-identification {
    padding: 16px;
  }
  
  .identify-options {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .product-grid {
    grid-template-columns: 1fr;
  }
  
  .status-content {
    flex-direction: column;
    gap: 16px;
  }
}

.page-header {
  text-align: center;
  margin-bottom: 32px;
}

.page-header h1 {
  font-size: 32px;
  color: #303133;
  margin-bottom: 8px;
}

.subtitle {
  color: #606266;
  font-size: 16px;
}

.login-prompt {
  max-width: 500px;
  margin: 80px auto;
}

.prompt-content {
  text-align: center;
  padding: 40px;
}

.prompt-content h3 {
  margin: 16px 0;
  color: #303133;
}

.prompt-content p {
  color: #606266;
  margin-bottom: 24px;
}

.button-group {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.user-status {
  margin-bottom: 24px;
}

.status-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.usage-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.upload-section {
  margin-bottom: 32px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.upload-section:hover {
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
}

.tool-uploader {
  margin-bottom: 24px;
}

.tool-uploader :deep(.el-upload-dragger) {
  padding: 60px 40px;
  min-height: 400px;
  border: 2px dashed #dcdfe6;
  border-radius: 12px;
  background: linear-gradient(135deg, #f8f9ff 0%, #f0f2ff 100%);
  transition: all 0.3s ease;
  position: relative;
}

.tool-uploader :deep(.el-upload-dragger:hover) {
  border-color: #409eff;
  background: linear-gradient(135deg, #ecf5ff 0%, #e1efff 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(64, 158, 255, 0.15);
}

.upload-placeholder {
  text-align: center;
  width: 100%;
}

.upload-icon-wrapper {
  margin-bottom: 24px;
}

.upload-icon {
  font-size: 80px;
  color: #409eff;
  opacity: 0.8;
  transition: all 0.3s ease;
}

.upload-content h3 {
  font-size: 20px;
  color: #303133;
  margin-bottom: 12px;
  font-weight: 600;
}

.upload-subtitle {
  font-size: 14px;
  color: #606266;
  margin-bottom: 20px;
  line-height: 1.6;
}

.upload-formats {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-bottom: 24px;
}

.format-size {
  color: #909399;
  font-size: 12px;
  margin-left: 8px;
}

.upload-examples {
  border-top: 1px solid #f0f0f0;
  padding-top: 20px;
}

.upload-examples p {
  font-size: 13px;
  color: #909399;
  margin-bottom: 12px;
}

.example-tags {
  display: flex;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
}

.image-preview {
  position: relative;
  width: 100%;
  height: 100%;
}

.image-preview img {
  max-width: 100%;
  max-height: 400px;
  object-fit: contain;
}

.preview-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.6));
  color: white;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-actions {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  gap: 8px;
}

.image-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.identify-options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 24px;
  padding: 16px 0;
}

.option-card {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.3s ease;
}

.option-card:hover {
  border-color: #409eff;
  background: #f0f9ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.option-description {
  font-size: 13px;
  color: #909399;
  margin-top: 8px;
  line-height: 1.4;
}

.identify-button {
  font-size: 16px;
  font-weight: 600;
  padding: 12px 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
  transition: all 0.3s ease;
}

.identify-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(64, 158, 255, 0.4);
}

.quota-warning {
  margin-top: 16px;
}

.action-buttons {
  text-align: center;
  padding-top: 8px;
}

.results-section {
  animation: fadeIn 0.5s;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.tool-info-card,
.matches-card,
.alternatives-card,
.history-section {
  margin-bottom: 24px;
  background: white;
  border-radius: 12px;
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.tool-info-card:hover,
.matches-card:hover,
.alternatives-card:hover,
.history-section:hover {
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.user-status .el-card {
  background: white;
  border-radius: 12px;
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.specifications {
  margin-top: 16px;
}

.specifications h4 {
  margin-bottom: 12px;
  color: #303133;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
}

.product-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s;
  position: relative;
}

.product-card:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.product-card.alternative {
  background: #f5f7fa;
}

.retailer-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: #409eff;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  text-transform: uppercase;
  z-index: 1;
}

.product-card img {
  width: 100%;
  height: 180px;
  object-fit: cover;
  background: #f5f7fa;
}

.product-info {
  padding: 12px;
}

.product-info h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.price {
  font-size: 18px;
  font-weight: bold;
  color: #f56c6c;
  margin-bottom: 8px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.history-item strong {
  color: #303133;
}
</style>