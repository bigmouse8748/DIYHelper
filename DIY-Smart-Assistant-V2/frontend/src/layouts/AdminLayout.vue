<template>
  <div class="admin-layout">
    <!-- Admin Header -->
    <header class="admin-header">
      <div class="header-container">
        <div class="brand-section">
          <el-icon class="brand-icon"><Tools /></el-icon>
          <h1 class="brand-title">DIY Admin Panel</h1>
        </div>
        
        <div class="header-actions">
          <el-button @click="navigateToUser" type="primary" text>
            <el-icon><ArrowLeft /></el-icon>
            Back to User Dashboard
          </el-button>
          
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
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  Logout
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </header>

    <!-- Admin Content -->
    <div class="admin-content">
      <!-- Sidebar Navigation -->
      <aside class="admin-sidebar">
        <nav class="sidebar-nav">
          <div class="nav-section">
            <h3 class="nav-section-title">Management</h3>
            <router-link 
              :to="{ name: 'admin-dashboard' }" 
              class="nav-item"
              active-class="nav-item-active"
            >
              <el-icon><DataAnalysis /></el-icon>
              <span>Dashboard</span>
            </router-link>
            
            <router-link 
              :to="{ name: 'admin-users' }" 
              class="nav-item"
              active-class="nav-item-active"
            >
              <el-icon><User /></el-icon>
              <span>Users</span>
            </router-link>
            
            <router-link 
              :to="{ name: 'admin-products' }" 
              class="nav-item"
              active-class="nav-item-active"
            >
              <el-icon><ShoppingBag /></el-icon>
              <span>Products</span>
            </router-link>
          </div>
          
          <div class="nav-section">
            <h3 class="nav-section-title">System</h3>
            <a href="#" class="nav-item" @click.prevent="showComingSoon">
              <el-icon><Setting /></el-icon>
              <span>Settings</span>
            </a>
            
            <a href="#" class="nav-item" @click.prevent="showComingSoon">
              <el-icon><DataAnalysis /></el-icon>
              <span>Analytics</span>
            </a>
          </div>
        </nav>
      </aside>

      <!-- Main Content Area -->
      <main class="admin-main">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import {
  Tools,
  User,
  ArrowDown,
  ArrowLeft,
  SwitchButton,
  DataAnalysis,
  ShoppingBag,
  Setting
} from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

const navigateToUser = () => {
  router.push({ name: 'dashboard' })
}

const showComingSoon = () => {
  ElMessage.info('This feature is coming soon!')
}

const handleUserCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      router.push({ name: 'profile' })
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
.admin-layout {
  min-height: 100vh;
  background: #f5f7fa;
}

/* Header */
.admin-header {
  background: #ffffff;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-container {
  max-width: 100%;
  padding: 0 24px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-icon {
  font-size: 28px;
  color: #f56c6c;
}

.brand-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-dropdown {
  color: #606266;
  font-weight: 500;
}

.user-dropdown:hover {
  color: #f56c6c;
}

/* Content Layout */
.admin-content {
  display: flex;
  min-height: calc(100vh - 64px);
}

/* Sidebar */
.admin-sidebar {
  width: 260px;
  background: #ffffff;
  border-right: 1px solid #e4e7ed;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.04);
  position: sticky;
  top: 64px;
  height: calc(100vh - 64px);
  overflow-y: auto;
}

.sidebar-nav {
  padding: 24px 0;
}

.nav-section {
  margin-bottom: 32px;
}

.nav-section-title {
  font-size: 12px;
  font-weight: 600;
  color: #909399;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 16px 0;
  padding: 0 24px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 24px;
  color: #606266;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
  border-right: 3px solid transparent;
}

.nav-item:hover {
  background: #f8f9fa;
  color: #f56c6c;
}

.nav-item-active {
  background: #fef0f0;
  color: #f56c6c;
  border-right-color: #f56c6c;
}

.nav-item .el-icon {
  font-size: 18px;
}

/* Main Content */
.admin-main {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

/* Responsive */
@media (max-width: 1024px) {
  .admin-sidebar {
    width: 220px;
  }
  
  .admin-main {
    padding: 16px;
  }
}

@media (max-width: 768px) {
  .header-container {
    padding: 0 16px;
  }
  
  .brand-title {
    font-size: 16px;
  }
  
  .admin-content {
    flex-direction: column;
  }
  
  .admin-sidebar {
    width: 100%;
    height: auto;
    position: static;
    border-right: none;
    border-bottom: 1px solid #e4e7ed;
  }
  
  .sidebar-nav {
    padding: 16px 0;
    display: flex;
    overflow-x: auto;
    gap: 16px;
  }
  
  .nav-section {
    margin-bottom: 0;
    min-width: 200px;
  }
  
  .nav-section-title {
    margin-bottom: 8px;
  }
  
  .nav-item {
    padding: 8px 16px;
    border-right: none;
    border-bottom: 3px solid transparent;
    white-space: nowrap;
  }
  
  .nav-item-active {
    border-right: none;
    border-bottom-color: #f56c6c;
  }
  
  .admin-main {
    padding: 16px 12px;
  }
}
</style>