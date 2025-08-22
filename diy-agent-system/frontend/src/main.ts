import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import router from './router'
import App from './App.vue'
import i18n from './i18n'
import './styles/main.css'

// Initialize AWS Amplify
import { Amplify } from 'aws-amplify'
import { awsConfig } from './aws-config'

// Configure Amplify for Cognito
Amplify.configure(awsConfig)

console.log('🚀 Starting DIY Assistant App...')

const app = createApp(App)
const pinia = createPinia()

// Register all Element Plus icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(pinia)
app.use(router)
app.use(ElementPlus)
app.use(i18n)

console.log('✅ App mounted successfully')
app.mount('#app')