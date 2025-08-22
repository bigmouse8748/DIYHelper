<template>
  <div class="dashboard-container">
    <!-- Dashboard Header -->
    <div class="dashboard-header">
      <div class="header-content">
        <div class="brand">
          <el-icon class="brand-icon"><Tools /></el-icon>
          <h1 class="brand-title">DIY Smart Assistant</h1>
        </div>
        <div class="header-actions">
          <el-dropdown @command="handleUserCommand">
            <el-button text class="user-dropdown">
              <el-icon><User /></el-icon>
              {{ authStore.user?.username }}
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  Profile
                </el-dropdown-item>
                <el-dropdown-item command="settings">
                  <el-icon><Setting /></el-icon>
                  Settings
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  Logout
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </div>

    <!-- Dashboard Content -->
    <div class="dashboard">
      <!-- Welcome Section -->
    <div class="welcome-section">
      <div class="welcome-content">
        <h1 class="welcome-title">Welcome to DIY Smart Assistant</h1>
        <p class="welcome-subtitle">Your intelligent companion for DIY projects and tool identification</p>
        <div class="user-info">
          <el-tag :type="userTypeColor" size="large">
            {{ authStore.user?.user_type?.toUpperCase() }}
          </el-tag>
          <span class="username">{{ authStore.user?.username }}</span>
        </div>
      </div>
      <div class="welcome-illustration">
        <el-icon class="illustration-icon"><Tools /></el-icon>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-section">
      <h2 class="section-title">Your Statistics</h2>
      <el-row :gutter="20">
        <el-col :xs="24" :sm="8" :md="8">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon tools">
                <el-icon><Search /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-number">{{ stats.toolsIdentified }}</div>
                <div class="stats-label">Tools Identified</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :sm="8" :md="8">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon projects">
                <el-icon><DataAnalysis /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-number">{{ stats.projectsAnalyzed }}</div>
                <div class="stats-label">Projects Analyzed</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :sm="8" :md="8">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon recommendations">
                <el-icon><ShoppingBag /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-number">{{ stats.recommendationsGiven }}</div>
                <div class="stats-label">Recommendations Given</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- Quick Actions -->
    <div class="actions-section">
      <h2 class="section-title">Quick Actions</h2>
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8">
          <el-card class="action-card" @click="navigateTo('tool-identification')">
            <div class="action-content">
              <el-icon class="action-icon"><Search /></el-icon>
              <h3 class="action-title">Tool Identification</h3>
              <p class="action-description">Upload an image to identify any tool instantly</p>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :sm="12" :md="8">
          <el-card class="action-card" @click="navigateTo('product-recommendation')">
            <div class="action-content">
              <el-icon class="action-icon"><ShoppingBag /></el-icon>
              <h3 class="action-title">Product Recommendation</h3>
              <p class="action-description">Get smart product recommendations for your projects</p>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :sm="12" :md="8">
          <el-card class="action-card" @click="navigateTo('project-analysis')">
            <div class="action-content">
              <el-icon class="action-icon"><DataAnalysis /></el-icon>
              <h3 class="action-title">Project Analysis</h3>
              <p class="action-description">Complete DIY project analysis</p>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- Recent Projects -->
    <div class="recent-section">
      <h2 class="section-title">Recent Projects</h2>
      <el-card>
        <div class="empty-state">
          <el-icon class="empty-icon"><DocumentAdd /></el-icon>
          <p>No recent projects yet. Start by identifying a tool or analyzing a project!</p>
        </div>
      </el-card>
    </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { useDeviceStore } from '@/stores/device'
import {
  Tools,
  Search,
  DataAnalysis,
  ShoppingBag,
  DocumentAdd,
  Setting,
  ArrowDown,
  User,
  SwitchButton
} from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const deviceStore = useDeviceStore()

const stats = reactive({
  toolsIdentified: 0,
  projectsAnalyzed: 0,
  recommendationsGiven: 0
})

const userTypeColor = computed(() => {
  const userType = authStore.user?.user_type
  switch (userType) {
    case 'premium': return 'success'
    case 'pro': return 'primary'
    case 'admin': return 'danger'
    default: return 'info'
  }
})

const navigateTo = (routeName: string) => {
  router.push({ name: routeName })
}

const handleUserCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      router.push({ name: 'profile' })
      break
    case 'settings':
      ElMessage.info('Settings are available in the dashboard below!')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm(
          'Are you sure you want to logout?',
          'Confirm Logout',
          {
            confirmButtonText: 'Logout',
            cancelButtonText: 'Cancel',
            type: 'warning'
          }
        )
        
        await authStore.logout()
        ElMessage.success('Logged out successfully')
        router.push({ name: 'home' })
      } catch (error) {
        // User cancelled
      }
      break
  }
}
</script>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  background: #f5f7fa;
}

.dashboard-header {
  background: white;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-icon {
  font-size: 28px;
  color: #667eea;
}

.brand-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.header-actions {
  display: flex;
  align-items: center;
}

.user-dropdown {
  color: #606266;
  font-weight: 500;
}

.user-dropdown:hover {
  color: #667eea;
}

.dashboard {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.welcome-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 40px;
  margin-bottom: 30px;
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.welcome-content {
  flex: 1;
}

.welcome-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 8px 0;
}

.welcome-subtitle {
  font-size: 18px;
  margin: 0 0 20px 0;
  opacity: 0.9;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.username {
  font-weight: 600;
  font-size: 16px;
}

.welcome-illustration {
  flex-shrink: 0;
  margin-left: 40px;
}

.illustration-icon {
  font-size: 120px;
  opacity: 0.3;
}

.section-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 20px 0;
  color: #303133;
}

.stats-section {
  margin-bottom: 40px;
}

.stats-card {
  margin-bottom: 20px;
}

.stats-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stats-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: white;
}

.stats-icon.tools {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stats-icon.projects {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stats-icon.recommendations {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stats-info {
  flex: 1;
}

.stats-number {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1;
}

.stats-label {
  font-size: 14px;
  color: #606266;
  margin-top: 4px;
}

.actions-section {
  margin-bottom: 40px;
}

.action-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.action-content {
  text-align: center;
  padding: 20px;
}

.action-icon {
  font-size: 48px;
  color: #667eea;
  margin-bottom: 16px;
}

.action-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.action-description {
  font-size: 14px;
  color: #606266;
  margin: 0;
  line-height: 1.5;
}

.recent-section {
  margin-bottom: 40px;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #909399;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

/* Responsive Design - Mobile */
@media (max-width: 768px) {
  .header-content {
    padding: 0 16px;
  }

  .brand-title {
    font-size: 16px;
  }

  .brand-icon {
    font-size: 24px;
  }

  .user-dropdown {
    font-size: 14px;
  }

  .dashboard {
    padding: 16px 12px;
  }

  .welcome-section {
    flex-direction: column;
    text-align: center;
    padding: 20px 16px;
    margin-bottom: 20px;
  }

  .welcome-illustration {
    margin-left: 0;
    margin-top: 16px;
  }

  .illustration-icon {
    font-size: 60px;
  }

  .welcome-title {
    font-size: 20px;
  }

  .welcome-subtitle {
    font-size: 14px;
  }

  .user-info {
    justify-content: center;
    flex-wrap: wrap;
    gap: 8px;
  }

  .section-title {
    font-size: 20px;
  }

}

/* Responsive Design - Tablet */
@media (min-width: 769px) and (max-width: 1024px) {
  .dashboard {
    padding: 0 16px;
  }

  .welcome-section {
    padding: 32px;
  }

  .welcome-title {
    font-size: 28px;
  }

  .illustration-icon {
    font-size: 100px;
  }
}
</style>