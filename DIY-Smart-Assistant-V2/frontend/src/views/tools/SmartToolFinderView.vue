<template>
  <div class="smart-tool-finder">
    <div class="finder-container">
      <!-- Sidebar -->
      <aside class="sidebar">
        <h3 class="sidebar-title">Filter Options</h3>
        
        <div class="filter-group">
          <label class="filter-label">Price Range</label>
          <el-select v-model="filters.priceRange" placeholder="Any Price" @change="updateFilters">
            <el-option label="Any Price" value=""></el-option>
            <el-option label="Under $50" value="under_50"></el-option>
            <el-option label="$50 - $150" value="50_150"></el-option>
            <el-option label="$150 - $500" value="150_500"></el-option>
            <el-option label="Over $500" value="over_500"></el-option>
          </el-select>
        </div>

        <div class="filter-group">
          <label class="filter-label">Difficulty Level</label>
          <el-select v-model="filters.difficulty" placeholder="Any Level" @change="updateFilters">
            <el-option label="Any Level" value=""></el-option>
            <el-option label="Beginner" value="beginner"></el-option>
            <el-option label="Intermediate" value="intermediate"></el-option>
            <el-option label="Professional" value="professional"></el-option>
          </el-select>
        </div>

        <div class="filter-group">
          <label class="filter-label">Power Type</label>
          <el-select v-model="filters.powerType" placeholder="Any Type" @change="updateFilters">
            <el-option label="Any Type" value=""></el-option>
            <el-option label="Electric" value="electric"></el-option>
            <el-option label="Manual" value="manual"></el-option>
            <el-option label="Pneumatic" value="pneumatic"></el-option>
          </el-select>
        </div>

        <div class="filter-group">
          <label class="filter-label">Quick Start</label>
          <div class="suggestion-chips">
            <div 
              v-for="suggestion in quickSuggestions" 
              :key="suggestion.id"
              class="suggestion-chip" 
              @click="sendQuickMessage(suggestion.text)"
            >
              {{ suggestion.label }}
            </div>
          </div>
        </div>
      </aside>

      <!-- Chat Container -->
      <main class="chat-container">
        <div class="chat-header">
          <h2 class="chat-title">Smart Tool Finder</h2>
          <p class="chat-subtitle">Tell me what you want to accomplish, and I'll find the perfect tools for you!</p>
        </div>

        <div class="chat-messages" ref="chatMessages">
          <div 
            v-for="message in messages" 
            :key="message.id"
            :class="['message', message.type]"
          >
            <div class="message-avatar">
              {{ message.type === 'user' ? '👤' : '🤖' }}
            </div>
            <div class="message-content">
              <div class="message-text">{{ message.text }}</div>
              
              <!-- Tool recommendations -->
              <div v-if="message.tools && message.tools.length > 0" class="tool-recommendations">
                <div 
                  v-for="tool in message.tools" 
                  :key="tool.id"
                  class="tool-card"
                >
                  <div class="tool-header">
                    <div class="tool-name">{{ tool.name }}</div>
                    <div class="tool-price">{{ tool.price_range || tool.estimated_price || 'Price varies' }}</div>
                  </div>
                  <div class="tool-description">{{ tool.description }}</div>
                  <div class="tool-specs">
                    <span class="tool-spec">{{ tool.difficulty || 'Any level' }}</span>
                    <span class="tool-spec">{{ tool.power_type || 'Any type' }}</span>
                  </div>
                  <div class="tool-reason">
                    💡 {{ tool.reason }}
                  </div>
                  <div class="shopping-links">
                    <el-button 
                      v-for="link in (tool.shopping_links || []).slice(0, 3)" 
                      :key="link.retailer"
                      size="small"
                      type="primary"
                      @click="openLink(link.url)"
                    >
                      {{ link.retailer }}
                    </el-button>
                  </div>
                </div>
              </div>
              
              <!-- Suggestions -->
              <div v-if="message.suggestions && message.suggestions.length > 0" class="suggestions">
                <el-button 
                  v-for="suggestion in message.suggestions" 
                  :key="suggestion"
                  size="small"
                  round
                  @click="sendQuickMessage(suggestion)"
                >
                  {{ suggestion }}
                </el-button>
              </div>
            </div>
          </div>
          
          <!-- Loading message -->
          <div v-if="loading" class="message assistant">
            <div class="message-avatar">🤖</div>
            <div class="message-content">
              <div class="loading">
                <el-icon class="is-loading"><Loading /></el-icon>
                <span>Searching for tools...</span>
              </div>
            </div>
          </div>
        </div>

        <div class="chat-input-container">
          <div class="chat-input-wrapper">
            <el-input
              v-model="inputMessage"
              type="textarea"
              placeholder="Type your message here..."
              :rows="1"
              :autosize="{ minRows: 1, maxRows: 4 }"
              @keydown="handleKeyPress"
              :disabled="loading"
            />
            <el-button 
              type="primary" 
              :loading="loading"
              @click="sendMessage"
              :disabled="!inputMessage.trim()"
            >
              Send
            </el-button>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// State
const messages = ref<any[]>([])
const inputMessage = ref('')
const loading = ref(false)
const chatMessages = ref<HTMLElement>()
const filters = ref({
  priceRange: '',
  difficulty: '',
  powerType: ''
})

const quickSuggestions = [
  { id: 1, label: 'Join Wood', text: 'I need tools to join wood pieces together' },
  { id: 2, label: 'Cut Lumber', text: 'What tools do I need to cut lumber?' },
  { id: 3, label: 'Drill Holes', text: 'Help me find tools for drilling holes' },
  { id: 4, label: 'Sand Surfaces', text: 'Show me tools for sanding surfaces' },
  { id: 5, label: 'Budget Tools', text: 'I need budget-friendly tools for my project' }
]

let messageId = 0

// Methods
const updateFilters = () => {
  // Filters updated, could trigger re-analysis of current recommendations
  console.log('Filters updated:', filters.value)
}

const sendQuickMessage = (message: string) => {
  inputMessage.value = message
  sendMessage()
}

const sendMessage = async () => {
  const message = inputMessage.value.trim()
  if (!message || loading.value) return

  // Add user message
  messages.value.push({
    id: ++messageId,
    type: 'user',
    text: message,
    timestamp: new Date()
  })

  inputMessage.value = ''
  loading.value = true
  
  await scrollToBottom()

  try {
    const response = await fetch('http://localhost:8000/api/v1/agents/smart-tool-finder/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.accessToken}`
      },
      body: JSON.stringify({
        query: message,
        filters: filters.value,
        conversation_history: messages.value.slice(-10) // Last 10 messages for context
      })
    })

    if (!response.ok) {
      throw new Error('Failed to get response')
    }

    const result = await response.json()
    
    if (result.success) {
      const data = result.data
      messages.value.push({
        id: ++messageId,
        type: 'assistant',
        text: data.message,
        tools: data.tools || [],
        suggestions: data.suggestions || [],
        timestamp: new Date()
      })
    } else {
      throw new Error(result.message || 'Failed to process request')
    }

  } catch (error) {
    console.error('Error sending message:', error)
    messages.value.push({
      id: ++messageId,
      type: 'assistant',
      text: 'Sorry, I couldn\'t process your request. Please try again.',
      timestamp: new Date()
    })
    ElMessage.error('Connection error. Please check if the backend is running and try again.')
  } finally {
    loading.value = false
    await scrollToBottom()
  }
}

const handleKeyPress = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

const openLink = (url: string) => {
  window.open(url, '_blank', 'noopener,noreferrer')
}

const scrollToBottom = async () => {
  await nextTick()
  if (chatMessages.value) {
    chatMessages.value.scrollTop = chatMessages.value.scrollHeight
  }
}

// Initialize
onMounted(() => {
  // Add welcome message
  messages.value.push({
    id: ++messageId,
    type: 'assistant',
    text: 'Welcome to Smart Tool Finder! I\'m here to help you find the perfect tools for your DIY projects.',
    suggestions: [
      'I need tools to join wood pieces together',
      'What tools do I need to cut lumber?', 
      'Help me find tools for drilling holes',
      'Show me tools for sanding surfaces'
    ],
    timestamp: new Date()
  })
})
</script>

<style scoped>
.smart-tool-finder {
  min-height: calc(100vh - 60px);
  background: #f5f7fa;
}

.finder-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 40px 20px;
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 30px;
}

/* Sidebar */
.sidebar {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  height: fit-content;
  position: sticky;
  top: 120px;
}

.sidebar-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 20px;
}

.filter-group {
  margin-bottom: 24px;
}

.filter-label {
  display: block;
  font-weight: 500;
  color: #606266;
  margin-bottom: 8px;
  font-size: 14px;
}

.suggestion-chips {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.suggestion-chip {
  padding: 8px 12px;
  background: #f8f9ff;
  border: 1px solid #e1e6ff;
  border-radius: 6px;
  color: #667eea;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.3s ease;
  text-align: center;
}

.suggestion-chip:hover {
  background: #667eea;
  color: white;
}

/* Chat Container */
.chat-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  height: 700px;
}

.chat-header {
  padding: 24px;
  border-bottom: 1px solid #e4e7ed;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px 12px 0 0;
}

.chat-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
}

.chat-subtitle {
  font-size: 16px;
  opacity: 0.9;
}

.chat-messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
}

.message.user .message-avatar {
  background: #667eea;
  color: white;
}

.message.assistant .message-avatar {
  background: #f0f2ff;
  color: #667eea;
}

.message-content {
  max-width: 70%;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message-text {
  padding: 12px 16px;
  border-radius: 12px;
  word-wrap: break-word;
}

.message.user .message-text {
  background: #667eea;
  color: white;
}

.message.assistant .message-text {
  background: #f8f9ff;
  color: #303133;
}

.tool-recommendations {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.tool-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  background: white;
  transition: all 0.3s ease;
}

.tool-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.tool-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.tool-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.tool-price {
  color: #667eea;
  font-weight: 600;
}

.tool-description {
  color: #606266;
  margin-bottom: 12px;
  font-size: 14px;
}

.tool-specs {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.tool-spec {
  padding: 4px 8px;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 12px;
  color: #606266;
}

.tool-reason {
  background: #f0f9ff;
  padding: 8px 12px;
  border-radius: 6px;
  border-left: 3px solid #667eea;
  font-size: 13px;
  color: #1e40af;
  margin-bottom: 12px;
}

.shopping-links {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.suggestions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.loading {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #909399;
  font-style: italic;
}

.chat-input-container {
  padding: 20px;
  border-top: 1px solid #e4e7ed;
}

.chat-input-wrapper {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

/* Responsive */
@media (max-width: 1024px) {
  .finder-container {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .sidebar {
    position: static;
    order: 2;
  }
  
  .chat-container {
    order: 1;
  }
}

@media (max-width: 768px) {
  .finder-container {
    padding: 20px 16px;
  }
  
  .chat-container {
    height: 600px;
  }
  
  .tool-card {
    padding: 12px;
  }
  
  .message-content {
    max-width: 85%;
  }
}
</style>