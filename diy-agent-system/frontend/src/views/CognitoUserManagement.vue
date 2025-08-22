<template>
  <div class="user-management">
    <div class="page-header">
      <h1>{{ $t('admin.users.title') }}</h1>
      <p>{{ $t('admin.users.subtitle') }}</p>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-grid">
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-number">{{ userStats.totalUsers }}</div>
          <div class="stat-label">{{ $t('admin.users.userCount') }}</div>
        </div>
        <el-icon class="stat-icon" color="#409EFF"><User /></el-icon>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-number">{{ userStats.freeUsers }}</div>
          <div class="stat-label">Free Users</div>
        </div>
        <el-icon class="stat-icon" color="#67C23A"><UserFilled /></el-icon>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-number">{{ userStats.proUsers }}</div>
          <div class="stat-label">Pro Users</div>
        </div>
        <el-icon class="stat-icon" color="#E6A23C"><Star /></el-icon>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-number">{{ userStats.premiumUsers }}</div>
          <div class="stat-label">Premium Users</div>
        </div>
        <el-icon class="stat-icon" color="#F56C6C"><Crown /></el-icon>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-number">{{ userStats.adminUsers }}</div>
          <div class="stat-label">Admin Users</div>
        </div>
        <el-icon class="stat-icon" color="#909399"><Shield /></el-icon>
      </el-card>
    </div>

    <!-- User Management Table -->
    <el-card class="table-card">
      <template #header>
        <div class="table-header">
          <div class="table-title">
            <el-icon><List /></el-icon>
            <span>User List</span>
          </div>
          <div class="table-actions">
            <el-input
              v-model="searchQuery"
              :placeholder="$t('admin.users.searchPlaceholder')"
              style="width: 300px; margin-right: 16px"
              clearable
              @input="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button
              type="primary"
              :icon="Refresh"
              @click="loadUsers"
            >
              {{ $t('common.refresh') }}
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="filteredUsers"
        stripe
        style="width: 100%"
      >
        <el-table-column
          prop="username"
          label="Username"
          width="200"
          sortable
        />
        
        <el-table-column
          prop="email"
          label="Email"
          sortable
        />
        
        <el-table-column
          label="Groups"
          width="200"
        >
          <template #default="{ row }">
            <div v-if="row.groups.length > 0">
              <el-tag
                v-for="group in row.groups"
                :key="group"
                :type="getGroupTagType(group)"
                size="small"
                style="margin-right: 4px"
              >
                {{ group }}
              </el-tag>
            </div>
            <el-text v-else type="info" size="small">No groups</el-text>
          </template>
        </el-table-column>
        
        <el-table-column
          label="Status"
          width="120"
        >
          <template #default="{ row }">
            <el-tag
              :type="getStatusTagType(row.status)"
              size="small"
            >
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column
          prop="created"
          label="Created"
          width="180"
          sortable
        >
          <template #default="{ row }">
            {{ formatDate(row.created) }}
          </template>
        </el-table-column>
        
        <el-table-column
          label="Actions"
          width="200"
          fixed="right"
        >
          <template #default="{ row }">
            <el-dropdown trigger="click" @command="handleAction">
              <el-button
                text
                :icon="Setting"
                size="small"
              >
                Actions
                <el-icon><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item
                    :command="{ action: 'upgrade-free', user: row }"
                    :disabled="row.groups.includes('free')"
                  >
                    Set as Free
                  </el-dropdown-item>
                  <el-dropdown-item
                    :command="{ action: 'upgrade-pro', user: row }"
                    :disabled="row.groups.includes('pro')"
                  >
                    Upgrade to Pro
                  </el-dropdown-item>
                  <el-dropdown-item
                    :command="{ action: 'upgrade-premium', user: row }"
                    :disabled="row.groups.includes('premium')"
                  >
                    Upgrade to Premium
                  </el-dropdown-item>
                  <el-dropdown-item
                    :command="{ action: 'upgrade-admin', user: row }"
                    :disabled="row.groups.includes('admin')"
                    divided
                  >
                    Make Admin
                  </el-dropdown-item>
                  <el-dropdown-item
                    :command="{ action: 'delete', user: row }"
                    style="color: #f56c6c"
                    divided
                  >
                    Delete User
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <div class="table-footer">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="totalUsers"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handlePageSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- Create User Dialog -->
    <el-dialog
      v-model="showCreateDialog"
      title="Create New User"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="120px"
      >
        <el-form-item label="Email" prop="email">
          <el-input
            v-model="createForm.email"
            placeholder="Enter user email"
          />
        </el-form-item>
        
        <el-form-item label="Username" prop="username">
          <el-input
            v-model="createForm.username"
            placeholder="Enter username"
          />
        </el-form-item>
        
        <el-form-item label="Password" prop="password">
          <el-input
            v-model="createForm.password"
            type="password"
            placeholder="Enter password"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="Initial Group" prop="group">
          <el-select
            v-model="createForm.group"
            placeholder="Select initial group"
            style="width: 100%"
          >
            <el-option label="Free" value="free" />
            <el-option label="Pro" value="pro" />
            <el-option label="Premium" value="premium" />
            <el-option label="Admin" value="admin" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">
          {{ $t('common.cancel') }}
        </el-button>
        <el-button
          type="primary"
          :loading="creating"
          @click="handleCreateUser"
        >
          {{ $t('common.confirm') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  User,
  UserFilled,
  Star,
  Crown,
  Shield,
  List,
  Search,
  Refresh,
  Setting,
  ArrowDown
} from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import { listAllUsers, upgradeUserGroup } from '@/api/cognitoAPI'

const { t } = useI18n()

// State
const loading = ref(false)
const creating = ref(false)
const users = ref<any[]>([])
const totalUsers = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const searchQuery = ref('')
const showCreateDialog = ref(false)

// Create form
const createFormRef = ref()
const createForm = ref({
  email: '',
  username: '',
  password: '',
  group: 'free'
})

const createRules = {
  email: [
    { required: true, message: 'Email is required', trigger: 'blur' },
    { type: 'email', message: 'Invalid email format', trigger: 'blur' }
  ],
  username: [
    { required: true, message: 'Username is required', trigger: 'blur' },
    { min: 3, max: 20, message: 'Username must be 3-20 characters', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Password is required', trigger: 'blur' },
    { min: 8, message: 'Password must be at least 8 characters', trigger: 'blur' }
  ],
  group: [
    { required: true, message: 'Initial group is required', trigger: 'change' }
  ]
}

// Computed
const userStats = computed(() => {
  const stats = {
    totalUsers: users.value.length,
    freeUsers: 0,
    proUsers: 0,
    premiumUsers: 0,
    adminUsers: 0
  }
  
  users.value.forEach(user => {
    if (user.groups.includes('admin')) stats.adminUsers++
    else if (user.groups.includes('premium')) stats.premiumUsers++
    else if (user.groups.includes('pro')) stats.proUsers++
    else stats.freeUsers++
  })
  
  return stats
})

const filteredUsers = computed(() => {
  if (!searchQuery.value) return users.value
  
  const query = searchQuery.value.toLowerCase()
  return users.value.filter(user =>
    user.username.toLowerCase().includes(query) ||
    user.email.toLowerCase().includes(query) ||
    user.groups.some(group => group.toLowerCase().includes(query))
  )
})

// Methods
const loadUsers = async () => {
  loading.value = true
  try {
    const response = await listAllUsers(100) // Load more users
    users.value = response.users
    totalUsers.value = response.count
    
    ElMessage.success(`Loaded ${response.count} users from Cognito`)
  } catch (error) {
    console.error('Failed to load users:', error)
    ElMessage.error('Failed to load users from Cognito')
  } finally {
    loading.value = false
  }
}

const getGroupTagType = (group: string) => {
  switch (group) {
    case 'admin': return 'danger'
    case 'premium': return 'warning'
    case 'pro': return 'success'
    case 'free': return 'info'
    default: return ''
  }
}

const getStatusTagType = (status: string) => {
  switch (status) {
    case 'CONFIRMED': return 'success'
    case 'UNCONFIRMED': return 'warning'
    case 'FORCE_CHANGE_PASSWORD': return 'danger'
    case 'EXTERNAL_PROVIDER': return 'info'
    default: return 'info'
  }
}

const handleSearch = () => {
  // Search is handled by computed property
}

const handleAction = async ({ action, user }) => {
  try {
    if (action === 'delete') {
      await ElMessageBox.confirm(
        `Are you sure you want to delete user "${user.username}"?`,
        'Confirm Delete',
        {
          confirmButtonText: 'Delete',
          cancelButtonText: 'Cancel',
          type: 'warning'
        }
      )
      
      // TODO: Implement delete user API
      ElMessage.warning('Delete functionality not implemented yet')
      return
    }
    
    if (action.startsWith('upgrade-')) {
      const newGroup = action.replace('upgrade-', '')
      await upgradeUserGroup(user.email, newGroup)
      
      ElMessage.success(`User upgraded to ${newGroup} group`)
      loadUsers() // Reload users
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(`Action failed: ${error.message || error}`)
    }
  }
}

const handleCreateUser = async () => {
  try {
    await createFormRef.value?.validate()
    
    creating.value = true
    
    // TODO: Implement create user API
    ElMessage.warning('Create user functionality not implemented yet')
    
    showCreateDialog.value = false
    createForm.value = {
      email: '',
      username: '',
      password: '',
      group: 'free'
    }
    
  } catch (error) {
    console.error('Create user failed:', error)
  } finally {
    creating.value = false
  }
}

const handlePageChange = (page: number) => {
  currentPage.value = page
}

const handlePageSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString()
}

// Lifecycle
onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.user-management {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 28px;
  color: #303133;
  margin-bottom: 8px;
}

.page-header p {
  color: #606266;
  font-size: 14px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 8px;
}

.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.stat-icon {
  font-size: 32px;
  opacity: 0.8;
}

.table-card {
  border-radius: 8px;
}

.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.table-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.table-actions {
  display: flex;
  align-items: center;
}

.table-footer {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-table th) {
  background-color: #fafafa;
  font-weight: 600;
}

:deep(.el-pagination) {
  --el-pagination-font-size: 13px;
}
</style>