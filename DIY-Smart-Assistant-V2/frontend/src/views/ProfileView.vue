<template>
  <div class="profile">
    <div class="profile-container">
      <el-card class="profile-card">
        <template #header>
          <div class="profile-header">
            <h2>Profile</h2>
          </div>
        </template>
        
        <div class="profile-content">
          <div class="profile-avatar">
            <el-avatar :size="120" class="avatar">
              <el-icon><User /></el-icon>
            </el-avatar>
          </div>
          
          <div class="profile-info">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="Username">
                {{ authStore.user?.username }}
              </el-descriptions-item>
              <el-descriptions-item label="Email">
                {{ authStore.user?.email }}
              </el-descriptions-item>
              <el-descriptions-item label="Account Type">
                <el-tag :type="userTypeColor" size="large">
                  {{ authStore.user?.user_type?.toUpperCase() }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="Member Since">
                {{ formatDate(authStore.user?.created_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="Status">
                <el-tag :type="authStore.user?.is_active ? 'success' : 'danger'">
                  {{ authStore.user?.is_active ? 'Active' : 'Inactive' }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </div>
        
        <template #footer>
          <div class="profile-actions">
            <el-button type="primary" :icon="Edit">
              Edit Profile
            </el-button>
            <el-button :icon="Key">
              Change Password
            </el-button>
          </div>
        </template>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { User, Edit, Key } from '@element-plus/icons-vue'

const authStore = useAuthStore()

const userTypeColor = computed(() => {
  const userType = authStore.user?.user_type
  switch (userType) {
    case 'premium': return 'success'
    case 'pro': return 'primary'
    case 'admin': return 'danger'
    default: return 'info'
  }
})

const formatDate = (dateString?: string) => {
  if (!dateString) return 'Unknown'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}
</script>

<style scoped>
.profile {
  max-width: 800px;
  margin: 0 auto;
}

.profile-card {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.profile-header h2 {
  margin: 0;
  color: #303133;
}

.profile-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 30px;
}

.profile-avatar {
  text-align: center;
}

.avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 48px;
}

.profile-info {
  width: 100%;
}

.profile-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

/* Responsive Design */
@media (max-width: 768px) {
  .profile-actions {
    flex-direction: column;
  }
  
  .profile-actions .el-button {
    width: 100%;
  }
}
</style>