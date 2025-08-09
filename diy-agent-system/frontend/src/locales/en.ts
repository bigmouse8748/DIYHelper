export default {
  // Navigation
  nav: {
    home: 'Home',
    projects: 'My Projects',
    about: 'About',
    logo: 'DIY Smart Assistant'
  },
  
  // Home Page
  home: {
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
    seconds: 's'
  },
  
  // Footer
  footer: {
    copyright: '© 2024 DIY Smart Assistant. Built with AI Agent Architecture'
  }
}