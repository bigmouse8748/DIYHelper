<template>
  <div class="project-analysis">
    <h1>Project Analysis</h1>
    
    <!-- Simple Upload -->
    <div class="upload-section">
      <input 
        type="file" 
        multiple 
        accept="image/*" 
        @change="handleFileSelect"
        ref="fileInput"
      >
      <button @click="triggerFileSelect">Choose Images</button>
      
      <div v-if="selectedFiles.length > 0">
        <p>Selected files: {{ selectedFiles.length }}</p>
        <ul>
          <li v-for="(file, index) in selectedFiles" :key="`file-${index}`">
            {{ file.name }} ({{ Math.round(file.size / 1024) }}KB)
          </li>
        </ul>
      </div>
    </div>
    
    <!-- Project Details -->
    <div class="project-form">
      <label>Description:</label>
      <textarea v-model="description" placeholder="Describe your project (optional)"></textarea>
      
      <label>Project Type:</label>
      <select v-model="projectType">
        <option value="general">General</option>
        <option value="woodworking">Woodworking</option>
        <option value="electronics">Electronics</option>
        <option value="metalworking">Metalworking</option>
      </select>
      
      <label>Budget Range:</label>
      <select v-model="budgetRange">
        <option value="under50">Under $50</option>
        <option value="50to150">$50-150</option>
        <option value="150to300">$150-300</option>
        <option value="300plus">$300+</option>
      </select>
    </div>
    
    <!-- Analyze Button -->
    <button 
      @click="analyzeProject" 
      :disabled="selectedFiles.length === 0 || loading"
      class="analyze-btn"
    >
      {{ loading ? 'Analyzing...' : 'Analyze Project' }}
    </button>
    
    <!-- Progress -->
    <div v-if="loading" class="progress">
      <p>{{ status }}</p>
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: `${progress}%` }"></div>
      </div>
    </div>
    
    <!-- Results -->
    <div v-if="result" class="results">
      <h2>Analysis Results</h2>
      <pre>{{ JSON.stringify(result, null, 2) }}</pre>
    </div>
    
    <!-- Error -->
    <div v-if="error" class="error">
      <h3>Error:</h3>
      <p>{{ error }}</p>
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

const triggerFileSelect = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files) {
    selectedFiles.value = Array.from(target.files)
    error.value = ''
  }
}

const analyzeProject = async () => {
  if (selectedFiles.value.length === 0) {
    error.value = 'Please select at least one image'
    return
  }
  
  loading.value = true
  progress.value = 0
  status.value = 'Preparing images...'
  error.value = ''
  result.value = null
  
  try {
    console.log('Starting analysis with files:', selectedFiles.value.length)
    
    const formData = new FormData()
    
    // Add files
    selectedFiles.value.forEach((file, index) => {
      formData.append('images', file)
      console.log(`Added file ${index}: ${file.name}`)
    })
    
    // Add project details
    formData.append('description', description.value || '')
    formData.append('project_type', projectType.value)
    formData.append('budget_range', budgetRange.value)
    
    console.log('Making API call...')
    progress.value = 50
    status.value = 'Analyzing with AI...'
    
    const response = await api.post(AGENT_ENDPOINTS.PROJECT_ANALYSIS, formData)
    
    console.log('API response:', response)
    
    if (response.data.success) {
      result.value = response.data.data
      status.value = 'Analysis complete!'
      progress.value = 100
    } else {
      throw new Error('Analysis failed')
    }
    
  } catch (err: any) {
    console.error('Analysis error:', err)
    console.error('Error response:', err.response)
    console.error('Error status:', err.response?.status)
    console.error('Error data:', err.response?.data)
    
    error.value = err.response?.data?.detail || err.message || 'Analysis failed'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.project-analysis {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
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
  display: block;
  margin: 10px 0 5px;
  font-weight: bold;
}

.project-form input, 
.project-form select, 
.project-form textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  margin-bottom: 10px;
}

.analyze-btn {
  background: #409EFF;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.analyze-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.progress {
  margin: 20px 0;
}

.progress-bar {
  width: 100%;
  height: 20px;
  background: #f0f0f0;
  border-radius: 10px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #409EFF;
  transition: width 0.3s;
}

.results {
  margin: 20px 0;
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
}

.error {
  margin: 20px 0;
  padding: 20px;
  background: #fef0f0;
  border: 1px solid #fcd6d6;
  border-radius: 8px;
  color: #f56565;
}
</style>