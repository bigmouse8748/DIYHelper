<template>
  <div class="analysis-page">
    <h1>Project Analysis - Working Version</h1>
    
    <!-- File Upload Section -->
    <div class="upload-section">
      <h3>Upload Project Images</h3>
      <input 
        type="file" 
        @change="handleFile" 
        multiple 
        accept="image/*"
        ref="fileInput"
      >
      <div v-if="selectedFiles.length > 0" class="file-list">
        <p><strong>Selected {{ selectedFiles.length }} files:</strong></p>
        <ul>
          <li v-for="(file, index) in selectedFiles" :key="`file-${index}`">
            {{ file.name }} ({{ Math.round(file.size / 1024) }}KB)
          </li>
        </ul>
      </div>
    </div>
    
    <!-- Project Details -->
    <div class="project-details">
      <h3>Project Details</h3>
      <div class="form-group">
        <label>Description (optional):</label>
        <textarea 
          v-model="description" 
          placeholder="Describe your project..."
          rows="3"
        ></textarea>
      </div>
      
      <div class="form-group">
        <label>Project Type:</label>
        <select v-model="projectType">
          <option value="general">General</option>
          <option value="woodworking">Woodworking</option>
          <option value="electronics">Electronics</option>
          <option value="metalworking">Metalworking</option>
          <option value="crafts">Crafts</option>
        </select>
      </div>
      
      <div class="form-group">
        <label>Budget Range:</label>
        <select v-model="budgetRange">
          <option value="under50">Under $50</option>
          <option value="50to150">$50-150</option>
          <option value="150to300">$150-300</option>
          <option value="300plus">$300+</option>
        </select>
      </div>
    </div>
    
    <!-- Action Buttons -->
    <div class="actions">
      <button 
        @click="analyzeProject" 
        :disabled="selectedFiles.length === 0 || isLoading"
        class="analyze-btn"
      >
        {{ isLoading ? 'Analyzing...' : 'Analyze Project' }}
      </button>
      
      <button @click="reset" class="reset-btn">Reset</button>
    </div>
    
    <!-- Loading State -->
    <div v-if="isLoading" class="loading">
      <p>{{ status }}</p>
      <div class="progress-bar">
        <div class="progress" :style="{ width: progress + '%' }"></div>
      </div>
      <p>{{ progress }}% complete</p>
    </div>
    
    <!-- Error Message -->
    <div v-if="error" class="error">
      <h3>Error:</h3>
      <p>{{ error }}</p>
    </div>
    
    <!-- Results -->
    <div v-if="result" class="results">
      <h2>Analysis Results</h2>
      
      <!-- Project Overview -->
      <div v-if="result.comprehensive_analysis" class="result-section">
        <h3>Project Overview</h3>
        <p><strong>Project:</strong> {{ result.comprehensive_analysis.project_name }}</p>
        <p><strong>Description:</strong> {{ result.comprehensive_analysis.description }}</p>
        <p><strong>Difficulty:</strong> {{ result.comprehensive_analysis.difficulty_level }}</p>
        <p><strong>Estimated Time:</strong> {{ result.comprehensive_analysis.estimated_time }}</p>
      </div>
      
      <!-- Materials -->
      <div v-if="result.comprehensive_analysis?.materials" class="result-section">
        <h3>Materials Needed</h3>
        <div class="materials-grid">
          <div v-for="(material, index) in result.comprehensive_analysis.materials" :key="`material-${index}`" class="material-card">
            <h4>{{ material.name }}</h4>
            <p><strong>Specification:</strong> {{ material.specification }}</p>
            <p><strong>Quantity:</strong> {{ material.quantity }}</p>
            <p><strong>Price Range:</strong> {{ material.estimated_price_range }}</p>
          </div>
        </div>
      </div>
      
      <!-- Tools -->
      <div v-if="result.comprehensive_analysis?.tools" class="result-section">
        <h3>Tools Required</h3>
        <div class="tools-grid">
          <div v-for="(tool, index) in result.comprehensive_analysis.tools" :key="`tool-${index}`" class="tool-card">
            <h4>{{ tool.name }}</h4>
            <span class="necessity" :class="tool.necessity?.toLowerCase()">{{ tool.necessity }}</span>
          </div>
        </div>
      </div>
      
      <!-- Safety Notes -->
      <div v-if="result.comprehensive_analysis?.safety_notes" class="result-section">
        <h3>Safety Notes</h3>
        <ul class="safety-list">
          <li v-for="(note, index) in result.comprehensive_analysis.safety_notes" :key="`safety-${index}`">
            {{ note }}
          </li>
        </ul>
      </div>
      
      <!-- Steps -->
      <div v-if="result.comprehensive_analysis?.steps" class="result-section">
        <h3>Step-by-Step Instructions</h3>
        <ol class="steps-list">
          <li v-for="(step, index) in result.comprehensive_analysis.steps" :key="`step-${index}`">
            {{ step }}
          </li>
        </ol>
      </div>
      
      <!-- Product Recommendations -->
      <div v-if="result.product_recommendations" class="result-section">
        <h3>Product Recommendations</h3>
        <p>Total products assessed: {{ result.product_recommendations.overall_recommendations?.total_products_assessed }}</p>
        <p>Average quality score: {{ result.product_recommendations.overall_recommendations?.average_quality_score?.toFixed(1) }}</p>
        
        <!-- Shopping Tips -->
        <div v-if="result.product_recommendations.overall_recommendations?.shopping_tips" class="shopping-tips">
          <h4>Shopping Tips:</h4>
          <ul>
            <li v-for="(tip, index) in result.product_recommendations.overall_recommendations.shopping_tips" :key="`tip-${index}`">
              {{ tip }}
            </li>
          </ul>
        </div>
      </div>
      
      <!-- Raw JSON (for debugging) -->
      <details class="raw-data">
        <summary>Raw API Response (Click to expand)</summary>
        <pre>{{ JSON.stringify(result, null, 2) }}</pre>
      </details>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import api, { AGENT_ENDPOINTS } from '@/utils/api'

const selectedFiles = ref<File[]>([])
const description = ref('')
const projectType = ref('general')
const budgetRange = ref('50to150')
const isLoading = ref(false)
const progress = ref(0)
const status = ref('')
const result = ref(null)
const error = ref('')

const handleFile = (event: any) => {
  const files = event.target.files
  selectedFiles.value = Array.from(files)
  error.value = ''
  console.log('Files selected:', selectedFiles.value.length)
}

const reset = () => {
  selectedFiles.value = []
  description.value = ''
  projectType.value = 'general'
  budgetRange.value = '50to150'
  isLoading.value = false
  progress.value = 0
  status.value = ''
  result.value = null
  error.value = ''
}

const analyzeProject = async () => {
  if (selectedFiles.value.length === 0) {
    error.value = 'Please select at least one image'
    return
  }
  
  isLoading.value = true
  progress.value = 0
  status.value = 'Preparing images...'
  error.value = ''
  result.value = null
  
  try {
    console.log('=== STARTING PROJECT ANALYSIS ===')
    console.log('Files:', selectedFiles.value.length)
    console.log('Description:', description.value)
    console.log('Project type:', projectType.value)
    console.log('Budget range:', budgetRange.value)
    
    const formData = new FormData()
    
    // Add files
    for (let i = 0; i < selectedFiles.value.length; i++) {
      const file = selectedFiles.value[i]
      formData.append('images', file)
      console.log(`Added file ${i}: ${file.name} (${file.size} bytes, ${file.type})`)
    }
    
    // Add project details
    formData.append('description', description.value || '')
    formData.append('project_type', projectType.value)
    formData.append('budget_range', budgetRange.value)
    
    progress.value = 25
    status.value = 'Uploading to AI analysis service...'
    
    console.log('Making API call to:', AGENT_ENDPOINTS.PROJECT_ANALYSIS)
    
    const response = await api.post(AGENT_ENDPOINTS.PROJECT_ANALYSIS, formData)
    
    progress.value = 75
    status.value = 'Processing results...'
    
    console.log('API Response:', response)
    
    if (response.data && response.data.success) {
      result.value = response.data.data
      status.value = 'Analysis complete!'
      progress.value = 100
      console.log('Analysis successful:', result.value)
    } else {
      throw new Error('API returned success: false')
    }
    
  } catch (err: any) {
    console.error('Analysis error:', err)
    console.error('Error response:', err.response)
    console.error('Error status:', err.response?.status)
    console.error('Error data:', err.response?.data)
    
    if (err.response?.data?.detail) {
      error.value = `API Error: ${err.response.data.detail}`
    } else if (err.response?.status) {
      error.value = `HTTP ${err.response.status}: ${err.message}`
    } else {
      error.value = `Error: ${err.message}`
    }
    
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.analysis-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.upload-section, .project-details {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.file-list {
  margin-top: 15px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 6px;
}

.file-list ul {
  margin: 10px 0 0 0;
  padding-left: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
  color: #333;
}

.form-group textarea, .form-group select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.actions {
  display: flex;
  gap: 10px;
  margin: 20px 0;
}

.analyze-btn {
  background: #409EFF;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
}

.analyze-btn:disabled {
  background: #c0c4cc;
  cursor: not-allowed;
}

.reset-btn {
  background: #f56c6c;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
}

.loading {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin: 20px 0;
  text-align: center;
}

.progress-bar {
  width: 100%;
  height: 20px;
  background: #f0f0f0;
  border-radius: 10px;
  overflow: hidden;
  margin: 15px 0;
}

.progress {
  height: 100%;
  background: linear-gradient(90deg, #409EFF, #67C23A);
  transition: width 0.3s ease;
}

.error {
  background: #fef0f0;
  border: 1px solid #fbc4c4;
  color: #f56565;
  padding: 20px;
  border-radius: 8px;
  margin: 20px 0;
}

.results {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin: 20px 0;
}

.result-section {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.result-section:last-child {
  border-bottom: none;
}

.materials-grid, .tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.material-card, .tool-card {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 6px;
  border-left: 4px solid #409EFF;
}

.material-card h4, .tool-card h4 {
  margin: 0 0 10px 0;
  color: #333;
}

.necessity {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.necessity.essential {
  background: #f56c6c;
  color: white;
}

.necessity.recommended {
  background: #e6a23c;
  color: white;
}

.necessity.optional {
  background: #909399;
  color: white;
}

.safety-list, .steps-list {
  margin-top: 15px;
}

.safety-list li {
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  padding: 10px;
  margin-bottom: 8px;
  border-radius: 4px;
  list-style: none;
  position: relative;
  padding-left: 30px;
}

.safety-list li::before {
  content: "⚠️";
  position: absolute;
  left: 8px;
  top: 10px;
}

.steps-list li {
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

.shopping-tips {
  background: #f0f9ff;
  padding: 15px;
  border-radius: 6px;
  margin-top: 15px;
}

.raw-data {
  margin-top: 30px;
  border-top: 2px solid #eee;
  padding-top: 20px;
}

.raw-data summary {
  cursor: pointer;
  font-weight: 600;
  color: #666;
}

.raw-data pre {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 12px;
  margin-top: 10px;
}
</style>