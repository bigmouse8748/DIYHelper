export default {
  // 导航
  nav: {
    home: '首页',
    products: '产品推荐',
    diyAssistant: 'DIY助手',
    toolIdentification: '工具识别',
    projects: '我的项目',
    about: '关于',
    dashboard: '个人中心',
    logo: 'DIY智能助手'
  },

  // 首页
  home: {
    hero: {
      title: 'DIY智能助手',
      subtitle: 'AI驱动的项目分析和工具识别平台，专为DIY爱好者设计',
      getStarted: '开始使用',
      startProject: '开始新项目'
    },
    
    features: {
      title: '我们的功能',
      tryNow: '立即试用',
      loginRequired: '需要登录',
      
      diyAssistant: {
        title: 'DIY智能助手',
        description: '上传图片，获取AI驱动的DIY项目分析，并获得智能工具和材料推荐',
        benefits: [
          'AI驱动的项目分析',
          '智能材料推荐',
          '实时产品定价',
          '逐步指导'
        ]
      },
      
      toolIdentification: {
        title: '工具识别',
        description: '通过照片识别工具，获取详细规格、定价和购买选项',
        benefits: [
          '即时工具识别',
          '详细规格说明',
          '价格比较',
          '购物推荐'
        ]
      },
      
      productRecommendations: {
        title: '产品推荐',
        description: '浏览我们精心挑选的DIY工具和材料，来自可信商家的优惠价格',
        benefits: [
          '精选产品推荐',
          '优惠价格保证',
          '多家商户选择',
          '无需登录访问'
        ]
      }
    },
    
    examples: {
      title: '实际效果展示',
      
      diy: {
        title: 'DIY项目分析',
        description: '上传您的木工项目照片，获得全面指导',
        features: ['材料清单', '工具推荐', '安全提示', '步骤指南']
      },
      
      tool: {
        title: '工具识别',
        description: '识别任何工具，获得即时产品信息和购买选项',
        features: ['品牌识别', '型号详情', '价格比较', '替代选项']
      }
    },
    
    authPrompt: {
      title: '准备开始了吗？',
      description: '免费注册，使用我们的AI驱动DIY工具，立即开始您的下一个项目！',
      register: '免费注册',
      login: '登录'
    },
    
    welcomeBack: '欢迎回来，{username}！',
    dashboardPrompt: {
      description: '继续您的项目或开始新的创作',
      dashboard: '前往控制台',
      newProject: '新项目'
    },
    
    messages: {
      loginRequired: '请登录以使用此功能'
    }
  },

  // DIY助手页面
  diy: {
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
    seconds: '秒',
    ready: '已就绪',
    inStock: '有库存',
    outOfStock: '无库存',
    viewProduct: '查看产品',
    viewDetails: '查看详情',
    viewAll: '查看全部',
    view: '视图'
  },

  // 工具识别
  toolIdentification: {
    title: '工具识别助手',
    subtitle: '上传工具图片，识别型号并找到购买选项',
    loginRequired: '需要登录',
    loginPrompt: '请登录以使用工具识别功能',
    dailyUsage: '每日使用量',
    uploadImage: '上传工具图片',
    dragOrClick: '拖拽图片到此处或点击上传',
    uploadHint: '支持多种格式图片，获得精准识别结果',
    supportedFormats: '支持 JPG、PNG 格式，最大 10MB',
    includeAlternatives: '包含替代产品',
    exactOnly: '仅精确匹配',
    alternativesDesc: '显示类似的替代产品和不同品牌选项',
    exactDesc: '仅显示完全匹配的产品结果',
    highAccuracy: '高精度模式',
    fastMode: '快速模式',
    highAccuracyDesc: '使用AI深度分析，识别更准确但速度较慢',
    fastModeDesc: '快速识别，适合简单工具识别',
    examples: '示例',
    example1: '电钻',
    example2: '电锯',
    example3: '扳手',
    identify: '识别工具',
    selectImage: '请先选择图片',
    quotaExceeded: '每日配额已用尽',
    upgradePrompt: '升级会员以获得更多识别次数',
    identifySuccess: '工具识别成功！',
    identifyFailed: '工具识别失败',
    invalidFormat: '不支持的文件格式，请上传图片文件',
    fileTooLarge: '文件过大，请上传小于10MB的图片',
    rotateNotImplemented: '图片旋转功能即将推出',
    toolInfo: '工具信息',
    confidence: '置信度',
    toolName: '工具名称',
    brand: '品牌',
    model: '型号',
    category: '类别',
    specifications: '规格参数',
    exactMatches: '精确匹配',
    alternatives: '替代产品',
    recentHistory: '最近历史',
    stage1: '正在分析图片',
    stage2: '识别工具特征',
    stage3: '匹配产品数据库',
    stage4: '生成识别结果'
  },

  // 工具分类
  toolCategory: {
    power_tools: '电动工具',
    hand_tools: '手动工具',
    measuring: '测量工具',
    cutting: '切割工具',
    fastening: '固定工具',
    outdoor: '户外工具',
    unknown: '未知'
  },

  // 用户认证
  auth: {
    welcome: '欢迎回来',
    createAccount: '创建账户',
    loginSubtitle: '登录以使用工具识别功能',
    registerSubtitle: '注册以解锁强大的工具识别功能',
    login: '登录',
    register: '注册',
    logout: '退出',
    username: '用户名',
    password: '密码',
    email: '邮箱',
    confirmPassword: '确认密码',
    acceptTerms: '我接受服务条款',
    noAccount: '没有账户？',
    haveAccount: '已有账户？',
    demoAccount: '演示账户',
    demoDescription: '使用高级演示账户体验功能',
    tryDemo: '试用演示',
    loginSuccess: '登录成功！',
    loginFailed: '登录失败',
    registerSuccess: '注册成功！',
    registerFailed: '注册失败',
    logoutSuccess: '退出成功',
    usernameRequired: '请输入用户名',
    passwordRequired: '请输入密码',
    emailRequired: '请输入邮箱',
    confirmPasswordRequired: '请确认密码',
    usernameLength: '用户名长度为3-20个字符',
    passwordLength: '密码至少6个字符',
    emailInvalid: '请输入有效的邮箱地址',
    passwordMismatch: '两次密码不一致',
    usernameInvalid: '用户名只能包含字母、数字和下划线',
    mustAcceptTerms: '您必须接受服务条款'
  },

  // 会员等级
  membership: {
    free: '免费',
    premium: '高级',
    pro: '专业',
    admin: '管理员',
    undefined: '未知',
    level: '会员等级',
    upgrade: '升级',
    freeMembershipIncluded: '包含免费会员',
    upgradeHint: '升级以获得无限识别和高级功能',
    freeFeatures: {
      identifications: '每日5次识别',
      history: '7天历史记录',
      alternatives: '3个替代产品'
    }
  },

  // 用户面板
  dashboard: {
    subtitle: '管理您的工具识别历史和账户信息',
    userInfo: '用户信息',
    identificationHistory: '识别历史',
    noHistory: '暂无识别历史记录',
    startIdentifying: '开始识别工具',
    loadHistoryFailed: '加载历史失败',
    confirmDelete: '确定要删除此识别记录吗？',
    deleteSuccess: '识别记录删除成功',
    deleteFailed: '删除识别记录失败'
  },

  // 页脚
  footer: {
    copyright: '© 2024 DIY智能助手。采用AI智能体架构构建'
  },

  // 管理员
  admin: {
    panel: {
      title: '管理员面板'
    },
    accessDenied: '需要管理员权限',
    
    products: {
      title: '产品推荐管理',
      subtitle: '管理推广产品链接和推荐',
      addProduct: '添加产品',
      addFromUrl: '从链接添加产品',
      editProduct: '编辑产品',
      productList: '产品列表',
      filterByCategory: '按分类筛选',
      filterByMerchant: '按商家筛选',
      includeInactive: '包含未激活产品',
      featured: '精选',
      inactive: '未激活',
      noProducts: '暂无产品',
      addFirstProduct: '添加第一个产品',
      create: '创建产品',
      confirmDelete: '确定要删除此产品吗？',
      views: '浏览量',
      clicks: '点击量',
      
      form: {
        pasteUrl: '粘贴产品链接',
        urlDescription: '只需粘贴来自亚马逊、家得宝、劳氏或沃尔玛的任何产品链接，我们的系统会自动提取产品信息。',
        title: '产品标题',
        titlePlaceholder: '输入产品标题（如：德瓦特20V电钻）',
        productUrl: '产品链接',
        urlPlaceholder: 'https://www.amazon.com/产品链接 或其他商家链接',
        urlHint: '支持亚马逊、家得宝、劳氏、沃尔玛推广链接',
        category: '分类',
        selectCategory: '选择分类',
        merchant: '商家',
        selectMerchant: '选择商家',
        description: '描述',
        descriptionPlaceholder: '可选的产品描述或特性',
        originalPrice: '原价',
        salePrice: '促销价',
        rating: '评分',
        brand: '品牌',
        brandPlaceholder: '如：德瓦特、密尔沃基',
        model: '型号',
        modelPlaceholder: '如：DCD771C2',
        imageUrl: '图片链接',
        imageUrlPlaceholder: '产品图片链接（可选）',
        isFeatured: '精选产品',
        isActive: '激活产品',
        featuredHint: '精选产品会优先显示在列表中'
      },
      
      preview: {
        title: '预览抓取信息',
        button: '预览产品'
      },
      
      table: {
        title: '产品标题',
        category: '分类',
        merchant: '商家',
        price: '价格',
        analytics: '统计',
        actions: '操作'
      },
      
      validation: {
        titleRequired: '产品标题为必填项',
        titleLength: '标题长度必须在3-255个字符之间',
        urlRequired: '产品链接为必填项',
        urlInvalid: '请输入有效的链接地址'
      },
      
      messages: {
        createSuccess: '产品创建成功',
        updateSuccess: '产品更新成功',
        deleteSuccess: '产品删除成功',
        previewSuccess: '产品信息抓取成功'
      },
      
      errors: {
        loadFailed: '加载产品失败',
        createFailed: '创建产品失败',
        updateFailed: '更新产品失败',
        deleteFailed: '删除产品失败',
        previewFailed: '抓取产品信息失败，请检查链接是否正确。'
      },

      addImage: '添加图片',
      
      imageUpload: {
        title: '上传产品图片',
        validation: {
          urlRequired: '请输入图片链接',
          urlInvalid: '请输入有效的链接'
        }
      }
    },

    users: {
      title: '用户管理',
      subtitle: '管理用户、权限和系统访问',
      userCount: '用户总数',
      activeUsers: '活跃用户',
      premiumUsers: '付费用户',
      adminUsers: '管理员',
      addUser: '添加用户',
      editUser: '编辑用户',
      searchPlaceholder: '按用户名或邮箱搜索...',
      
      filters: {
        all: '全部用户',
        active: '仅活跃用户',
        inactive: '仅非活跃用户',
        premium: '付费会员',
        admin: '管理员'
      },
      
      actions: {
        edit: '编辑',
        delete: '删除',
        resetPassword: '重置密码',
        toggleStatus: '切换状态',
        forceLogout: '强制登出',
        export: '导出',
        batchDelete: '批量删除',
        batchActive: '批量激活',
        batchInactive: '批量停用'
      },
      
      form: {
        username: '用户名',
        email: '邮箱',
        password: '密码',
        confirmPassword: '确认密码',
        membershipLevel: '会员等级',
        membership: '会员等级',
        isActive: '账户状态',
        activeUser: '激活用户',
        lastLogin: '最后登录',
        createdAt: '创建时间',
        user: '用户',
        newPassword: '新密码'
      },
      
      status: {
        active: '活跃',
        inactive: '非活跃',
        never: '从未登录'
      },
      
      membership: {
        free: '免费用户',
        premium: '付费用户',
        admin: '管理员'
      },
      
      confirmations: {
        deleteUser: '确定要删除此用户吗？',
        resetPassword: '确定要重置此用户的密码吗？',
        toggleStatus: '确定要更改此用户的状态吗？',
        forceLogout: '确定要强制此用户登出吗？',
        batchDelete: '确定要删除所选的 {count} 个用户吗？'
      },
      
      messages: {
        userCreated: '用户创建成功',
        userUpdated: '用户更新成功',
        userDeleted: '用户删除成功',
        passwordReset: '密码重置成功',
        statusToggled: '用户状态更新成功',
        logoutForced: '用户强制登出成功',
        exportCompleted: '用户导出成功'
      },
      
      errors: {
        loadFailed: '加载用户失败',
        createFailed: '创建用户失败',
        updateFailed: '更新用户失败',
        deleteFailed: '删除用户失败',
        passwordResetFailed: '重置密码失败',
        exportFailed: '导出用户失败'
      }
    }
  },

  // 产品推荐
  products: {
    title: '产品推荐',
    subtitle: '精选DIY工具和材料推荐，价格实惠品质可靠',
    featured: '精选',
    noProducts: '暂无产品',
    refresh: '刷新',
    priceOnSite: '到商家查看价格',
    buyNow: '访问商店',
    loadMore: '加载更多',
    
    filters: {
      all: '全部产品',
      allMerchants: '全部商家',
      allProjectTypes: '全部项目类型',
      featuredOnly: '仅显示精选'
    },
    
    gridView: '网格视图',
    listView: '列表视图',
    
    errors: {
      loadFailed: '加载产品失败'
    }
  }
}