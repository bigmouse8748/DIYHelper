export default {
  // 导航
  nav: {
    home: '首页',
    projects: '我的项目',
    about: '关于',
    logo: 'DIY智能助手'
  },

  // 首页
  home: {
    title: 'DIY智能助手',
    subtitle: '上传图片，获取AI驱动的DIY项目分析，并获得智能工具和材料推荐',
    uploadTitle: '上传项目图片',
    uploadTip: '支持JPG、PNG格式，最多4张图片',
    projectDescription: '项目描述',
    projectDescriptionPlaceholder: '描述您的DIY项目（可选）',
    projectType: '项目类型',
    projectTypePlaceholder: '选择项目类型（可选）',
    budgetRange: '预算范围',
    budgetRangePlaceholder: '选择预算范围（可选）',
    analyzeButton: '开始智能分析',
    analyzing: '分析中...',
    
    // 项目类型
    projectTypes: {
      woodworking: '木工制作',
      electronics: '电子制作', 
      crafts: '工艺制作',
      homeDecor: '家居装饰',
      repair: '维修保养',
      other: '其他'
    },
    
    // 预算范围
    budgetRanges: {
      'under50': '50美元以下',
      '50to150': '50-150美元', 
      '150to300': '150-300美元',
      '300to500': '300-500美元',
      'over500': '500美元以上'
    },
    
    // 加载状态
    loading: {
      uploading: '正在上传图片...',
      analyzing: 'AI正在分析您的项目...',
      searching: '正在搜索相关产品...',
      assessing: '正在评估产品质量...',
      generating: '正在生成分析报告...'
    },
    
    // 消息提示
    messages: {
      uploadError: '请至少选择一张图片',
      imageTypeError: '只允许上传图片文件！',
      imageSizeError: '图片大小不能超过10MB！',
      analysisError: '分析失败，请重试',
      analysisSuccess: '分析完成！',
      maxImagesWarning: '最多允许4张图片，当前已选择{count}张图片'
    }
  },

  // 分析结果
  results: {
    projectAnalysis: '项目分析结果',
    toolsAndMaterials: '工具和材料', 
    materialsNeeded: '所需材料',
    toolsNeeded: '所需工具',
    safetyNotes: '安全注意事项',
    buildingSteps: '制作步骤',
    smartRecommendations: '智能产品推荐',
    shoppingTips: '购物建议',
    bestRecommendations: '最佳推荐',
    totalTime: '总耗时',
    agentsUsed: '使用的智能体',
    analysisInfo: '分析信息',
    
    // 难度等级
    difficulty: {
      label: '难度',
      simple: '简单',
      medium: '中等', 
      hard: '困难'
    },
    
    // 必要性等级  
    necessity: {
      essential: '必需',
      recommended: '推荐',
      optional: '可选'
    },
    
    // 推荐等级
    recommendations: {
      'Professional Choice': '专业首选',
      'Highly Recommended': '强烈推荐',
      'Best Value': '性价比最佳', 
      'Safety Essential': '安全必备',
      'Recommended': '推荐',
      'Good Choice': '不错选择'
    },
    
    // 产品操作
    viewProduct: '查看商品',
    assessmentDetails: '评估详情',
    productUnavailable: '商品链接不可用',
    
    // 空状态
    noMaterials: '未检测到具体材料',
    noTools: '未检测到具体工具', 
    noSuggestions: '暂无购物建议',
    
    // 额外翻译
    averageRating: '平均评分',
    productsFound: '共找到{count}个产品',
    totalProductsAssessed: '评估产品数',
    averageQualityScore: '平均质量评分',
    scoreUnit: '分',
    specification: '规格',
    quantity: '数量',
    estimatedPrice: '预估价格',
    estimatedTime: '预估时间',
    stepLabel: '步骤'
  },

  // 关于页面
  about: {
    title: '关于DIY智能助手',
    subtitle: 'AI智能体驱动的智能DIY项目分析平台',
    
    features: {
      smartAnalysis: '智能图像分析',
      smartAnalysisDesc: '采用尖端AI视觉技术，智能识别DIY项目类型、所需材料和工具，提供专业分析结果。',
      smartSearch: '智能产品搜索', 
      smartSearchDesc: '自动搜索多个电商平台，找到最符合您需求的材料和工具，节省您的时间和精力。',
      qualityAssessment: '智能质量评估',
      qualityAssessmentDesc: '基于多维度评估算法，分析产品质量、价格合理性和用户评价，推荐最优质的产品。',
      agentArchitecture: '智能体协作架构',
      agentArchitectureDesc: '采用模块化智能体架构，每个智能体专注于特定任务，协同工作提供最佳分析结果。'
    },
    
    techStack: {
      title: '技术架构',
      frontend: '前端技术',
      backend: '后端技术', 
      agents: '智能体模块',
      imageAnalysis: '图像分析智能体',
      imageAnalysisDesc: '负责分析上传的图片，识别DIY项目内容',
      productSearch: '产品搜索智能体',
      productSearchDesc: '在多个电商平台搜索相关产品',
      qualityAssessment: '质量评估智能体',
      qualityAssessmentDesc: '评估产品质量和性价比'
    },
    
    contact: {
      title: '联系我们',
      subtitle: '如果您有任何问题或建议，请随时联系我们：',
      feedback: '反馈邮箱：support@diy-helper.com',
      github: 'GitHub：github.com/diy-agent-system'
    }
  },

  // 项目页面
  projects: {
    title: '我的项目',
    subtitle: '管理您的DIY项目分析历史',
    empty: '暂无项目记录',
    emptyDesc: '您还没有分析过任何DIY项目',
    startAnalysis: '开始分析项目'
  },

  // 通用
  common: {
    loading: '加载中...',
    error: '错误',
    success: '成功',
    cancel: '取消',
    confirm: '确认',
    save: '保存',
    delete: '删除',
    edit: '编辑',
    close: '关闭',
    back: '返回',
    next: '下一步',
    previous: '上一步',
    search: '搜索',
    filter: '筛选',
    sort: '排序',
    refresh: '刷新',
    seconds: '秒'
  },

  // 页脚
  footer: {
    copyright: '© 2024 DIY智能助手。采用AI智能体架构构建'
  }
}