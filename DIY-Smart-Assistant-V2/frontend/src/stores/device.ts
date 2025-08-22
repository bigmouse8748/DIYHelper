import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useDeviceStore = defineStore('device', () => {
  // State
  const screenWidth = ref(window.innerWidth)
  const screenHeight = ref(window.innerHeight)
  const isMobileUserAgent = ref(false)
  
  // Check user agent for mobile devices
  const checkUserAgent = () => {
    const userAgent = navigator.userAgent.toLowerCase()
    const mobileRegex = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/
    isMobileUserAgent.value = mobileRegex.test(userAgent)
  }
  
  // Update screen dimensions
  const updateScreenSize = () => {
    screenWidth.value = window.innerWidth
    screenHeight.value = window.innerHeight
  }
  
  // Computed properties
  const isMobile = computed(() => {
    // Consider it mobile if screen width < 768px OR user agent is mobile
    return screenWidth.value < 768 || isMobileUserAgent.value
  })
  
  const isTablet = computed(() => {
    return screenWidth.value >= 768 && screenWidth.value < 1024
  })
  
  const isDesktop = computed(() => {
    return screenWidth.value >= 1024 && !isMobileUserAgent.value
  })
  
  const deviceType = computed(() => {
    if (isMobile.value) return 'mobile'
    if (isTablet.value) return 'tablet'
    return 'desktop'
  })
  
  // Initialize
  const initialize = () => {
    checkUserAgent()
    updateScreenSize()
    
    // Listen for resize events
    window.addEventListener('resize', updateScreenSize)
  }
  
  // Cleanup
  const cleanup = () => {
    window.removeEventListener('resize', updateScreenSize)
  }
  
  return {
    // State
    screenWidth,
    screenHeight,
    
    // Computed
    isMobile,
    isTablet,
    isDesktop,
    deviceType,
    
    // Actions
    initialize,
    cleanup,
    updateScreenSize
  }
})