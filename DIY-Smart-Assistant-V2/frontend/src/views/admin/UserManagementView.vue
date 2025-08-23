<template>
  <div class="user-management">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">User Management</h1>
        <p class="page-subtitle">Manage users, permissions, and account settings</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="fetchUsers" :loading="loading">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
        <el-button type="success" @click="showCreateUserDialog">
          <el-icon><Plus /></el-icon>
          Add User
        </el-button>
      </div>
    </div>

    <!-- Filters and Search -->
    <el-card class="filters-card">
      <el-row :gutter="16" align="middle">
        <el-col :xs="24" :sm="8" :md="6">
          <el-input
            v-model="searchQuery"
            placeholder="Search users by name, email..."
            @input="handleSearch"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        
        <el-col :xs="24" :sm="6" :md="4">
          <el-select v-model="userTypeFilter" placeholder="User Type" @change="handleFilter" clearable>
            <el-option label="Admin" value="admin"></el-option>
            <el-option label="Premium" value="premium"></el-option>
            <el-option label="Pro" value="pro"></el-option>
            <el-option label="Free" value="free"></el-option>
          </el-select>
        </el-col>
        
        <el-col :xs="24" :sm="6" :md="4">
          <el-select v-model="activeFilter" placeholder="Status" @change="handleFilter" clearable>
            <el-option label="Active" :value="true"></el-option>
            <el-option label="Inactive" :value="false"></el-option>
          </el-select>
        </el-col>
        
        <el-col :xs="24" :sm="4" :md="3">
          <el-button @click="clearFilters" text>Clear All</el-button>
        </el-col>
        
        <el-col :xs="24" :sm="12" :md="7">
          <div class="user-stats">
            <span>Total Users: <strong>{{ totalUsers }}</strong></span>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- Users Table -->
    <el-card class="users-table-card">
      <el-table 
        :data="users" 
        v-loading="loading"
        stripe
        style="width: 100%"
        empty-text="No users found"
      >
        <el-table-column prop="id" label="ID" width="80" sortable />
        
        <el-table-column label="User" min-width="250">
          <template #default="scope">
            <div class="user-cell">
              <el-avatar 
                :size="40" 
                :src="scope.row.avatar_url || ''"
                class="user-avatar"
              >
                <el-icon><User /></el-icon>
              </el-avatar>
              <div class="user-info">
                <div class="user-name">{{ scope.row.username }}</div>
                <div class="user-email">{{ scope.row.email }}</div>
                <div v-if="scope.row.full_name" class="user-full-name">{{ scope.row.full_name }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="user_type" label="Type" width="100" sortable>
          <template #default="scope">
            <el-tag :type="getUserTypeColor(scope.row.user_type)" size="small">
              {{ scope.row.user_type?.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="is_active" label="Status" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'" size="small">
              {{ scope.row.is_active ? 'ACTIVE' : 'INACTIVE' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="email_verified" label="Email" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.email_verified ? 'success' : 'warning'" size="small">
              {{ scope.row.email_verified ? 'VERIFIED' : 'PENDING' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="last_login" label="Last Login" width="140" sortable>
          <template #default="scope">
            <span v-if="scope.row.last_login">{{ formatDate(scope.row.last_login) }}</span>
            <span v-else class="text-muted">Never</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="Created" width="140" sortable>
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="Actions" width="200" fixed="right">
          <template #default="scope">
            <el-button-group size="small">
              <el-button @click="viewUser(scope.row)" type="info" text>
                <el-icon><View /></el-icon>
                View
              </el-button>
              <el-button @click="editUser(scope.row)" type="primary" text>
                <el-icon><Edit /></el-icon>
                Edit
              </el-button>
              <el-button 
                @click="resetPassword(scope.row)" 
                type="warning" 
                text
                :disabled="scope.row.id === currentUserId"
              >
                <el-icon><Key /></el-icon>
                Reset
              </el-button>
              <el-button 
                @click="deleteUser(scope.row)" 
                type="danger" 
                text
                :disabled="scope.row.id === currentUserId"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :small="false"
          :disabled="loading"
          :total="totalUsers"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- User Form Dialog -->
    <el-dialog
      v-model="userDialogVisible"
      :title="editingUser ? 'Edit User' : 'Create New User'"
      width="600px"
    >
      <el-form
        ref="userFormRef"
        :model="userForm"
        :rules="userFormRules"
        label-width="120px"
      >
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="Username" prop="username">
              <el-input v-model="userForm.username" placeholder="Enter username" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="Email" prop="email">
              <el-input v-model="userForm.email" placeholder="Enter email" type="email" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="Full Name" prop="full_name">
              <el-input v-model="userForm.full_name" placeholder="Enter full name (optional)" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="User Type" prop="user_type">
              <el-select v-model="userForm.user_type" style="width: 100%">
                <el-option label="Free" value="free"></el-option>
                <el-option label="Pro" value="pro"></el-option>
                <el-option label="Premium" value="premium"></el-option>
                <el-option label="Admin" value="admin"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Phone" prop="phone">
              <el-input v-model="userForm.phone" placeholder="Phone number (optional)" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item>
              <el-checkbox v-model="userForm.is_active">Account Active</el-checkbox>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item>
              <el-checkbox v-model="userForm.email_verified">Email Verified</el-checkbox>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20" v-if="!editingUser">
          <el-col :span="24">
            <el-form-item label="Password" prop="password">
              <el-input 
                v-model="userForm.password" 
                placeholder="Enter password" 
                type="password" 
                show-password
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="userDialogVisible = false">Cancel</el-button>
          <el-button 
            type="primary" 
            @click="handleUserSave"
            :loading="saving"
          >
            {{ editingUser ? 'Update User' : 'Create User' }}
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- User Detail Dialog -->
    <el-dialog
      v-model="userDetailVisible"
      title="User Details"
      width="500px"
    >
      <div v-if="selectedUser" class="user-details">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="User ID">{{ selectedUser.id }}</el-descriptions-item>
          <el-descriptions-item label="Username">{{ selectedUser.username }}</el-descriptions-item>
          <el-descriptions-item label="Email">{{ selectedUser.email }}</el-descriptions-item>
          <el-descriptions-item label="Full Name">{{ selectedUser.full_name || 'Not provided' }}</el-descriptions-item>
          <el-descriptions-item label="Phone">{{ selectedUser.phone || 'Not provided' }}</el-descriptions-item>
          <el-descriptions-item label="Location">{{ selectedUser.location || 'Not provided' }}</el-descriptions-item>
          <el-descriptions-item label="User Type">
            <el-tag :type="getUserTypeColor(selectedUser.user_type)">
              {{ selectedUser.user_type?.toUpperCase() }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="selectedUser.is_active ? 'success' : 'danger'">
              {{ selectedUser.is_active ? 'ACTIVE' : 'INACTIVE' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Email Status">
            <el-tag :type="selectedUser.email_verified ? 'success' : 'warning'">
              {{ selectedUser.email_verified ? 'VERIFIED' : 'PENDING' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Created">{{ formatDate(selectedUser.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="Last Login">
            {{ selectedUser.last_login ? formatDate(selectedUser.last_login) : 'Never' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  User,
  Search,
  Refresh,
  Plus,
  Edit,
  View,
  Delete,
  Key
} from '@element-plus/icons-vue'
import axios from 'axios'

// API configuration
const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000') + '/api/v1'
const getAuthToken = () => localStorage.getItem('access_token')

// Current admin user ID (from token)
const currentUserId = ref(4)

// State
const loading = ref(false)
const saving = ref(false)
const users = ref<any[]>([])
const totalUsers = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

// Filters
const searchQuery = ref('')
const userTypeFilter = ref('')
const activeFilter = ref<boolean | null>(null)

// Dialog states
const userDialogVisible = ref(false)
const userDetailVisible = ref(false)
const editingUser = ref<any>(null)
const selectedUser = ref<any>(null)
const userFormRef = ref()

// User form
const userForm = reactive({
  username: '',
  email: '',
  full_name: '',
  phone: '',
  user_type: 'free',
  is_active: true,
  email_verified: false,
  password: ''
})

// Form validation rules
const userFormRules = {
  username: [
    { required: true, message: 'Username is required', trigger: 'blur' },
    { min: 3, max: 30, message: 'Username must be 3-30 characters', trigger: 'blur' }
  ],
  email: [
    { required: true, message: 'Email is required', trigger: 'blur' },
    { type: 'email', message: 'Please enter a valid email', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Password is required', trigger: 'blur' },
    { min: 6, message: 'Password must be at least 6 characters', trigger: 'blur' }
  ]
}

// API helper
const apiRequest = (method: string, url: string, data?: any) => {
  const token = getAuthToken()
  if (!token) {
    throw new Error('No authentication token found. Please login again.')
  }
  return axios({
    method,
    url: `${API_BASE_URL}${url}`,
    data,
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  })
}

// Fetch users from database
const fetchUsers = async () => {
  try {
    loading.value = true
    
    const params = new URLSearchParams({
      page: currentPage.value.toString(),
      size: pageSize.value.toString()
    })
    
    if (searchQuery.value) {
      params.append('search', searchQuery.value)
    }
    
    if (userTypeFilter.value) {
      params.append('user_type', userTypeFilter.value)
    }
    
    if (activeFilter.value !== null) {
      params.append('is_active', activeFilter.value.toString())
    }
    
    const response = await apiRequest('GET', `/users/admin/users?${params.toString()}`)
    
    users.value = response.data.users || []
    totalUsers.value = response.data.total_count || 0
    
  } catch (error: any) {
    console.error('Failed to fetch users:', error)
    ElMessage.error('Failed to load users: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// User type color mapping
const getUserTypeColor = (type: string) => {
  const colors = {
    'admin': 'danger',
    'premium': 'warning',
    'pro': 'primary',
    'free': 'info'
  }
  return colors[type as keyof typeof colors] || 'info'
}

// Format date
const formatDate = (date: string | null) => {
  if (!date) return 'Never'
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Handle search with debouncing
let searchTimeout: ReturnType<typeof setTimeout>
const handleSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    fetchUsers()
  }, 500)
}

// Handle filter change
const handleFilter = () => {
  currentPage.value = 1
  fetchUsers()
}

// Clear all filters
const clearFilters = () => {
  searchQuery.value = ''
  userTypeFilter.value = ''
  activeFilter.value = null
  currentPage.value = 1
  fetchUsers()
}

// Pagination handlers
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  fetchUsers()
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  fetchUsers()
}

// Show create user dialog
const showCreateUserDialog = () => {
  editingUser.value = null
  resetUserForm()
  userDialogVisible.value = true
}

// Reset user form
const resetUserForm = () => {
  Object.assign(userForm, {
    username: '',
    email: '',
    full_name: '',
    phone: '',
    user_type: 'free',
    is_active: true,
    email_verified: false,
    password: ''
  })
}

// View user details
const viewUser = (user: any) => {
  selectedUser.value = user
  userDetailVisible.value = true
}

// Edit user
const editUser = (user: any) => {
  editingUser.value = user
  Object.assign(userForm, {
    username: user.username || '',
    email: user.email || '',
    full_name: user.full_name || '',
    phone: user.phone || '',
    user_type: user.user_type || 'free',
    is_active: user.is_active ?? true,
    email_verified: user.email_verified ?? false,
    password: '' // Don't populate password for editing
  })
  userDialogVisible.value = true
}

// Handle user save (create or update)
const handleUserSave = async () => {
  try {
    // Validate form
    const valid = await userFormRef.value?.validate()
    if (!valid) return
    
    saving.value = true
    
    const userData = { ...userForm }
    
    if (editingUser.value) {
      // Update existing user
      delete userData.password // Don't send password for updates
      await apiRequest('PUT', `/users/admin/users/${editingUser.value.id}`, userData)
      ElMessage.success('User updated successfully!')
    } else {
      // Create new user
      if (!userData.password) {
        ElMessage.error('Password is required for new users')
        return
      }
      await apiRequest('POST', '/users/admin/users', userData)
      ElMessage.success('User created successfully!')
    }
    
    userDialogVisible.value = false
    fetchUsers() // Refresh the list
    
  } catch (error: any) {
    console.error('Failed to save user:', error)
    ElMessage.error('Failed to save user: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

// Reset user password
const resetPassword = async (user: any) => {
  try {
    const { value: newPassword } = await ElMessageBox.prompt(
      `Enter new password for ${user.username}:`,
      'Reset Password',
      {
        confirmButtonText: 'Reset',
        cancelButtonText: 'Cancel',
        inputType: 'password',
        inputValidator: (value) => {
          if (!value || value.length < 6) {
            return 'Password must be at least 6 characters'
          }
          return true
        }
      }
    )
    
    await apiRequest('PUT', `/users/admin/users/${user.id}/password`, {
      new_password: newPassword
    })
    
    ElMessage.success(`Password reset successfully for ${user.username}`)
    
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Failed to reset password:', error)
      ElMessage.error('Failed to reset password: ' + (error.response?.data?.detail || error.message))
    }
  }
}

// Delete user
const deleteUser = async (user: any) => {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to delete user "${user.username}"? This action cannot be undone.`,
      'Delete User',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning',
      }
    )
    
    await apiRequest('DELETE', `/users/admin/users/${user.id}`)
    ElMessage.success(`User ${user.username} deleted successfully`)
    fetchUsers() // Refresh the list
    
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Failed to delete user:', error)
      ElMessage.error('Failed to delete user: ' + (error.response?.data?.detail || error.message))
    }
  }
}

// Load users on component mount
onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.user-management {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-content h1 {
  margin: 0;
  color: #2c3e50;
  font-size: 24px;
  font-weight: 600;
}

.header-content p {
  margin: 5px 0 0 0;
  color: #7f8c8d;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.filters-card {
  margin-bottom: 20px;
}

.user-stats {
  text-align: right;
  color: #666;
  font-size: 14px;
}

.users-table-card {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  flex: 1;
}

.user-name {
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 2px;
}

.user-email {
  font-size: 12px;
  color: #7f8c8d;
  margin-bottom: 1px;
}

.user-full-name {
  font-size: 11px;
  color: #95a5a6;
}

.text-muted {
  color: #95a5a6;
  font-style: italic;
}

.pagination-wrapper {
  margin-top: 20px;
  text-align: center;
}

.user-details {
  padding: 10px 0;
}

.el-descriptions {
  margin-top: 20px;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 15px;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .user-stats {
    text-align: left;
  }
}
</style>