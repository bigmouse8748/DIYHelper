<template>
  <div class="admin-dashboard" v-loading="loading">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">Admin Dashboard</h1>
        <p class="page-subtitle">System overview and analytics</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Statistics Overview -->
    <div class="stats-overview">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :lg="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon users">
                <el-icon><User /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-number">{{ stats.totalUsers }}</div>
                <div class="stats-label">Total Users</div>
                <div class="stats-change positive">+{{ stats.newUsersToday }} today</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :sm="12" :lg="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon tools">
                <el-icon><Search /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-number">{{ stats.toolsIdentified }}</div>
                <div class="stats-label">Tools Identified</div>
                <div class="stats-change positive">+{{ stats.toolsToday }} today</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :sm="12" :lg="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon projects">
                <el-icon><DataAnalysis /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-number">{{ stats.projectsAnalyzed }}</div>
                <div class="stats-label">Projects Analyzed</div>
                <div class="stats-change positive">+{{ stats.projectsToday }} today</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :sm="12" :lg="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon recommendations">
                <el-icon><ShoppingBag /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-number">{{ stats.recommendations }}</div>
                <div class="stats-label">Recommendations</div>
                <div class="stats-change positive">+{{ stats.recommendationsToday }} today</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- Charts and Analytics -->
    <div class="analytics-section">
      <el-row :gutter="20">
        <!-- User Activity Chart -->
        <el-col :xs="24" :lg="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span class="card-title">User Activity (Last 7 Days)</span>
                <el-tag type="info" size="small">Daily</el-tag>
              </div>
            </template>
            <div class="chart-placeholder">
              <el-icon class="chart-icon"><TrendCharts /></el-icon>
              <p>Chart visualization would be displayed here</p>
              <p class="chart-note">Integration with Chart.js or ECharts coming soon</p>
            </div>
          </el-card>
        </el-col>
        
        <!-- Feature Usage -->
        <el-col :xs="24" :lg="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span class="card-title">Feature Usage</span>
                <el-tag type="success" size="small">This Month</el-tag>
              </div>
            </template>
            <div class="feature-usage">
              <div class="usage-item">
                <div class="usage-info">
                  <span class="usage-name">Tool Identification</span>
                  <span class="usage-percent">{{ featureUsage.toolIdentification }}%</span>
                </div>
                <el-progress :percentage="featureUsage.toolIdentification" :show-text="false" />
              </div>
              <div class="usage-item">
                <div class="usage-info">
                  <span class="usage-name">Smart Tool Finder</span>
                  <span class="usage-percent">{{ featureUsage.smartToolFinder }}%</span>
                </div>
                <el-progress :percentage="featureUsage.smartToolFinder" :show-text="false" />
              </div>
              <div class="usage-item">
                <div class="usage-info">
                  <span class="usage-name">Project Analysis</span>
                  <span class="usage-percent">{{ featureUsage.projectAnalysis }}%</span>
                </div>
                <el-progress :percentage="featureUsage.projectAnalysis" :show-text="false" />
              </div>
              <div class="usage-item">
                <div class="usage-info">
                  <span class="usage-name">Our Picks</span>
                  <span class="usage-percent">{{ featureUsage.ourPicks }}%</span>
                </div>
                <el-progress :percentage="featureUsage.ourPicks" :show-text="false" />
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- Recent Activity -->
    <div class="activity-section">
      <el-card>
        <template #header>
          <div class="card-header">
            <span class="card-title">Recent System Activity</span>
            <el-button type="primary" text @click="viewAllActivity">View All</el-button>
          </div>
        </template>
        
        <div class="activity-list">
          <div 
            v-for="activity in recentActivity" 
            :key="activity.id"
            class="activity-item"
          >
            <div class="activity-icon" :class="activity.type">
              <el-icon>
                <component :is="activity.icon" />
              </el-icon>
            </div>
            <div class="activity-content">
              <div class="activity-title">{{ activity.title }}</div>
              <div class="activity-description">{{ activity.description }}</div>
              <div class="activity-meta">
                <span class="activity-user">{{ activity.user }}</span>
                <span class="activity-time">{{ formatTime(activity.timestamp) }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  User,
  Search,
  DataAnalysis,
  ShoppingBag,
  Refresh,
  TrendCharts
} from '@element-plus/icons-vue'
import api from '@/utils/api'

// State
const stats = reactive({
  totalUsers: 0,
  newUsersToday: 0,
  toolsIdentified: 0,
  toolsToday: 0,
  projectsAnalyzed: 0,
  projectsToday: 0,
  recommendations: 0,
  recommendationsToday: 0
})

const recentActivity = ref([])
const featureUsage = reactive({
  toolIdentification: 0,
  smartToolFinder: 0,
  projectAnalysis: 0,
  ourPicks: 0
})
const loading = ref(false)

// Methods
const fetchDashboardData = async () => {
  loading.value = true
  try {
    // Fetch statistics
    const statsResponse = await api.get('/api/v1/admin/dashboard/stats')
    if (statsResponse.data) {
      stats.totalUsers = statsResponse.data.total_users || 0
      stats.newUsersToday = statsResponse.data.new_users_today || 0
      stats.toolsIdentified = statsResponse.data.tools_identified || 0
      stats.toolsToday = statsResponse.data.tools_today || 0
      stats.projectsAnalyzed = statsResponse.data.projects_analyzed || 0
      stats.projectsToday = statsResponse.data.projects_today || 0
      stats.recommendations = statsResponse.data.recommendations || 0
      stats.recommendationsToday = statsResponse.data.recommendations_today || 0
    }

    // Fetch recent activity
    const activityResponse = await api.get('/api/v1/admin/dashboard/recent-activity')
    if (activityResponse.data) {
      recentActivity.value = activityResponse.data
    }

    // Fetch feature usage
    const usageResponse = await api.get('/api/v1/admin/dashboard/feature-usage')
    if (usageResponse.data) {
      featureUsage.toolIdentification = usageResponse.data.tool_identification || 0
      featureUsage.smartToolFinder = usageResponse.data.smart_tool_finder || 0
      featureUsage.projectAnalysis = usageResponse.data.project_analysis || 0
      featureUsage.ourPicks = usageResponse.data.our_picks || 0
    }
  } catch (error: any) {
    console.error('Failed to fetch dashboard data:', error)
    ElMessage.error('Failed to load dashboard data')
  } finally {
    loading.value = false
  }
}

const refreshData = async () => {
  try {
    await fetchDashboardData()
    ElMessage.success('Data refreshed successfully!')
  } catch (error) {
    ElMessage.error('Failed to refresh data')
  }
}

const viewAllActivity = () => {
  ElMessage.info('Full activity log feature coming soon!')
}

const formatTime = (timestamp: string) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60))
  
  if (diffMinutes < 1) return 'Just now'
  if (diffMinutes < 60) return `${diffMinutes} minutes ago`
  
  const diffHours = Math.floor(diffMinutes / 60)
  if (diffHours < 24) return `${diffHours} hours ago`
  
  return date.toLocaleDateString()
}

// Lifecycle
onMounted(() => {
  fetchDashboardData()
})
</script>

<style scoped>
.admin-dashboard {
  max-width: 1400px;
  margin: 0 auto;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.header-content h1.page-title {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 4px 0;
}

.page-subtitle {
  color: #606266;
  margin: 0;
  font-size: 16px;
}

/* Statistics Overview */
.stats-overview {
  margin-bottom: 32px;
}

.stats-card {
  height: 120px;
  margin-bottom: 16px;
}

.stats-content {
  display: flex;
  align-items: center;
  gap: 16px;
  height: 100%;
}

.stats-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
  flex-shrink: 0;
}

.stats-icon.users {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stats-icon.tools {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stats-icon.projects {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stats-icon.recommendations {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stats-info {
  flex: 1;
}

.stats-number {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.stats-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 4px;
}

.stats-change {
  font-size: 12px;
  font-weight: 500;
}

.stats-change.positive {
  color: #67c23a;
}

/* Analytics Section */
.analytics-section {
  margin-bottom: 32px;
}

.chart-card {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-weight: 600;
  color: #303133;
}

.chart-placeholder {
  height: 300px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #909399;
  background: #f8f9fa;
  border-radius: 8px;
}

.chart-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.chart-note {
  font-size: 12px;
  margin: 8px 0 0 0;
}

/* Feature Usage */
.feature-usage {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 16px 0;
}

.usage-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.usage-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.usage-name {
  font-weight: 500;
  color: #303133;
}

.usage-percent {
  font-weight: 600;
  color: #606266;
}

/* Activity Section */
.activity-section {
  margin-bottom: 32px;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  border-radius: 8px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  transition: all 0.3s ease;
}

.activity-item:hover {
  background: #f5f7fa;
  border-color: #d9d9d9;
}

.activity-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
  flex-shrink: 0;
}

.activity-icon.user {
  background: #667eea;
}

.activity-icon.tool {
  background: #f56c6c;
}

.activity-icon.project {
  background: #409eff;
}

.activity-icon.recommendation {
  background: #67c23a;
}

.activity-content {
  flex: 1;
  min-width: 0;
}

.activity-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.activity-description {
  color: #606266;
  font-size: 14px;
  margin-bottom: 8px;
}

.activity-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #909399;
}

/* Responsive */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .header-actions {
    align-self: flex-start;
  }
  
  .chart-placeholder {
    height: 200px;
  }
  
  .activity-item {
    padding: 12px;
  }
  
  .activity-meta {
    flex-direction: column;
    gap: 4px;
  }
}
</style>