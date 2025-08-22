<template>
  <div class="project-analysis">
    <h1>Project Analysis - Ultra Simple</h1>
    
    <!-- Simple Upload -->
    <div class="upload-section">
      <input 
        type="file" 
        multiple 
        accept="image/*" 
        @change="handleFileSelect"
        ref="fileInput"
      >
      <br><br>
      
      <div v-if="selectedFiles.length > 0">
        <p>Selected {{ selectedFiles.length }} files</p>
      </div>
      
      <div v-if="error" style="color: red; margin: 10px 0;">
        Error: {{ error }}
      </div>
    </div>
    
    <!-- Simple Project Details -->
    <div class="project-form">
      <label>Description:</label><br>
      <textarea v-model="description" style="width: 100%; height: 60px;"></textarea><br><br>
      
      <label>Project Type:</label><br>
      <select v-model="projectType" style="width: 200px;">
        <option value="general">General</option>
        <option value="woodworking">Woodworking</option>
        <option value="electronics">Electronics</option>
      </select><br><br>
      
      <label>Budget Range:</label><br>
      <select v-model="budgetRange" style="width: 200px;">
        <option value="under50">Under $50</option>
        <option value="50to150">$50-150</option>
        <option value="150to300">$150-300</option>
      </select><br><br>
    </div>
    
    <!-- Analyze Button -->
    <button 
      @click="analyzeProject" 
      style="padding: 12px 24px; background: #409EFF; color: white; border: none; border-radius: 4px; cursor: pointer;"
    >
      {{ loading ? 'Analyzing...' : 'Analyze Project' }}
    </button>
    
    <!-- Simple Progress -->
    <div v-if="loading" style="margin: 20px 0;">
      <p>{{ status }}</p>
      <p>Progress: {{ progress }}%</p>
    </div>
    
    <!-- Simple Results -->
    <div v-if="result" style="margin: 20px 0; padding: 20px; background: #f9f9f9;">
      <h2>Analysis Results</h2>
      <div style="white-space: pre-wrap; font-family: monospace; font-size: 12px;">{{ JSON.stringify(result, null, 2) }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import api, { AGENT_ENDPOINTS } from '@/utils/api'

const fileInput = ref<HTMLInputElement>()
const selectedFiles = ref<File[]>([])
const description = ref('')
const projectType = ref('general')
const budgetRange = ref('50to150')
const loading = ref(false)
const progress = ref(0)
const status = ref('')
const result = ref(null)
const error = ref('')

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files) {
    selectedFiles.value = Array.from(target.files)
    error.value = ''
    console.log('Files selected:', selectedFiles.value.length)
  }
}

const analyzeProject = async () => {
  if (selectedFiles.value.length === 0) {
    error.value = 'Please select at least one image'
    return
  }
  
  loading.value = true
  progress.value = 0
  status.value = 'Starting analysis...'
  error.value = ''
  result.value = null
  
  try {
    console.log('=== STARTING PROJECT ANALYSIS ===')
    console.log('Number of files:', selectedFiles.value.length)
    console.log('Description:', description.value)
    console.log('Project type:', projectType.value)
    console.log('Budget range:', budgetRange.value)
    
    const formData = new FormData()
    
    // Add files one by one
    for (let i = 0; i < selectedFiles.value.length; i++) {
      const file = selectedFiles.value[i]
      formData.append('images', file)
      console.log(`Added file ${i}: ${file.name} (${file.size} bytes, ${file.type})`)
    }
    
    // Add project details
    formData.append('description', description.value || '')
    formData.append('project_type', projectType.value)
    formData.append('budget_range', budgetRange.value)
    
    console.log('=== MAKING API CALL ===')
    console.log('Endpoint:', AGENT_ENDPOINTS.PROJECT_ANALYSIS)
    
    progress.value = 25
    status.value = 'Uploading to server...'
    
    const response = await api.post(AGENT_ENDPOINTS.PROJECT_ANALYSIS, formData)
    
    console.log('=== API RESPONSE ===')
    console.log('Response status:', response.status)
    console.log('Response data:', response.data)
    
    progress.value = 75
    status.value = 'Processing response...'
    
    if (response.data && response.data.success) {
      result.value = response.data.data
      status.value = 'Analysis complete!'
      progress.value = 100
      console.log('=== SUCCESS ===')
    } else {
      throw new Error('API returned success: false')
    }
    
  } catch (err: any) {
    console.log('=== ERROR OCCURRED ===')
    console.error('Full error object:', err)
    console.error('Error message:', err.message)
    console.error('Error response:', err.response)
    console.error('Error response status:', err.response?.status)
    console.error('Error response data:', err.response?.data)
    console.error('Error code:', err.code)
    
    if (err.response?.data?.detail) {
      error.value = `API Error: ${err.response.data.detail}`
    } else if (err.response?.status) {
      error.value = `HTTP ${err.response.status}: ${err.message}`
    } else {
      error.value = `Error: ${err.message}`
    }
    
    status.value = 'Analysis failed'
    progress.value = 0
    
  } finally {
    loading.value = false
    console.log('=== ANALYSIS COMPLETE ===')
  }
}
</script>

<style scoped>
.project-analysis {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

.upload-section {
  margin: 20px 0;
  padding: 20px;
  border: 2px dashed #ccc;
  border-radius: 8px;
}

.project-form {
  margin: 20px 0;
}

.project-form label {
  font-weight: bold;
}
</style>