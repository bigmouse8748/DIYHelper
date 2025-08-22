import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

// Element Plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'

const app = createApp(App)

// Register Element Plus icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  // Skip any key that starts with a number or contains invalid characters
  if (/^[a-zA-Z][\w-]*$/.test(key)) {
    app.component(key, component)
  } else {
    console.warn(`Skipping invalid component name: ${key}`)
  }
}

const pinia = createPinia()
app.use(pinia)
app.use(router)
app.use(ElementPlus)

app.mount('#app')
