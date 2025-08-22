<template>
  <div id="app">
    <router-view />
    <DebugInfo />
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useDeviceStore } from '@/stores/device'
import DebugInfo from '@/components/DebugInfo.vue'

const authStore = useAuthStore()
const deviceStore = useDeviceStore()

// Initialize auth state and device detection when app starts
onMounted(async () => {
  await authStore.initialize()
  deviceStore.initialize()
})

// Clean up device store event listener
onUnmounted(() => {
  deviceStore.cleanup()
})
</script>

<style>
/* Global styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  width: 100%;
  overflow-x: hidden;
}

#app {
  min-height: 100vh;
  width: 100%;
}

/* Ensure proper desktop layout */
@media (min-width: 769px) {
  body {
    min-width: 1024px;
  }
  
  #app {
    min-width: 1024px;
  }
}

/* Ensure mobile layouts are constrained properly */
@media (max-width: 768px) {
  body {
    min-width: 320px;
    max-width: 100vw;
  }
  
  #app {
    min-width: 320px;
    max-width: 100vw;
  }
}

/* Element Plus customization */
:root {
  --el-color-primary: #667eea;
  --el-color-primary-light-3: rgba(102, 126, 234, 0.7);
  --el-color-primary-light-5: rgba(102, 126, 234, 0.5);
  --el-color-primary-light-7: rgba(102, 126, 234, 0.3);
  --el-color-primary-light-9: rgba(102, 126, 234, 0.1);
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Animation classes */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.3s cubic-bezier(1.0, 0.5, 0.8, 1.0);
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateX(20px);
  opacity: 0;
}
</style>
