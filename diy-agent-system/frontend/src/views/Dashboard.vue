<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>{{ $t('nav.dashboard') }}</h1>
      <p>{{ $t('dashboard.subtitle') }}</p>
    </div>

    <!-- User info card -->
    <el-card class="user-card">
      <template #header>
        <div class="card-header">
          <el-icon><User /></el-icon>
          <span>{{ $t('dashboard.userInfo') }}</span>
          <div style="margin-left: auto; display: flex; gap: 8px;">
            <el-button 
              v-if="isAdmin"
              type="primary" 
              size="small"
              :icon="Setting"
              @click="goToAdminPanel"
            >
              {{ $t('admin.panel.title') }}
            </el-button>
            <el-button 
              text 
              type="primary" 
              @click="testAuth"
            >
              Debug Auth
            </el-button>
          </div>
        </div>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item :label="$t('auth.username')">
          {{ authStore.currentUser?.username }}
        </el-descriptions-item>
        <el-descriptions-item :label="$t('auth.email')">
          {{ authStore.currentUser?.email }}
        </el-descriptions-item>
        <el-descriptions-item :label="$t('membership.level')">
          <el-tag :type="getMembershipType(authStore.currentUser?.group)">
            {{ $t(`membership.${authStore.currentUser?.group || 'free'}`) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item :label="$t('toolIdentification.dailyUsage')">
          0 / {{ authStore.dailyQuota === -1 ? '∞' : authStore.dailyQuota }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- History section -->
    <el-card class="history-card">
      <template #header>
        <div class="card-header">
          <el-icon><Clock /></el-icon>
          <span>{{ $t('dashboard.identificationHistory') }}</span>
          <el-button 
            text 
            :icon="Refresh" 
            style="margin-left: auto"
            @click="loadHistory"
          >
            {{ $t('common.refresh') }}
          </el-button>
        </div>
      </template>

      <div v-if="isLoading" class="loading">
        <el-skeleton :rows="3" animated />
      </div>

      <div v-else-if="historyList.length === 0" class="empty-state">
        <el-empty :description="$t('dashboard.noHistory')" />
        <el-button type="primary" @click="goToToolIdentification">
          {{ $t('dashboard.startIdentifying') }}
        </el-button>
      </div>

      <div v-else class="history-list">
        <div 
          v-for="item in historyList" 
          :key="item.id" 
          class="history-item"
          @click="viewHistoryItem(item)"
        >
          <div class="history-content">
            <div class="tool-info">
              <h4>{{ item.tool_info.name }}</h4>
              <div class="tool-details">
                <span v-if="item.tool_info.brand">{{ item.tool_info.brand }}</span>
                <span v-if="item.tool_info.model">{{ item.tool_info.model }}</span>
                <el-tag size="small" type="info">{{ item.tool_info.category }}</el-tag>
              </div>
            </div>
            <div class="history-meta">
              <div class="confidence">
                {{ $t('toolIdentification.confidence') }}: {{ (item.tool_info.confidence * 100).toFixed(0) }}%
              </div>
              <div class="timestamp">{{ formatDate(item.search_timestamp) }}</div>
            </div>
          </div>
          <div class="history-actions">
            <el-button 
              size="small" 
              :icon="View"
              @click.stop="viewHistoryItem(item)"
            >
              {{ $t('common.viewDetails') }}
            </el-button>
            <el-button 
              size="small" 
              type="danger" 
              :icon="Delete"
              @click.stop="deleteHistoryItem(item.id)"
            >
              {{ $t('common.delete') }}
            </el-button>
          </div>
        </div>
      </div>

      <div v-if="historyList.length > 0" class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="totalHistory"
          layout="prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- Detailed view dialog -->
    <el-dialog
      v-model="showDetailDialog"
      :title="$t('common.viewDetails')"
      width="80%"
      max-width="1000px"
    >
      <div v-if="selectedHistory" class="history-detail">
        <!-- Tool information -->
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon><Tools /></el-icon>
              <span>{{ $t('toolIdentification.toolInfo') }}</span>
            </div>
          </template>
          
          <el-descriptions :column="2" border>
            <el-descriptions-item :label="$t('toolIdentification.toolName')">
              {{ selectedHistory.tool_info.name }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('toolIdentification.brand')">
              {{ selectedHistory.tool_info.brand || '-' }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('toolIdentification.model')">
              {{ selectedHistory.tool_info.model || '-' }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('toolIdentification.confidence')">
              {{ (selectedHistory.tool_info.confidence * 100).toFixed(0) }}%
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- Products found -->
        <el-card v-if="selectedHistory.exact_matches?.length > 0" style="margin-top: 16px;">
          <template #header>
            <span>{{ $t('toolIdentification.exactMatches') }}</span>
          </template>
          
          <div class="product-grid">
            <div 
              v-for="product in selectedHistory.exact_matches" 
              :key="`${product.retailer}-${product.title}`"
              class="product-card"
            >
              <img :src="product.image_url" :alt="product.title" />
              <div class="product-info">
                <h4>{{ product.title }}</h4>
                <div class="price">${{ product.price.toFixed(2) }}</div>
                <el-button 
                  size="small" 
                  type="primary"
                  @click="openProductLink(product.url)"
                >
                  {{ product.retailer }}
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  User,
  Clock,
  Refresh,
  View,
  Delete,
  Tools,
  Setting
} from '@element-plus/icons-vue'
import { getIdentificationHistory, deleteIdentification } from '@/api/toolIdentification'
import { useCognitoAuthStore } from '@/stores/cognitoAuth'
import { debugAuth } from '@/api/debug'

const { t } = useI18n()
const router = useRouter()
const authStore = useCognitoAuthStore()

// State
const isLoading = ref(false)
const historyList = ref<any[]>([])
const totalHistory = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const showDetailDialog = ref(false)
const selectedHistory = ref<any>(null)

// Computed
const getMembershipType = (group?: string) => {
  switch (group) {
    case 'admin': return 'danger'
    case 'premium': return 'warning'
    case 'pro': return 'success'
    case 'free': 
    default: return 'info'
  }
}

const isAdmin = computed(() => {
  return authStore.currentUser?.group === 'admin'
})

// Methods
const loadHistory = async () => {
  isLoading.value = true
  try {
    const result = await getIdentificationHistory(50) // Load more history for dashboard
    historyList.value = result.history
    totalHistory.value = result.total
  } catch (error) {
    console.error('Failed to load history:', error)
    ElMessage.error(t('dashboard.loadHistoryFailed'))
  } finally {
    isLoading.value = false
  }
}

const viewHistoryItem = (item: any) => {
  selectedHistory.value = item
  showDetailDialog.value = true
}

const deleteHistoryItem = async (id: string) => {
  try {
    await ElMessageBox.confirm(
      t('dashboard.confirmDelete'),
      t('common.confirm'),
      {
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
        type: 'warning'
      }
    )
    
    await deleteIdentification(id)
    ElMessage.success(t('dashboard.deleteSuccess'))
    loadHistory() // Reload history
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(t('dashboard.deleteFailed'))
    }
  }
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  // In a real app, you'd reload with pagination
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString()
}

const goToToolIdentification = () => {
  router.push('/tool-identification')
}

const goToAdminPanel = () => {
  router.push('/admin/products')
}

const openProductLink = (url: string) => {
  window.open(url, '_blank')
}

const testAuth = async () => {
  try {
    console.log('🧪 Testing authentication...')
    console.log('Current auth state:', {
      isAuthenticated: authStore.isAuthenticated,
      isAdmin: authStore.isAdmin,
      userGroups: authStore.userGroups,
      currentUser: authStore.currentUser
    })
    
    const result = await debugAuth()
    console.log('🎯 Auth test result:', result)
    
    ElMessage.success(`Auth test successful! Admin status: ${result.is_admin}`)
  } catch (error: any) {
    console.error('❌ Auth test failed:', error)
    ElMessage.error(`Auth test failed: ${error.response?.data?.detail || error.message}`)
  }
}

// Lifecycle
onMounted(() => {
  if (authStore.isAuthenticated) {
    loadHistory()
  }
})
</script>

<style scoped>
.dashboard {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 32px;
}

.dashboard-header h1 {
  font-size: 28px;
  color: #303133;
  margin-bottom: 8px;
}

.dashboard-header p {
  color: #606266;
}

.user-card,
.history-card {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.empty-state {
  text-align: center;
  padding: 40px;
}

.history-list {
  margin-bottom: 16px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.history-item:hover {
  border-color: #409eff;
  background: #f0f9ff;
}

.history-content {
  flex: 1;
}

.tool-info h4 {
  margin: 0 0 8px 0;
  color: #303133;
}

.tool-details {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 8px;
}

.history-meta {
  display: flex;
  gap: 16px;
  font-size: 14px;
  color: #909399;
}

.history-actions {
  display: flex;
  gap: 8px;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.product-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  text-align: center;
}

.product-card img {
  width: 100%;
  height: 120px;
  object-fit: cover;
}

.product-info {
  padding: 12px;
}

.product-info h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.price {
  font-size: 16px;
  font-weight: bold;
  color: #f56c6c;
  margin-bottom: 8px;
}
</style>