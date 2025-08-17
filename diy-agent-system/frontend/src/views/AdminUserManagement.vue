<template>
  <div class="admin-user-management">
    <div class="page-header">
      <div class="header-content">
        <h1>{{ $t('admin.users.title') }}</h1>
        <p class="subtitle">{{ $t('admin.users.subtitle') }}</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="showAddUserDialog = true" :icon="Plus">
          {{ $t('admin.users.addUser') }}
        </el-button>
        <el-button type="success" @click="exportUsers" :icon="Download">
          {{ $t('admin.users.exportUsers') }}
        </el-button>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon total">
          <el-icon><User /></el-icon>
        </div>
        <div class="stat-content">
          <h3>{{ userStats.total }}</h3>
          <p>{{ $t('admin.users.stats.totalUsers') }}</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon active">
          <el-icon><Check /></el-icon>
        </div>
        <div class="stat-content">
          <h3>{{ userStats.active }}</h3>
          <p>{{ $t('admin.users.stats.activeUsers') }}</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon premium">
          <el-icon><Star /></el-icon>
        </div>
        <div class="stat-content">
          <h3>{{ userStats.premium }}</h3>
          <p>{{ $t('admin.users.stats.premiumUsers') }}</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon today">
          <el-icon><Calendar /></el-icon>
        </div>
        <div class="stat-content">
          <h3>{{ userStats.todayRegistrations }}</h3>
          <p>{{ $t('admin.users.stats.todayRegistrations') }}</p>
        </div>
      </div>
    </div>

    <!-- Filters and Search -->
    <div class="filter-section">
      <div class="search-controls">
        <el-input
          v-model="searchQuery"
          :placeholder="$t('admin.users.searchPlaceholder')"
          @input="debounceSearch"
          @clear="clearSearch"
          clearable
          size="large"
          class="search-input"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      
      <div class="filter-controls">
        <el-select 
          v-model="filterMembership" 
          @change="loadUsers"
          :placeholder="$t('admin.users.filterByMembership')"
          clearable
          size="default"
        >
          <el-option label="Free" value="free" />
          <el-option label="Premium" value="premium" />
          <el-option label="Pro" value="pro" />
          <el-option label="Admin" value="admin" />
        </el-select>
        
        <el-select 
          v-model="filterStatus" 
          @change="loadUsers"
          :placeholder="$t('admin.users.filterByStatus')"
          clearable
          size="default"
        >
          <el-option :label="$t('admin.users.status.active')" value="active" />
          <el-option :label="$t('admin.users.status.inactive')" value="inactive" />
        </el-select>
        
        <el-checkbox v-model="includeInactive" @change="loadUsers">
          {{ $t('admin.users.includeInactive') }}
        </el-checkbox>
      </div>
      
      <div class="batch-actions" v-if="selectedUsers.length > 0">
        <span class="selected-count">{{ $t('admin.users.selectedCount', { count: selectedUsers.length }) }}</span>
        <el-button size="small" @click="batchUpdateMembership" type="warning">
          {{ $t('admin.users.batchUpdateMembership') }}
        </el-button>
        <el-button size="small" @click="batchDeleteUsers" type="danger">
          {{ $t('admin.users.batchDelete') }}
        </el-button>
      </div>
    </div>

    <!-- Users Table -->
    <div class="users-section">
      <el-table 
        :data="users" 
        v-loading="loading"
        @selection-change="handleSelectionChange"
        stripe
        class="users-table"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="id" label="ID" width="70" />
        
        <el-table-column :label="$t('admin.users.table.user')" min-width="200">
          <template #default="scope">
            <div class="user-info">
              <div class="user-avatar">
                <el-avatar 
                  :size="40" 
                  :src="scope.row.avatar_url"
                  :class="{ inactive: !scope.row.is_active }"
                >
                  {{ scope.row.username.charAt(0).toUpperCase() }}
                </el-avatar>
              </div>
              <div class="user-details">
                <div class="username">{{ scope.row.username }}</div>
                <div class="email">{{ scope.row.email }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column :label="$t('admin.users.table.membership')" width="120">
          <template #default="scope">
            <el-tag 
              :type="getMembershipTagType(scope.row.membership_level)"
              size="small"
            >
              {{ scope.row.membership_level }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column :label="$t('admin.users.table.status')" width="100">
          <template #default="scope">
            <el-tag 
              :type="scope.row.is_active ? 'success' : 'danger'"
              size="small"
            >
              {{ scope.row.is_active ? $t('admin.users.status.active') : $t('admin.users.status.inactive') }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column :label="$t('admin.users.table.usage')" width="120">
          <template #default="scope">
            <div class="usage-info">
              <div class="usage-count">{{ scope.row.daily_identifications || 0 }}/{{ scope.row.daily_limit || 0 }}</div>
              <div class="usage-label">{{ $t('admin.users.dailyUsage') }}</div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column :label="$t('admin.users.table.registered')" width="130">
          <template #default="scope">
            <div class="date-info">
              <div class="date">{{ formatDate(scope.row.created_at) }}</div>
              <div class="time">{{ formatTime(scope.row.created_at) }}</div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column :label="$t('admin.users.table.lastLogin')" width="130">
          <template #default="scope">
            <div class="date-info" v-if="scope.row.last_login">
              <div class="date">{{ formatDate(scope.row.last_login) }}</div>
              <div class="time">{{ formatTime(scope.row.last_login) }}</div>
            </div>
            <span v-else class="never-login">{{ $t('admin.users.neverLoggedIn') }}</span>
          </template>
        </el-table-column>
        
        <el-table-column :label="$t('admin.users.table.actions')" width="280" fixed="right">
          <template #default="scope">
            <div class="action-buttons">
              <el-button size="small" @click="editUser(scope.row)" :icon="Edit">
                {{ $t('common.edit') }}
              </el-button>
              
              <el-dropdown @command="(command) => handleUserAction(command, scope.row)">
                <el-button size="small" type="primary">
                  {{ $t('admin.users.moreActions') }}
                  <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="resetPassword" :icon="Key">
                      {{ $t('admin.users.resetPassword') }}
                    </el-dropdown-item>
                    <el-dropdown-item command="toggleStatus" :icon="scope.row.is_active ? Minus : Plus">
                      {{ scope.row.is_active ? $t('admin.users.deactivate') : $t('admin.users.activate') }}
                    </el-dropdown-item>
                    <el-dropdown-item command="viewActivity" :icon="View">
                      {{ $t('admin.users.viewActivity') }}
                    </el-dropdown-item>
                    <el-dropdown-item command="forceLogout" :icon="SwitchButton">
                      {{ $t('admin.users.forceLogout') }}
                    </el-dropdown-item>
                    <el-dropdown-item command="delete" :icon="Delete" divided>
                      {{ $t('common.delete') }}
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <div v-if="!loading && users.length === 0" class="empty-state">
        <el-empty :description="$t('admin.users.noUsers')">
          <el-button type="primary" @click="showAddUserDialog = true">
            {{ $t('admin.users.addFirstUser') }}
          </el-button>
        </el-empty>
      </div>
      
      <!-- Pagination -->
      <div class="pagination-wrapper" v-if="users.length > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="totalUsers"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Add User Dialog -->
    <el-dialog 
      v-model="showAddUserDialog" 
      :title="$t('admin.users.addUser')"
      width="500px"
      @close="resetAddForm"
    >
      <el-form :model="addUserForm" :rules="addUserRules" ref="addUserFormRef" label-width="120px">
        <el-form-item :label="$t('admin.users.form.username')" prop="username">
          <el-input v-model="addUserForm.username" />
        </el-form-item>
        
        <el-form-item :label="$t('admin.users.form.email')" prop="email">
          <el-input v-model="addUserForm.email" type="email" />
        </el-form-item>
        
        <el-form-item :label="$t('admin.users.form.password')" prop="password">
          <el-input v-model="addUserForm.password" type="password" show-password />
        </el-form-item>
        
        <el-form-item :label="$t('admin.users.form.confirmPassword')" prop="confirmPassword">
          <el-input v-model="addUserForm.confirmPassword" type="password" show-password />
        </el-form-item>
        
        <el-form-item :label="$t('admin.users.form.membership')">
          <el-select v-model="addUserForm.membership_level" style="width: 100%">
            <el-option label="Free" value="free" />
            <el-option label="Premium" value="premium" />
            <el-option label="Pro" value="pro" />
            <el-option label="Admin" value="admin" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-checkbox v-model="addUserForm.is_active">
            {{ $t('admin.users.form.activeUser') }}
          </el-checkbox>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddUserDialog = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="createUser" :loading="saving">
          {{ $t('common.create') }}
        </el-button>
      </template>
    </el-dialog>

    <!-- Edit User Dialog -->
    <el-dialog 
      v-model="showEditUserDialog" 
      :title="$t('admin.users.editUser')"
      width="500px"
      @close="resetEditForm"
    >
      <el-form :model="editUserForm" :rules="editUserRules" ref="editUserFormRef" label-width="120px">
        <el-form-item :label="$t('admin.users.form.username')" prop="username">
          <el-input v-model="editUserForm.username" />
        </el-form-item>
        
        <el-form-item :label="$t('admin.users.form.email')" prop="email">
          <el-input v-model="editUserForm.email" type="email" />
        </el-form-item>
        
        <el-form-item :label="$t('admin.users.form.membership')">
          <el-select v-model="editUserForm.membership_level" style="width: 100%">
            <el-option label="Free" value="free" />
            <el-option label="Premium" value="premium" />
            <el-option label="Pro" value="pro" />
            <el-option label="Admin" value="admin" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-checkbox v-model="editUserForm.is_active">
            {{ $t('admin.users.form.activeUser') }}
          </el-checkbox>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showEditUserDialog = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="updateUser" :loading="saving">
          {{ $t('common.save') }}
        </el-button>
      </template>
    </el-dialog>

    <!-- Reset Password Dialog -->
    <el-dialog 
      v-model="showResetPasswordDialog" 
      :title="$t('admin.users.resetPassword')"
      width="400px"
      @close="resetPasswordForm"
    >
      <el-form :model="resetPasswordFormData" :rules="resetPasswordRules" ref="resetPasswordFormRef" label-width="120px">
        <el-form-item :label="$t('admin.users.form.user')">
          <el-input :value="selectedUser?.username" disabled />
        </el-form-item>
        
        <el-form-item :label="$t('admin.users.form.newPassword')" prop="newPassword">
          <el-input v-model="resetPasswordFormData.newPassword" type="password" show-password />
        </el-form-item>
        
        <el-form-item :label="$t('admin.users.form.confirmPassword')" prop="confirmPassword">
          <el-input v-model="resetPasswordFormData.confirmPassword" type="password" show-password />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showResetPasswordDialog = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="resetUserPassword" :loading="saving">
          {{ $t('common.save') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, Download, User, Check, Star, Calendar, Search, Edit, ArrowDown, 
  Key, Minus, View, SwitchButton, Delete 
} from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import axios from 'axios'

const { t } = useI18n()
const authStore = useAuthStore()
const router = useRouter()

// Check admin access
if (!authStore.isAuthenticated || authStore.currentUser?.membership_level !== 'admin') {
  ElMessage.error(t('admin.accessDenied'))
  router.push('/dashboard')
}

// Reactive data
const loading = ref(false)
const saving = ref(false)
const showAddUserDialog = ref(false)
const showEditUserDialog = ref(false)
const showResetPasswordDialog = ref(false)
const users = ref([])
const selectedUsers = ref([])
const selectedUser = ref(null)
const userStats = ref({
  total: 0,
  active: 0,
  premium: 0,
  todayRegistrations: 0
})

// Pagination
const currentPage = ref(1)
const pageSize = ref(20)
const totalUsers = ref(0)

// Filters
const searchQuery = ref('')
const filterMembership = ref('')
const filterStatus = ref('')
const includeInactive = ref(true)

// Search debouncing
let searchTimeout: NodeJS.Timeout | null = null

// Forms
const addUserFormRef = ref()
const addUserForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  membership_level: 'free',
  is_active: true
})

const editUserFormRef = ref()
const editUserForm = reactive({
  username: '',
  email: '',
  membership_level: 'free',
  is_active: true
})

const resetPasswordFormRef = ref()
const resetPasswordFormData = reactive({
  newPassword: '',
  confirmPassword: ''
})

// Validation rules
const addUserRules = {
  username: [
    { required: true, message: t('admin.users.validation.usernameRequired'), trigger: 'blur' },
    { min: 3, max: 50, message: t('admin.users.validation.usernameLength'), trigger: 'blur' }
  ],
  email: [
    { required: true, message: t('admin.users.validation.emailRequired'), trigger: 'blur' },
    { type: 'email', message: t('admin.users.validation.emailInvalid'), trigger: 'blur' }
  ],
  password: [
    { required: true, message: t('admin.users.validation.passwordRequired'), trigger: 'blur' },
    { min: 6, message: t('admin.users.validation.passwordLength'), trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: t('admin.users.validation.confirmPasswordRequired'), trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (value !== addUserForm.password) {
          callback(new Error(t('admin.users.validation.passwordMismatch')))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ]
}

const editUserRules = {
  username: [
    { required: true, message: t('admin.users.validation.usernameRequired'), trigger: 'blur' },
    { min: 3, max: 50, message: t('admin.users.validation.usernameLength'), trigger: 'blur' }
  ],
  email: [
    { required: true, message: t('admin.users.validation.emailRequired'), trigger: 'blur' },
    { type: 'email', message: t('admin.users.validation.emailInvalid'), trigger: 'blur' }
  ]
}

const resetPasswordRules = {
  newPassword: [
    { required: true, message: t('admin.users.validation.passwordRequired'), trigger: 'blur' },
    { min: 6, message: t('admin.users.validation.passwordLength'), trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: t('admin.users.validation.confirmPasswordRequired'), trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (value !== resetPasswordFormData.newPassword) {
          callback(new Error(t('admin.users.validation.passwordMismatch')))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ]
}

// API base URL
const API_BASE = import.meta.env.PROD ? 
  (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8002') : 
  'http://localhost:8002' // Direct backend URL for development

// Lifecycle
onMounted(async () => {
  await Promise.all([
    loadUsers(),
    loadUserStats()
  ])
})

// Methods
const loadUsers = async () => {
  try {
    loading.value = true
    const token = localStorage.getItem('access_token')
    
    const response = await axios.get(`${API_BASE}/api/admin/users`, {
      headers: { Authorization: `Bearer ${token}` },
      params: {
        page: currentPage.value,
        page_size: pageSize.value,
        search: searchQuery.value.trim() || undefined,
        membership: filterMembership.value || undefined,
        status: filterStatus.value || undefined,
        include_inactive: includeInactive.value
      }
    })
    
    if (response.data.success) {
      users.value = response.data.users
      totalUsers.value = response.data.total
    }
  } catch (error) {
    console.error('Error loading users:', error)
    ElMessage.error(t('admin.users.errors.loadFailed'))
  } finally {
    loading.value = false
  }
}

const loadUserStats = async () => {
  try {
    const token = localStorage.getItem('access_token')
    
    const response = await axios.get(`${API_BASE}/api/admin/users/stats`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    if (response.data.success) {
      userStats.value = response.data.stats
    }
  } catch (error) {
    console.error('Error loading user stats:', error)
  }
}

const debounceSearch = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    loadUsers()
  }, 500)
}

const clearSearch = () => {
  searchQuery.value = ''
  currentPage.value = 1
  loadUsers()
}

const handleSelectionChange = (selection) => {
  selectedUsers.value = selection
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadUsers()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadUsers()
}

// User actions
const createUser = async () => {
  if (!addUserFormRef.value) return
  
  try {
    await addUserFormRef.value.validate()
    saving.value = true
    
    const token = localStorage.getItem('access_token')
    
    const response = await axios.post(`${API_BASE}/api/admin/users`, addUserForm, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    if (response.data.success) {
      ElMessage.success(t('admin.users.messages.createSuccess'))
      showAddUserDialog.value = false
      resetAddForm()
      await loadUsers()
      await loadUserStats()
    }
  } catch (error) {
    console.error('Error creating user:', error)
    ElMessage.error(t('admin.users.errors.createFailed'))
  } finally {
    saving.value = false
  }
}

const editUser = (user) => {
  selectedUser.value = user
  Object.assign(editUserForm, {
    username: user.username,
    email: user.email,
    membership_level: user.membership_level,
    is_active: user.is_active
  })
  showEditUserDialog.value = true
}

const updateUser = async () => {
  if (!editUserFormRef.value || !selectedUser.value) return
  
  try {
    await editUserFormRef.value.validate()
    saving.value = true
    
    const token = localStorage.getItem('access_token')
    
    const response = await axios.put(`${API_BASE}/api/admin/users/${selectedUser.value.id}`, editUserForm, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    if (response.data.success) {
      ElMessage.success(t('admin.users.messages.updateSuccess'))
      showEditUserDialog.value = false
      resetEditForm()
      await loadUsers()
      await loadUserStats()
    }
  } catch (error) {
    console.error('Error updating user:', error)
    ElMessage.error(t('admin.users.errors.updateFailed'))
  } finally {
    saving.value = false
  }
}

const handleUserAction = async (command, user) => {
  selectedUser.value = user
  
  switch (command) {
    case 'resetPassword':
      showResetPasswordDialog.value = true
      break
    case 'toggleStatus':
      await toggleUserStatus(user)
      break
    case 'viewActivity':
      viewUserActivity(user)
      break
    case 'forceLogout':
      await forceUserLogout(user)
      break
    case 'delete':
      await deleteUser(user)
      break
  }
}

const resetUserPassword = async () => {
  if (!resetPasswordFormRef.value || !selectedUser.value) return
  
  try {
    await resetPasswordFormRef.value.validate()
    saving.value = true
    
    const token = localStorage.getItem('access_token')
    
    const response = await axios.post(`${API_BASE}/api/admin/users/${selectedUser.value.id}/reset-password`, {
      new_password: resetPasswordFormData.newPassword
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    if (response.data.success) {
      ElMessage.success(t('admin.users.messages.passwordResetSuccess'))
      showResetPasswordDialog.value = false
      resetPasswordForm()
    }
  } catch (error) {
    console.error('Error resetting password:', error)
    ElMessage.error(t('admin.users.errors.passwordResetFailed'))
  } finally {
    saving.value = false
  }
}

const toggleUserStatus = async (user) => {
  try {
    const token = localStorage.getItem('access_token')
    
    const response = await axios.post(`${API_BASE}/api/admin/users/${user.id}/toggle-status`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    if (response.data.success) {
      const action = user.is_active ? 'deactivated' : 'activated'
      ElMessage.success(t(`admin.users.messages.userStatus${action.charAt(0).toUpperCase() + action.slice(1)}`))
      await loadUsers()
      await loadUserStats()
    }
  } catch (error) {
    console.error('Error toggling user status:', error)
    ElMessage.error(t('admin.users.errors.statusToggleFailed'))
  }
}

const forceUserLogout = async (user) => {
  try {
    await ElMessageBox.confirm(
      t('admin.users.confirmForceLogout', { username: user.username }),
      t('admin.users.forceLogout'),
      {
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
        type: 'warning'
      }
    )
    
    const token = localStorage.getItem('access_token')
    
    const response = await axios.post(`${API_BASE}/api/admin/users/${user.id}/force-logout`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    if (response.data.success) {
      ElMessage.success(t('admin.users.messages.forceLogoutSuccess'))
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Error forcing logout:', error)
      ElMessage.error(t('admin.users.errors.forceLogoutFailed'))
    }
  }
}

const deleteUser = async (user) => {
  try {
    await ElMessageBox.confirm(
      t('admin.users.confirmDelete', { username: user.username }),
      t('common.delete'),
      {
        confirmButtonText: t('common.delete'),
        cancelButtonText: t('common.cancel'),
        type: 'warning'
      }
    )
    
    const token = localStorage.getItem('access_token')
    
    const response = await axios.delete(`${API_BASE}/api/admin/users/${user.id}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    if (response.data.success) {
      ElMessage.success(t('admin.users.messages.deleteSuccess'))
      await loadUsers()
      await loadUserStats()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Error deleting user:', error)
      ElMessage.error(t('admin.users.errors.deleteFailed'))
    }
  }
}

const viewUserActivity = (user) => {
  // TODO: Implement user activity view
  ElMessage.info(t('admin.users.messages.featureComingSoon'))
}

const batchUpdateMembership = async () => {
  // TODO: Implement batch membership update
  ElMessage.info(t('admin.users.messages.featureComingSoon'))
}

const batchDeleteUsers = async () => {
  // TODO: Implement batch delete
  ElMessage.info(t('admin.users.messages.featureComingSoon'))
}

const exportUsers = async () => {
  try {
    const token = localStorage.getItem('access_token')
    
    const response = await axios.get(`${API_BASE}/api/admin/users/export`, {
      headers: { Authorization: `Bearer ${token}` },
      responseType: 'blob'
    })
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `users_export_${new Date().toISOString().split('T')[0]}.csv`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    
    ElMessage.success(t('admin.users.messages.exportSuccess'))
  } catch (error) {
    console.error('Error exporting users:', error)
    ElMessage.error(t('admin.users.errors.exportFailed'))
  }
}

// Helper functions
const getMembershipTagType = (membership) => {
  switch (membership) {
    case 'admin': return 'danger'
    case 'pro': return 'warning'
    case 'premium': return 'success'
    default: return 'info'
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString()
}

const formatTime = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleTimeString()
}

// Reset forms
const resetAddForm = () => {
  Object.assign(addUserForm, {
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    membership_level: 'free',
    is_active: true
  })
  if (addUserFormRef.value) {
    addUserFormRef.value.clearValidate()
  }
}

const resetEditForm = () => {
  selectedUser.value = null
  Object.assign(editUserForm, {
    username: '',
    email: '',
    membership_level: 'free',
    is_active: true
  })
  if (editUserFormRef.value) {
    editUserFormRef.value.clearValidate()
  }
}

const resetPasswordForm = () => {
  Object.assign(resetPasswordFormData, {
    newPassword: '',
    confirmPassword: ''
  })
  if (resetPasswordFormRef.value) {
    resetPasswordFormRef.value.clearValidate()
  }
}
</script>

<style scoped>
.admin-user-management {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.header-content h1 {
  margin: 0;
  color: #303133;
  font-size: 2rem;
}

.subtitle {
  color: #606266;
  margin: 5px 0 0 0;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Statistics Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid #f0f0f0;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 24px;
  color: white;
}

.stat-icon.total { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.stat-icon.active { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
.stat-icon.premium { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
.stat-icon.today { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }

.stat-content h3 {
  margin: 0 0 4px 0;
  font-size: 2rem;
  font-weight: 700;
  color: #303133;
}

.stat-content p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

/* Filter Section */
.filter-section {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.search-controls {
  margin-bottom: 16px;
}

.search-input {
  max-width: 400px;
}

.filter-controls {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.batch-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 12px;
  background: #f0f9ff;
  border-radius: 8px;
  border: 1px solid #bfdbfe;
}

.selected-count {
  font-weight: 600;
  color: #1d4ed8;
}

/* Users Section */
.users-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.users-table {
  width: 100%;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  flex-shrink: 0;
}

.user-avatar .el-avatar.inactive {
  opacity: 0.5;
}

.user-details {
  flex: 1;
  min-width: 0;
}

.username {
  font-weight: 600;
  color: #303133;
  margin-bottom: 2px;
}

.email {
  color: #606266;
  font-size: 12px;
}

.usage-info {
  text-align: center;
}

.usage-count {
  font-weight: 600;
  color: #303133;
  margin-bottom: 2px;
}

.usage-label {
  color: #909399;
  font-size: 11px;
}

.date-info {
  text-align: center;
}

.date {
  color: #303133;
  margin-bottom: 2px;
  font-size: 12px;
}

.time {
  color: #909399;
  font-size: 11px;
}

.never-login {
  color: #c0c4cc;
  font-size: 12px;
  font-style: italic;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

@media (max-width: 768px) {
  .admin-user-management {
    padding: 15px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .filter-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .action-buttons {
    flex-direction: column;
  }
}
</style>