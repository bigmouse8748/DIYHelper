export default {
  // Navigation
  nav: {
    home: 'Home',
    diyAssistant: 'DIY Assistant',
    toolIdentification: 'Tool ID',
    projects: 'My Projects',
    about: 'About',
    dashboard: 'Dashboard',
    logo: 'DIY Smart Assistant'
  },
  
  // Home Page
  home: {
    hero: {
      title: 'DIY Smart Assistant',
      subtitle: 'AI-powered project analysis and tool identification platform for DIY enthusiasts',
      getStarted: 'Get Started',
      startProject: 'Start New Project'
    },
    
    features: {
      title: 'Our Features',
      tryNow: 'Try Now',
      loginRequired: 'Login Required',
      
      diyAssistant: {
        title: 'DIY Smart Assistant',
        description: 'Upload images and get AI-powered analysis of your DIY projects with smart tool and material recommendations',
        benefits: [
          'AI-powered project analysis',
          'Smart material recommendations',
          'Real-time product pricing',
          'Step-by-step guidance'
        ]
      },
      
      toolIdentification: {
        title: 'Tool Identification',
        description: 'Identify tools from photos and get detailed specifications, pricing, and purchasing options',
        benefits: [
          'Instant tool recognition',
          'Detailed specifications',
          'Price comparison',
          'Shopping recommendations'
        ]
      }
    },
    
    examples: {
      title: 'See It In Action',
      
      diy: {
        title: 'DIY Project Analysis',
        description: 'Upload a photo of your woodworking project and get comprehensive guidance',
        features: ['Material List', 'Tool Recommendations', 'Safety Tips', 'Step-by-Step Guide']
      },
      
      tool: {
        title: 'Tool Identification',
        description: 'Identify any tool and get instant product information and buying options',
        features: ['Brand Recognition', 'Model Details', 'Price Comparison', 'Alternative Options']
      }
    },
    
    authPrompt: {
      title: 'Ready to get started?',
      description: 'Sign up for free to access our AI-powered DIY tools and start your next project today!',
      register: 'Sign Up Free',
      login: 'Login'
    },
    
    welcomeBack: 'Welcome back, {username}!',
    dashboardPrompt: {
      description: 'Continue working on your projects or start something new',
      dashboard: 'Go to Dashboard',
      newProject: 'New Project'
    },
    
    messages: {
      loginRequired: 'Please login to access this feature'
    },
    
    // Legacy fields for DIY Assistant page
    title: 'DIY Smart Assistant',
    subtitle: 'Upload images and get AI-powered analysis of your DIY projects with smart tool and material recommendations',
    uploadTitle: 'Upload Project Images',
    uploadTip: 'Supports JPG, PNG formats, maximum 4 images',
    projectDescription: 'Project Description',
    projectDescriptionPlaceholder: 'Describe your DIY project (optional)',
    projectType: 'Project Type',
    projectTypePlaceholder: 'Select project type (optional)',
    budgetRange: 'Budget Range',
    budgetRangePlaceholder: 'Select budget range (optional)',
    analyzeButton: 'Start Smart Analysis',
    analyzing: 'Analyzing...',
    
    // Project Types
    projectTypes: {
      woodworking: 'Woodworking',
      electronics: 'Electronics', 
      crafts: 'Arts & Crafts',
      homeDecor: 'Home Decor',
      repair: 'Repair & Maintenance',
      other: 'Other'
    },
    
    // Budget Ranges
    budgetRanges: {
      'under50': 'Under $50',
      '50to150': '$50 - $150', 
      '150to300': '$150 - $300',
      '300to500': '$300 - $500',
      'over500': 'Over $500'
    },
    
    // Loading States
    loading: {
      uploading: 'Uploading images...',
      analyzing: 'AI is analyzing your project...',
      searching: 'Searching for related products...',
      assessing: 'Assessing product quality...',
      generating: 'Generating analysis report...'
    },
    
    // Messages
    messages: {
      uploadError: 'Please select at least one image',
      imageTypeError: 'Only image files are allowed!',
      imageSizeError: 'Image size cannot exceed 10MB!',
      analysisError: 'Analysis failed, please try again',
      analysisSuccess: 'Analysis completed!',
      maxImagesWarning: 'Maximum 4 images allowed, currently selected {count} images'
    }
  },
  
  // DIY Assistant Page
  diy: {
    title: 'DIY Smart Assistant',
    subtitle: 'Upload images and get AI-powered analysis of your DIY projects with smart tool and material recommendations',
    uploadTitle: 'Upload Project Images',
    uploadTip: 'Supports JPG, PNG formats, maximum 4 images',
    projectDescription: 'Project Description',
    projectDescriptionPlaceholder: 'Describe your DIY project (optional)',
    projectType: 'Project Type',
    projectTypePlaceholder: 'Select project type (optional)',
    budgetRange: 'Budget Range',
    budgetRangePlaceholder: 'Select budget range (optional)',
    analyzeButton: 'Start Smart Analysis',
    analyzing: 'Analyzing...',
    
    // Project Types
    projectTypes: {
      woodworking: 'Woodworking',
      electronics: 'Electronics', 
      crafts: 'Arts & Crafts',
      homeDecor: 'Home Decor',
      repair: 'Repair & Maintenance',
      other: 'Other'
    },
    
    // Budget Ranges
    budgetRanges: {
      'under50': 'Under $50',
      '50to150': '$50 - $150', 
      '150to300': '$150 - $300',
      '300to500': '$300 - $500',
      'over500': 'Over $500'
    },
    
    // Loading States
    loading: {
      uploading: 'Uploading images...',
      analyzing: 'AI is analyzing your project...',
      searching: 'Searching for related products...',
      assessing: 'Assessing product quality...',
      generating: 'Generating analysis report...'
    },
    
    // Messages
    messages: {
      uploadError: 'Please select at least one image',
      imageTypeError: 'Only image files are allowed!',
      imageSizeError: 'Image size cannot exceed 10MB!',
      analysisError: 'Analysis failed, please try again',
      analysisSuccess: 'Analysis completed!',
      maxImagesWarning: 'Maximum 4 images allowed, currently selected {count} images'
    }
  },
  
  // Analysis Results
  results: {
    projectAnalysis: 'Project Analysis Results',
    toolsAndMaterials: 'Tools & Materials', 
    materialsNeeded: 'Materials Needed',
    toolsNeeded: 'Tools Needed',
    safetyNotes: 'Safety Notes',
    buildingSteps: 'Building Steps',
    smartRecommendations: 'Smart Product Recommendations',
    shoppingTips: 'Shopping Tips',
    bestRecommendations: 'Best Recommendations',
    totalTime: 'Total Time',
    agentsUsed: 'Agents Used',
    analysisInfo: 'Analysis Information',
    
    // Difficulty Levels
    difficulty: {
      label: 'Difficulty',
      simple: 'Simple',
      medium: 'Medium', 
      hard: 'Hard'
    },
    
    // Necessity Levels  
    necessity: {
      essential: 'Essential',
      recommended: 'Recommended',
      optional: 'Optional'
    },
    
    // Recommendation Levels
    recommendations: {
      'Professional Choice': 'Professional Choice',
      'Highly Recommended': 'Highly Recommended',
      'Best Value': 'Best Value', 
      'Safety Essential': 'Safety Essential',
      'Recommended': 'Recommended',
      'Good Choice': 'Good Choice'
    },
    
    // Product Actions
    viewProduct: 'View Product',
    assessmentDetails: 'Assessment Details',
    productUnavailable: 'Product link unavailable',
    
    // Empty States
    noMaterials: 'No specific materials detected',
    noTools: 'No specific tools detected', 
    noSuggestions: 'No shopping suggestions available',
    
    // Additional
    averageRating: 'Average Rating',
    productsFound: 'Found {count} products',
    totalProductsAssessed: 'Products Assessed',
    averageQualityScore: 'Average Quality Score',
    scoreUnit: 'pts',
    specification: 'Specification',
    quantity: 'Quantity',
    estimatedPrice: 'Estimated Price',
    estimatedTime: 'Estimated Time',
    stepLabel: 'Step'
  },
  
  // About Page
  about: {
    title: 'About DIY Smart Assistant',
    subtitle: 'AI Agent-based smart DIY project analysis platform',
    
    features: {
      smartAnalysis: 'Smart Image Analysis',
      smartAnalysisDesc: 'Using cutting-edge AI vision technology to intelligently identify DIY project types, required materials and tools, providing professional analysis results.',
      smartSearch: 'Smart Product Search', 
      smartSearchDesc: 'Automatically search multiple e-commerce platforms to find materials and tools that best match your needs, saving you time and effort.',
      qualityAssessment: 'Smart Quality Assessment',
      qualityAssessmentDesc: 'Based on multi-dimensional assessment algorithms, analyze product quality, price reasonableness, and user reviews to recommend the highest quality products.',
      agentArchitecture: 'Agent Collaboration Architecture',
      agentArchitectureDesc: 'Using modular Agent architecture, each Agent focuses on specific tasks and works together to provide the best analysis results.'
    },
    
    techStack: {
      title: 'Technical Architecture',
      frontend: 'Frontend Technology',
      backend: 'Backend Technology', 
      agents: 'Agent Modules',
      imageAnalysis: 'Image Analysis Agent',
      imageAnalysisDesc: 'Responsible for analyzing uploaded images and identifying DIY project content',
      productSearch: 'Product Search Agent',
      productSearchDesc: 'Search for related products on multiple e-commerce platforms',
      qualityAssessment: 'Quality Assessment Agent',
      qualityAssessmentDesc: 'Assess product quality and value for money'
    },
    
    contact: {
      title: 'Contact Us',
      subtitle: 'If you have any questions or suggestions, please feel free to contact us:',
      feedback: 'Feedback: support@diy-helper.com',
      github: 'GitHub: github.com/diy-agent-system'
    }
  },
  
  // Projects Page
  projects: {
    title: 'My Projects',
    subtitle: 'Manage your DIY project analysis history',
    empty: 'No project records yet',
    emptyDesc: 'You haven\'t analyzed any DIY projects yet',
    startAnalysis: 'Start Analyzing Projects'
  },
  
  // Common
  common: {
    loading: 'Loading...',
    error: 'Error',
    success: 'Success',
    cancel: 'Cancel',
    confirm: 'Confirm',
    save: 'Save',
    delete: 'Delete',
    edit: 'Edit',
    close: 'Close',
    back: 'Back',
    next: 'Next',
    previous: 'Previous',
    search: 'Search',
    filter: 'Filter',
    sort: 'Sort',
    refresh: 'Refresh',
    seconds: 's',
    ready: 'Ready',
    inStock: 'In Stock',
    outOfStock: 'Out of Stock',
    viewProduct: 'View Product',
    viewDetails: 'View Details',
    viewAll: 'View All'
  },
  
  // Tool Identification
  toolIdentification: {
    title: 'Tool Identification Assistant',
    subtitle: 'Upload tool images to identify models and find purchase options',
    loginRequired: 'Login Required',
    loginPrompt: 'Please login to use the tool identification feature',
    dailyUsage: 'Daily Usage',
    uploadImage: 'Upload Tool Image',
    dragOrClick: 'Drag image here or click to upload',
    uploadHint: 'Support multiple image formats for accurate identification results',
    supportedFormats: 'Supports JPG, PNG formats, max 10MB',
    includeAlternatives: 'Include alternative products',
    exactOnly: 'Exact matches only',
    alternativesDesc: 'Show similar alternative products and different brand options',
    exactDesc: 'Show only perfectly matching product results',
    highAccuracy: 'High accuracy mode',
    fastMode: 'Fast mode',
    highAccuracyDesc: 'Use AI deep analysis for more accurate but slower identification',
    fastModeDesc: 'Quick identification, suitable for simple tool recognition',
    examples: 'Examples',
    example1: 'Drill',
    example2: 'Saw',
    example3: 'Wrench',
    identify: 'Identify Tool',
    selectImage: 'Please select an image first',
    quotaExceeded: 'Daily quota exceeded',
    upgradePrompt: 'Upgrade membership for more identifications',
    identifySuccess: 'Tool identified successfully!',
    identifyFailed: 'Tool identification failed',
    invalidFormat: 'Unsupported file format, please upload image files',
    fileTooLarge: 'File too large, please upload images smaller than 10MB',
    rotateNotImplemented: 'Image rotation feature coming soon',
    toolInfo: 'Tool Information',
    confidence: 'Confidence',
    toolName: 'Tool Name',
    brand: 'Brand',
    model: 'Model',
    category: 'Category',
    specifications: 'Specifications',
    exactMatches: 'Exact Matches',
    alternatives: 'Alternative Products',
    recentHistory: 'Recent History',
    stage1: 'Analyzing image',
    stage2: 'Identifying tool features',
    stage3: 'Matching product database',
    stage4: 'Generating identification results'
  },

  // Tool Categories
  toolCategory: {
    power_tools: 'Power Tools',
    hand_tools: 'Hand Tools',
    measuring: 'Measuring Tools',
    cutting: 'Cutting Tools',
    fastening: 'Fastening Tools',
    outdoor: 'Outdoor Tools',
    unknown: 'Unknown'
  },

  // Authentication
  auth: {
    welcome: 'Welcome Back',
    createAccount: 'Create Account',
    loginSubtitle: 'Sign in to access tool identification features',
    registerSubtitle: 'Join us to unlock powerful tool identification',
    login: 'Login',
    register: 'Register',
    logout: 'Logout',
    username: 'Username',
    password: 'Password',
    email: 'Email',
    confirmPassword: 'Confirm Password',
    acceptTerms: 'I accept the terms and conditions',
    noAccount: "Don't have an account?",
    haveAccount: 'Already have an account?',
    demoAccount: 'Demo Account',
    demoDescription: 'Try our features with a premium demo account',
    tryDemo: 'Try Demo',
    loginSuccess: 'Login successful!',
    loginFailed: 'Login failed',
    registerSuccess: 'Registration successful!',
    registerFailed: 'Registration failed',
    logoutSuccess: 'Logout successful',
    usernameRequired: 'Username is required',
    passwordRequired: 'Password is required',
    emailRequired: 'Email is required',
    confirmPasswordRequired: 'Please confirm your password',
    usernameLength: 'Username must be 3-20 characters',
    passwordLength: 'Password must be at least 6 characters',
    emailInvalid: 'Please enter a valid email',
    passwordMismatch: 'Passwords do not match',
    usernameInvalid: 'Username can only contain letters, numbers, and underscores',
    mustAcceptTerms: 'You must accept the terms and conditions'
  },

  // Membership
  membership: {
    free: 'Free',
    premium: 'Premium',
    pro: 'Pro',
    level: 'Membership Level',
    upgrade: 'Upgrade',
    freeMembershipIncluded: 'Free Membership Included',
    upgradeHint: 'Upgrade for unlimited identifications and advanced features',
    freeFeatures: {
      identifications: '5 identifications per day',
      history: '7 days history',
      alternatives: '3 alternative products'
    }
  },

  // Dashboard
  dashboard: {
    subtitle: 'Manage your tool identification history and account',
    userInfo: 'User Information',
    identificationHistory: 'Identification History',
    noHistory: 'No identification history yet',
    startIdentifying: 'Start Identifying Tools',
    loadHistoryFailed: 'Failed to load history',
    confirmDelete: 'Are you sure you want to delete this identification?',
    deleteSuccess: 'Identification deleted successfully',
    deleteFailed: 'Failed to delete identification'
  },

  // Footer
  footer: {
    copyright: '© 2024 DIY Smart Assistant. Built with AI Agent Architecture'
  }
}