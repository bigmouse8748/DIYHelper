<template>
  <div class="project-analysis">
    <div class="page-header">
      <h1 class="page-title">Project Analysis</h1>
      <p class="page-subtitle">Upload project images for comprehensive DIY analysis</p>
    </div>

    <el-row :gutter="20">
      <!-- Upload Section -->
      <el-col :xs="24" :lg="12">
        <el-card class="upload-card">
          <template #header>
            <h3>Upload Project Images</h3>
          </template>
          
          <el-upload
            ref="uploadRef"
            class="upload-dragger"
            drag
            multiple
            :auto-upload="false"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            :before-upload="beforeUpload"
            accept="image/*"
            :limit="5"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              Drop images here or <em>click to upload</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                Upload 1-5 project images (JPG/PNG, max 10MB each)
              </div>
            </template>
          </el-upload>

          <div class="form-section">
            <el-form :model="projectForm" label-position="top">
              <el-form-item label="Project Description (optional)">
                <el-input
                  v-model="projectForm.description"
                  type="textarea"
                  :rows="3"
                  placeholder="Describe your project..."
                />
              </el-form-item>
              
              <el-form-item label="Project Type">
                <el-select v-model="projectForm.projectType" placeholder="Select type">
                  <el-option label="General" value="general" />
                  <el-option label="Woodworking" value="woodworking" />
                  <el-option label="Electronics" value="electronics" />
                  <el-option label="Metalworking" value="metalworking" />
                  <el-option label="Crafts" value="crafts" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="Budget Range">
                <el-select v-model="projectForm.budgetRange" placeholder="Select budget">
                  <el-option label="Under $50" value="under50" />
                  <el-option label="$50-150" value="50to150" />
                  <el-option label="$150-300" value="150to300" />
                  <el-option label="$300+" value="300plus" />
                </el-select>
              </el-form-item>
            </el-form>
          </div>

          <el-button 
            type="primary" 
            size="large" 
            @click="analyzeProject"
            :loading="loading"
            :disabled="!fileList.length"
            class="analyze-button"
          >
            <el-icon v-if="!loading"><search /></el-icon>
            {{ loading ? 'Analyzing...' : 'Analyze Project' }}
          </el-button>
        </el-card>
      </el-col>

      <!-- Results Section -->
      <el-col :xs="24" :lg="12">
        <el-card v-if="analysisResult" class="result-card">
          <template #header>
            <h3>Analysis Results</h3>
          </template>
          
          <div class="result-content">
            <pre>{{ JSON.stringify(analysisResult, null, 2) }}</pre>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { UploadProps, UploadUserFile } from 'element-plus'
// import { ElMessage } from 'element-plus' // Removed to fix setAttribute error
import { UploadFilled, Search } from '@element-plus/icons-vue'
import api from '@/utils/api'

const uploadRef = ref()
const fileList = ref<UploadUserFile[]>([])
const loading = ref(false)
const analysisResult = ref(null)

const projectForm = ref({
  description: '',
  projectType: 'general',
  budgetRange: '50to150'
})

const beforeUpload: UploadProps['beforeUpload'] = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isImage) {
    console.error('Please upload image files only!')
    return false
  }
  if (!isLt10M) {
    console.error('Image size must be less than 10MB!')
    return false
  }
  return true
}

const handleFileChange: UploadProps['onChange'] = (uploadFile, uploadFiles) => {
  fileList.value = uploadFiles
}

const handleFileRemove: UploadProps['onRemove'] = (uploadFile, uploadFiles) => {
  fileList.value = uploadFiles
}

const analyzeProject = async () => {
  if (fileList.value.length === 0) {
    console.error('Please upload at least one image')
    return
  }

  loading.value = true
  analysisResult.value = null
  
  try {
    console.log('Starting analysis with files:', fileList.value.length)
    
    const formData = new FormData()
    
    // Add files
    for (let i = 0; i < fileList.value.length; i++) {
      const file = fileList.value[i]
      if (file.raw) {
        formData.append('images', file.raw)
        console.log(`Added file ${i}: ${file.name}`)
      }
    }
    
    // Add project details
    formData.append('description', projectForm.value.description || '')
    formData.append('project_type', projectForm.value.projectType)
    formData.append('budget_range', projectForm.value.budgetRange)
    
    console.log('Making API call...')
    
    const response = await api.post('/api/v1/agents/project/analyze', formData)
    
    console.log('Response:', response)
    
    if (response.data && response.data.success) {
      analysisResult.value = response.data.data
      console.log('Analysis completed successfully!')
    } else {
      throw new Error('Analysis failed')
    }
    
  } catch (error: any) {
    console.error('Analysis error:', error)
    console.error('Error response:', error.response)
    
    if (error.response?.data?.detail) {
      console.error('API Error:', error.response.data.detail)
    } else if (error.response?.status === 422) {
      console.error('422 Error: Invalid request')
    } else {
      console.error('Error:', error.message || 'Analysis failed')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.project-analysis {
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-title {
  font-size: 32px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 10px 0;
}

.page-subtitle {
  font-size: 16px;
  color: #909399;
  margin: 0;
}

.upload-card {
  margin-bottom: 20px;
}

.form-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.analyze-button {
  width: 100%;
  margin-top: 20px;
}

.result-card {
  margin-bottom: 20px;
}

.result-content {
  max-height: 600px;
  overflow-y: auto;
}

.result-content pre {
  font-size: 12px;
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
}
</style>