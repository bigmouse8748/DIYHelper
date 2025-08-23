<template>
  <div style="padding: 20px;">
    <h1>Pure HTML Analysis - No Vue Components</h1>
    
    <div style="margin: 20px 0;">
      <input 
        type="file" 
        id="fileInput"
        multiple 
        accept="image/*"
        @change="handleFileChange"
      >
    </div>
    
    <div style="margin: 20px 0;">
      <button @click="analyze" style="padding: 10px 20px;">Analyze</button>
    </div>
    
    <div v-if="message" style="margin: 20px 0; padding: 10px; background: #f0f0f0;">
      {{ message }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import api from '@/utils/api'

const message = ref('')
let files: File[] = []

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files) {
    files = Array.from(target.files)
    message.value = `Selected ${files.length} files`
  }
}

const analyze = async () => {
  if (files.length === 0) {
    message.value = 'Please select files first'
    return
  }
  
  message.value = 'Analyzing...'
  
  try {
    const formData = new FormData()
    
    files.forEach(file => {
      formData.append('images', file)
    })
    
    formData.append('description', '')
    formData.append('project_type', 'general')
    formData.append('budget_range', 'medium')
    
    const response = await api.post('/api/v1/agents/project/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    const data = response.data
    
    message.value = 'Analysis successful! Check console for results.'
    console.log('Results:', data)
    
  } catch (error) {
    message.value = `Error: ${error}`
    console.error('Error:', error)
  }
}
</script>