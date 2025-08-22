<template>
  <div class="main-layout">
    <el-container>
      <!-- Header -->
      <el-header class="main-header">
        <div class="header-left">
          <el-icon class="app-icon"><Tools /></el-icon>
          <h1 class="app-title">DIY Smart Assistant</h1>
        </div>
        
        <div class="header-center" v-if="!deviceStore.isMobile">
          <el-menu
            :default-active="$route.name"
            mode="horizontal"
            :ellipsis="false"
            @select="handleMenuSelect"
          >
            <el-menu-item index="dashboard">
              <el-icon><HomeFilled /></el-icon>
              <span>Home</span>
            </el-menu-item>
            <el-menu-item index="tool-identification">
              <el-icon><Search /></el-icon>
              <span>Tool Identification</span>
            </el-menu-item>
            <el-menu-item index="smart-tool-finder">
              <el-icon><ChatLineRound /></el-icon>
              <span>Smart Tool Finder</span>
            </el-menu-item>
            <el-menu-item index="project-analysis">
              <el-icon><DataAnalysis /></el-icon>
              <span>Project Analysis</span>
            </el-menu-item>
            <el-menu-item index="our-picks">
              <el-icon><Star /></el-icon>
              <span>Our Picks</span>
            </el-menu-item>
          </el-menu>
        </div>
        
        <div class="header-right">
          <!-- User Menu -->
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
      </el-header>
      
      <!-- Main Content -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { useDeviceStore } from '@/stores/device'
import {
  Tools,
  HomeFilled,
  Search,
  ChatLineRound,
  DataAnalysis,
  Star,
  User,
  ArrowDown,
  Setting,
  SwitchButton
} from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const deviceStore = useDeviceStore()

const handleMenuSelect = (key: string) => {
  router.push({ name: key })
}

const handleUserCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      router.push({ name: 'profile' })
      break
    case 'settings':
      ElMessage.info('Settings page coming soon!')
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
        router.push({ name: 'landing' })
      } catch (error) {
        // User cancelled
      }
      break
  }
}
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
}

.main-header {
  background: white;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
  height: 60px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 200px;
}

.app-icon {
  font-size: 28px;
  color: #667eea;
}

.app-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.header-center .el-menu {
  border-bottom: none;
  background: transparent;
}

.header-center .el-menu-item {
  border-bottom: 2px solid transparent;
}

.header-center .el-menu-item.is-active {
  border-bottom-color: #667eea;
  color: #667eea;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
  min-width: 200px;
  justify-content: flex-end;
}

.user-dropdown {
  color: #606266;
  font-weight: 500;
}

.user-dropdown:hover {
  color: #667eea;
}

.main-content {
  background: #f5f7fa;
  padding: 20px;
  min-height: calc(100vh - 60px);
}

/* Responsive Design - Desktop First */
@media (max-width: 768px) {
  .main-header {
    padding: 0 16px;
  }
  
  .app-title {
    font-size: 16px;
  }
  
  .header-left {
    min-width: auto;
    gap: 8px;
  }
  
  .header-right {
    min-width: auto;
  }
  
  .user-dropdown {
    font-size: 14px;
  }
}

/* Tablet specific adjustments */
@media (min-width: 769px) and (max-width: 1024px) {
  .header-center .el-menu-item {
    padding: 0 12px;
  }
  
  .header-center .el-menu-item span {
    display: none;
  }
}
</style>