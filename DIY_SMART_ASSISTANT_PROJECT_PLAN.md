# DIY Smart Assistant - 智能DIY助手平台

## 🎯 项目愿景

打造一个现代化的智能DIY助手平台，为用户提供AI驱动的项目分析、工具识别和购物建议服务。通过先进的机器学习技术，帮助DIY爱好者更好地规划和完成项目。

### 核心价值主张
- **智能分析**: 使用AI技术分析用户上传的项目图片，提供专业的DIY指导
- **工具识别**: 通过图像识别技术，帮助用户识别工具并提供购买建议
- **个性化推荐**: 基于用户偏好和项目需求，提供精准的产品推荐
- **多级服务**: 提供从免费到专业版的多层次服务

---

## 🏗️ 技术架构设计

### 整体架构原则
- **微服务思想**: 模块化设计，职责分离
- **API优先**: RESTful API设计，前后端分离
- **可扩展性**: 支持水平扩展和功能扩展
- **安全性**: 完善的认证授权和数据保护
- **用户体验**: 响应式设计，支持多设备访问

### 技术栈选择

#### **前端技术栈**
```typescript
// 核心框架
Vue 3 + TypeScript + Composition API

// UI框架
Element Plus (组件丰富，文档完善)

// 状态管理
Pinia (Vue 3官方推荐，简单易用)

// 路由
Vue Router 4

// 构建工具
Vite (快速构建，热更新)

// 国际化
Vue I18n (支持中英文切换)

// HTTP客户端
Axios (拦截器，请求响应处理)

// 工具库
Day.js (日期处理)
Lodash (工具函数)
```

#### **后端技术栈**
```python
# Web框架
FastAPI (高性能，自动API文档，类型提示)

# 数据库ORM
SQLAlchemy (功能强大，支持多数据库)

# 数据库
PostgreSQL (生产) / SQLite (开发)

# 认证系统 - 混合本地认证
JWT (无状态，适合分布式，15-30分钟过期)
bcrypt (安全密码哈希)
Refresh Token (7天过期，可撤销)
Token黑名单机制 (Redis存储)
邮箱验证和密码重置

# AI服务
OpenAI GPT-4 Vision API (图像分析)

# 文件处理
Pillow (图像处理)
python-multipart (文件上传)

# 数据验证
Pydantic (类型验证，数据序列化)

# 异步支持
asyncio + httpx (异步HTTP调用)

# 任务队列
Celery + Redis (后台任务处理)
```

---

## 📊 系统设计

### 数据库设计

#### **用户系统**
```sql
-- 用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    avatar_url VARCHAR(500),
    user_type user_type_enum DEFAULT 'free',
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    phone VARCHAR(20),
    location VARCHAR(100)
);

-- 用户类型枚举
CREATE TYPE user_type_enum AS ENUM ('free', 'pro', 'premium', 'admin');

-- 用户会话表 (JWT黑名单)
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    jti VARCHAR(36) UNIQUE NOT NULL,  -- JWT ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_revoked BOOLEAN DEFAULT FALSE
);
```

#### **产品系统**
```sql
-- 产品表
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category product_category_enum NOT NULL,
    subcategory VARCHAR(100),
    brand VARCHAR(100),
    model VARCHAR(100),
    sku VARCHAR(100),
    
    -- 价格信息
    original_price DECIMAL(10,2),
    sale_price DECIMAL(10,2),
    discount_percentage INTEGER,
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- 商家信息
    merchant merchant_enum NOT NULL,
    merchant_product_id VARCHAR(100),
    product_url VARCHAR(500) NOT NULL,
    
    -- 媒体资源
    images JSONB DEFAULT '[]',  -- [{"url": "", "alt": "", "type": "main|gallery"}]
    videos JSONB DEFAULT '[]',
    
    -- 规格参数
    specifications JSONB DEFAULT '{}',
    dimensions JSONB DEFAULT '{}',  -- {"length": 10, "width": 5, "height": 3, "weight": 2}
    
    -- 评价信息
    rating DECIMAL(3,2),
    rating_count INTEGER DEFAULT 0,
    reviews_summary JSONB DEFAULT '{}',
    
    -- 标签和分类
    tags JSONB DEFAULT '[]',
    project_types JSONB DEFAULT '[]',
    difficulty_levels JSONB DEFAULT '[]',  -- ["beginner", "intermediate", "advanced"]
    
    -- 状态管理
    is_featured BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    availability_status availability_enum DEFAULT 'in_stock',
    sort_order INTEGER DEFAULT 0,
    
    -- 统计信息
    view_count INTEGER DEFAULT 0,
    click_count INTEGER DEFAULT 0,
    purchase_count INTEGER DEFAULT 0,
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_checked TIMESTAMP,
    
    -- 创建者
    created_by INTEGER REFERENCES users(id)
);

-- 产品分类枚举
CREATE TYPE product_category_enum AS ENUM (
    'power_tools', 'hand_tools', 'materials', 'hardware', 
    'safety_equipment', 'measuring_tools', 'automotive', 
    'electrical', 'plumbing', 'woodworking', 'metalworking'
);

-- 商家枚举
CREATE TYPE merchant_enum AS ENUM (
    'amazon', 'home_depot', 'lowes', 'harbor_freight',
    'menards', 'ace_hardware', 'walmart', 'target'
);

-- 可用性枚举
CREATE TYPE availability_enum AS ENUM (
    'in_stock', 'low_stock', 'out_of_stock', 'discontinued'
);
```

#### **AI服务系统**
```sql
-- 工具识别记录
CREATE TABLE tool_identifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    
    -- 输入信息
    original_filename VARCHAR(255),
    image_path VARCHAR(500) NOT NULL,
    image_hash VARCHAR(64),  -- 防止重复识别
    file_size INTEGER,
    image_dimensions JSONB,  -- {"width": 1920, "height": 1080}
    
    -- AI识别结果
    identification_result JSONB NOT NULL,
    -- {
    --   "primary": {"name": "DeWalt Circular Saw", "model": "DWE575", "confidence": 0.95},
    --   "alternatives": [{"name": "...", "confidence": 0.85}],
    --   "category": "power_tools",
    --   "features": ["cordless", "7.25_inch_blade"]
    -- }
    
    -- 推荐产品
    recommended_products JSONB DEFAULT '[]',  -- 产品ID数组
    
    -- 处理信息
    processing_time DECIMAL(5,3),  -- 处理时间(秒)
    ai_model_version VARCHAR(50),
    confidence_score DECIMAL(3,2),
    
    -- 用户反馈
    user_feedback JSONB DEFAULT '{}',  -- {"helpful": true, "rating": 5, "comment": ""}
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- DIY项目分析记录
CREATE TABLE project_analyses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    
    -- 项目输入
    project_name VARCHAR(200),
    description TEXT,
    images JSONB NOT NULL,  -- [{"path": "", "filename": "", "role": "main|detail|reference"}]
    project_type VARCHAR(50),
    budget_range budget_range_enum,
    skill_level skill_level_enum,
    timeline VARCHAR(50),  -- "weekend", "week", "month"
    
    -- AI分析结果
    analysis_result JSONB NOT NULL,
    -- {
    --   "project_overview": {"name": "...", "description": "...", "difficulty": "intermediate"},
    --   "materials": [{"item": "2x4 lumber", "quantity": "10 pieces", "estimated_cost": 25.99}],
    --   "tools_required": [{"tool": "circular_saw", "essential": true, "alternatives": []}],
    --   "steps": [{"step": 1, "title": "...", "description": "...", "time": "30min"}],
    --   "safety_notes": ["wear safety glasses", "use dust mask"],
    --   "tips": ["measure twice cut once", "pre-drill holes"],
    --   "estimated_total_cost": {"min": 150, "max": 250},
    --   "estimated_time": {"min": "4 hours", "max": "8 hours"}
    -- }
    
    -- 推荐产品
    recommended_products JSONB DEFAULT '[]',
    
    -- 处理信息
    processing_time DECIMAL(5,3),
    ai_model_version VARCHAR(50),
    
    -- 项目状态
    project_status project_status_enum DEFAULT 'planned',
    progress_notes TEXT,
    completion_date TIMESTAMP,
    
    -- 用户评价
    user_rating INTEGER CHECK (user_rating >= 1 AND user_rating <= 5),
    user_feedback TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 预算范围枚举
CREATE TYPE budget_range_enum AS ENUM (
    'under_50', '50_to_150', '150_to_300', '300_to_500', 
    '500_to_1000', 'over_1000', 'no_limit'
);

-- 技能水平枚举
CREATE TYPE skill_level_enum AS ENUM ('beginner', 'intermediate', 'advanced', 'expert');

-- 项目状态枚举
CREATE TYPE project_status_enum AS ENUM (
    'planned', 'in_progress', 'completed', 'abandoned', 'on_hold'
);
```

#### **系统管理**
```sql
-- 用户使用配额记录
CREATE TABLE user_quotas (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    service_type service_type_enum NOT NULL,
    usage_date DATE NOT NULL,
    usage_count INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, service_type, usage_date)
);

CREATE TYPE service_type_enum AS ENUM (
    'tool_identification', 'project_analysis', 'api_call'
);

-- 系统配置表
CREATE TABLE system_configs (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value JSONB NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,  -- 是否对前端公开
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 审计日志
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,  -- "login", "create_product", "delete_user"
    resource_type VARCHAR(50),  -- "user", "product", "project"
    resource_id INTEGER,
    changes JSONB,  -- 变更前后的数据对比
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔐 认证系统详细设计

### **为什么选择混合本地认证（JWT）**

经过深入分析，我们最终选择了**混合本地认证系统**而非AWS Cognito，主要原因：

#### **技术决策理由**
1. **简化复杂度**: 避免Cognito配置的复杂性和潜在问题
2. **成本效益**: 早期用户量下成本极低，后期可扩展
3. **完全控制**: 可以完全定制用户流程和体验
4. **调试友好**: 问题定位和解决更加直观
5. **快速迭代**: 需求变更时可以快速实现

#### **架构优势**
- ✅ **现代化**: 使用业界标准JWT技术
- ✅ **安全性**: bcrypt密码哈希 + token撤销机制
- ✅ **可扩展**: 抽象接口设计，便于后期升级
- ✅ **性能**: 无状态token，支持高并发
- ✅ **灵活性**: 可以根据业务需求灵活调整

### **JWT认证系统架构**

#### **核心组件设计**
```python
# core/auth.py - 认证核心
class AuthService:
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire = timedelta(minutes=30)  # 短期token
        self.refresh_token_expire = timedelta(days=7)     # 长期token
        
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """验证用户凭据"""
        user = await get_user_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            return None
        return user
    
    async def create_tokens(self, user: User) -> TokenPair:
        """创建访问token和刷新token"""
        # JWT payload
        access_payload = {
            "sub": str(user.id),
            "email": user.email,
            "user_type": user.user_type,
            "exp": datetime.utcnow() + self.access_token_expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        refresh_payload = {
            "sub": str(user.id),
            "exp": datetime.utcnow() + self.refresh_token_expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
            "jti": str(uuid.uuid4())  # 用于token撤销
        }
        
        access_token = jwt.encode(access_payload, self.secret_key, self.algorithm)
        refresh_token = jwt.encode(refresh_payload, self.secret_key, self.algorithm)
        
        # 存储refresh token以便撤销
        await self._store_refresh_token(refresh_payload["jti"], user.id)
        
        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=int(self.access_token_expire.total_seconds())
        )
    
    async def verify_token(self, token: str, token_type: str = "access") -> Optional[dict]:
        """验证token并返回payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # 检查token类型
            if payload.get("type") != token_type:
                return None
                
            # 如果是refresh token，检查是否被撤销
            if token_type == "refresh":
                jti = payload.get("jti")
                if not jti or await self._is_token_revoked(jti):
                    return None
                    
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    async def refresh_access_token(self, refresh_token: str) -> TokenPair:
        """使用refresh token获取新的access token"""
        payload = await self.verify_token(refresh_token, "refresh")
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
            
        user = await get_user_by_id(int(payload["sub"]))
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User inactive")
            
        return await self.create_tokens(user)
    
    async def revoke_token(self, refresh_token: str) -> bool:
        """撤销refresh token"""
        try:
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=[self.algorithm])
            jti = payload.get("jti")
            if jti:
                await self._revoke_refresh_token(jti)
                return True
        except jwt.JWTError:
            pass
        return False

# 密码处理
class PasswordService:
    @staticmethod
    def hash_password(password: str) -> str:
        """哈希密码"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    @staticmethod
    def generate_reset_token() -> str:
        """生成密码重置token"""
        return secrets.token_urlsafe(32)
```

#### **数据库扩展**
```sql
-- 用户认证相关表
-- 添加到用户表的字段
ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN email_verify_token VARCHAR(64);
ALTER TABLE users ADD COLUMN password_reset_token VARCHAR(64);
ALTER TABLE users ADD COLUMN password_reset_expires TIMESTAMP;
ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN locked_until TIMESTAMP;

-- refresh token管理表
CREATE TABLE refresh_tokens (
    id SERIAL PRIMARY KEY,
    jti VARCHAR(36) UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    revoked_at TIMESTAMP,
    is_revoked BOOLEAN DEFAULT FALSE
);

-- 邮箱验证码表
CREATE TABLE email_verification_codes (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) NOT NULL,
    code VARCHAR(6) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 登录历史表
CREATE TABLE login_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    ip_address INET NOT NULL,
    user_agent TEXT,
    login_successful BOOLEAN NOT NULL,
    failure_reason VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **API端点设计**
```python
# API端点实现
@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """用户注册"""
    # 检查用户是否已存在
    existing_user = await get_user_by_email(user_data.email, db)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 创建新用户
    hashed_password = PasswordService.hash_password(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # 发送验证邮件
    await send_verification_email(user.email, user.email_verify_token)
    
    return UserResponse.from_orm(user)

@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginCredentials,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    # 记录登录尝试
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent")
    
    try:
        # 验证用户
        user = await auth_service.authenticate_user(credentials.email, credentials.password)
        if not user:
            await record_login_attempt(credentials.email, ip_address, False, "Invalid credentials")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # 检查账户状态
        if not user.is_active:
            raise HTTPException(status_code=401, detail="Account disabled")
        
        if not user.email_verified:
            raise HTTPException(status_code=401, detail="Please verify your email first")
        
        # 生成tokens
        tokens = await auth_service.create_tokens(user)
        
        # 记录成功登录
        await record_login_attempt(user.email, ip_address, True)
        
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        user.failed_login_attempts = 0
        await db.commit()
        
        return TokenResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_type=tokens.token_type,
            expires_in=tokens.expires_in,
            user=UserResponse.from_orm(user)
        )
        
    except HTTPException as e:
        await record_login_attempt(credentials.email, ip_address, False, str(e.detail))
        raise

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest
):
    """刷新访问token"""
    tokens = await auth_service.refresh_access_token(refresh_data.refresh_token)
    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
        expires_in=tokens.expires_in
    )

@router.post("/logout")
async def logout(
    logout_data: LogoutRequest,
    current_user: User = Depends(get_current_user)
):
    """用户登出"""
    success = await auth_service.revoke_token(logout_data.refresh_token)
    return {"message": "Logged out successfully", "success": success}
```

### **安全特性**

#### **密码安全**
- ✅ **bcrypt哈希**: 使用bcrypt进行密码哈希，防彩虹表攻击
- ✅ **盐值随机**: 每个密码使用不同的随机盐值
- ✅ **强度要求**: 密码长度和复杂度要求
- ✅ **防暴力破解**: 失败次数限制和账户锁定

#### **Token安全**
- ✅ **双token机制**: 短期access token + 长期refresh token
- ✅ **token撤销**: refresh token可以被主动撤销
- ✅ **签名验证**: JWT签名防篡改
- ✅ **过期控制**: 合理的token过期时间

#### **会话安全**
- ✅ **IP追踪**: 记录登录IP地址
- ✅ **设备识别**: 基于User-Agent的设备识别
- ✅ **异常检测**: 异常登录行为检测
- ✅ **审计日志**: 完整的认证操作日志

### **渐进式增强计划**

#### **Phase 1: 基础认证** (立即实现)
```python
✅ 用户注册/登录/登出
✅ JWT token生成和验证
✅ 密码安全哈希存储
✅ 基础的用户权限检查
```

#### **Phase 2: 安全增强** (后续迭代)
```python
🔄 邮箱验证机制
🔄 密码重置功能
🔄 登录失败锁定
🔄 双因素认证(TOTP)
```

#### **Phase 3: 高级功能** (可选实现)
```python
🔮 社交登录集成
🔮 单点登录(SSO)
🔮 设备管理
🔮 会话管理
```

### **未来升级路径**

设计抽象接口，保留向Cognito或其他认证服务迁移的可能：

```python
# 抽象认证接口
class AbstractAuthProvider:
    async def register(self, user_data: UserCreate) -> User: ...
    async def login(self, credentials: LoginCredentials) -> TokenPair: ...
    async def refresh_token(self, refresh_token: str) -> TokenPair: ...
    async def revoke_token(self, token: str) -> bool: ...
    async def verify_email(self, token: str) -> bool: ...
    async def reset_password(self, email: str) -> bool: ...

# 当前实现
class JWTAuthProvider(AbstractAuthProvider):
    # JWT + 本地数据库实现

# 未来可选实现
class CognitoAuthProvider(AbstractAuthProvider):
    # AWS Cognito实现 (如果需要)
    
class Auth0Provider(AbstractAuthProvider):
    # Auth0实现 (如果需要)
```

这样的设计确保了当前实现的简单性，同时为未来的扩展保留了灵活性。

---

### API设计

#### **认证授权 API**
```typescript
// 用户认证
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
POST   /api/v1/auth/refresh
GET    /api/v1/auth/me
POST   /api/v1/auth/verify-email
POST   /api/v1/auth/forgot-password
POST   /api/v1/auth/reset-password
PUT    /api/v1/auth/change-password
```

#### **用户管理 API**
```typescript
// 用户资料
GET    /api/v1/users/profile
PUT    /api/v1/users/profile
POST   /api/v1/users/avatar
GET    /api/v1/users/preferences
PUT    /api/v1/users/preferences
GET    /api/v1/users/usage-stats
GET    /api/v1/users/history
DELETE /api/v1/users/history/{id}
```

#### **AI服务 API**
```typescript
// 工具识别
POST   /api/v1/ai/tools/identify        // 上传图片识别工具
GET    /api/v1/ai/tools/history         // 获取识别历史
GET    /api/v1/ai/tools/{id}           // 获取单个识别结果
DELETE /api/v1/ai/tools/{id}           // 删除识别记录
POST   /api/v1/ai/tools/{id}/feedback  // 提供用户反馈

// 项目分析
POST   /api/v1/ai/projects/analyze     // 分析DIY项目
GET    /api/v1/ai/projects/history     // 获取分析历史
GET    /api/v1/ai/projects/{id}        // 获取单个分析结果
PUT    /api/v1/ai/projects/{id}        // 更新项目状态
DELETE /api/v1/ai/projects/{id}        // 删除分析记录
POST   /api/v1/ai/projects/{id}/rate   // 项目评价
```

#### **产品服务 API**
```typescript
// 产品浏览
GET    /api/v1/products                // 产品列表(支持搜索、过滤、排序)
GET    /api/v1/products/{id}           // 产品详情
GET    /api/v1/products/categories     // 产品分类
GET    /api/v1/products/brands         // 品牌列表
GET    /api/v1/products/merchants      // 商家列表
POST   /api/v1/products/{id}/view      // 记录浏览
POST   /api/v1/products/{id}/click     // 记录点击
GET    /api/v1/products/recommendations // 个性化推荐
```

#### **管理员 API**
```typescript
// 产品管理
GET    /api/v1/admin/products          // 管理产品列表
POST   /api/v1/admin/products          // 创建产品
PUT    /api/v1/admin/products/{id}     // 更新产品
DELETE /api/v1/admin/products/{id}     // 删除产品
POST   /api/v1/admin/products/import   // 批量导入
POST   /api/v1/admin/products/sync     // 同步价格信息

// 用户管理
GET    /api/v1/admin/users             // 用户列表
GET    /api/v1/admin/users/{id}        // 用户详情
PUT    /api/v1/admin/users/{id}        // 更新用户
PUT    /api/v1/admin/users/{id}/type   // 变更用户类型
POST   /api/v1/admin/users/{id}/disable // 禁用用户

// 系统管理
GET    /api/v1/admin/analytics         // 系统统计
GET    /api/v1/admin/configs           // 系统配置
PUT    /api/v1/admin/configs/{key}     // 更新配置
GET    /api/v1/admin/logs              // 审计日志
```

---

## 🎨 前端架构设计

### 项目结构
```
frontend/
├── src/
│   ├── main.ts                    # 应用入口
│   ├── App.vue                    # 根组件
│   ├── components/                # 通用组件
│   │   ├── layout/               # 布局组件
│   │   │   ├── AppHeader.vue
│   │   │   ├── AppSidebar.vue
│   │   │   ├── AppFooter.vue
│   │   │   └── AppBreadcrumb.vue
│   │   ├── forms/                # 表单组件
│   │   │   ├── ImageUploader.vue
│   │   │   ├── FormField.vue
│   │   │   └── SearchBox.vue
│   │   ├── ui/                   # UI组件
│   │   │   ├── LoadingSpinner.vue
│   │   │   ├── EmptyState.vue
│   │   │   ├── ConfirmDialog.vue
│   │   │   └── ToastNotification.vue
│   │   └── business/             # 业务组件
│   │       ├── ProductCard.vue
│   │       ├── ToolResult.vue
│   │       ├── ProjectAnalysis.vue
│   │       └── UserAvatar.vue
│   ├── views/                    # 页面组件
│   │   ├── auth/                 # 认证页面
│   │   │   ├── LoginView.vue
│   │   │   ├── RegisterView.vue
│   │   │   └── ForgotPasswordView.vue
│   │   ├── dashboard/            # 仪表板
│   │   │   ├── DashboardView.vue
│   │   │   └── ProfileView.vue
│   │   ├── tools/                # 工具识别
│   │   │   ├── ToolIdentificationView.vue
│   │   │   ├── ToolHistoryView.vue
│   │   │   └── ToolResultView.vue
│   │   ├── projects/             # 项目分析
│   │   │   ├── ProjectAnalysisView.vue
│   │   │   ├── ProjectHistoryView.vue
│   │   │   └── ProjectDetailView.vue
│   │   ├── products/             # 产品浏览
│   │   │   ├── ProductListView.vue
│   │   │   ├── ProductDetailView.vue
│   │   │   └── ProductCategoryView.vue
│   │   └── admin/                # 管理员页面
│   │       ├── AdminDashboardView.vue
│   │       ├── ProductManagementView.vue
│   │       ├── UserManagementView.vue
│   │       └── SystemConfigView.vue
│   ├── stores/                   # Pinia状态管理
│   │   ├── auth.ts              # 认证状态
│   │   ├── user.ts              # 用户信息
│   │   ├── products.ts          # 产品数据
│   │   ├── tools.ts             # 工具识别
│   │   ├── projects.ts          # 项目分析
│   │   └── app.ts               # 应用全局状态
│   ├── composables/             # 组合式函数
│   │   ├── useAuth.ts           # 认证逻辑
│   │   ├── useApi.ts            # API调用
│   │   ├── useFileUpload.ts     # 文件上传
│   │   ├── usePermission.ts     # 权限检查
│   │   └── useLocalStorage.ts   # 本地存储
│   ├── api/                     # API客户端
│   │   ├── client.ts            # HTTP客户端配置
│   │   ├── auth.ts              # 认证API
│   │   ├── products.ts          # 产品API
│   │   ├── tools.ts             # 工具识别API
│   │   ├── projects.ts          # 项目分析API
│   │   └── admin.ts             # 管理员API
│   ├── router/                  # 路由配置
│   │   ├── index.ts             # 主路由
│   │   ├── guards.ts            # 路由守卫
│   │   └── routes/              # 路由模块
│   │       ├── auth.ts
│   │       ├── dashboard.ts
│   │       ├── tools.ts
│   │       ├── projects.ts
│   │       ├── products.ts
│   │       └── admin.ts
│   ├── utils/                   # 工具函数
│   │   ├── request.ts           # 请求封装
│   │   ├── storage.ts           # 存储工具
│   │   ├── validation.ts        # 表单验证
│   │   ├── format.ts            # 格式化工具
│   │   └── constants.ts         # 常量定义
│   ├── types/                   # TypeScript类型
│   │   ├── api.ts               # API类型
│   │   ├── user.ts              # 用户类型
│   │   ├── product.ts           # 产品类型
│   │   └── common.ts            # 通用类型
│   ├── locales/                 # 国际化
│   │   ├── index.ts             # i18n配置
│   │   ├── en.ts                # 英文
│   │   └── zh.ts                # 中文
│   ├── styles/                  # 样式文件
│   │   ├── main.scss            # 主样式
│   │   ├── variables.scss       # 变量定义
│   │   ├── mixins.scss          # 混合器
│   │   └── components.scss      # 组件样式
│   └── assets/                  # 静态资源
│       ├── images/
│       ├── icons/
│       └── fonts/
├── public/                      # 公共文件
├── package.json
├── vite.config.ts
├── tsconfig.json
└── tailwind.config.js          # Tailwind CSS配置
```

### 状态管理设计
```typescript
// stores/auth.ts - 认证状态
export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    token: null,
    refreshToken: null,
    isAuthenticated: false,
    permissions: [],
    loginTime: null
  }),
  
  getters: {
    isAdmin: (state) => state.user?.userType === 'admin',
    isPremium: (state) => ['premium', 'admin'].includes(state.user?.userType || ''),
    hasPermission: (state) => (permission: string) => 
      state.permissions.includes(permission),
    userQuota: (state) => getUserQuota(state.user?.userType)
  },
  
  actions: {
    async login(credentials: LoginCredentials),
    async register(userData: RegisterData),
    async logout(),
    async refreshAuth(),
    async updateProfile(data: ProfileData),
    clearAuth()
  }
})

// stores/products.ts - 产品状态
export const useProductsStore = defineStore('products', {
  state: (): ProductsState => ({
    products: [],
    categories: [],
    brands: [],
    merchants: [],
    filters: defaultFilters,
    pagination: defaultPagination,
    loading: false,
    selectedProduct: null
  }),
  
  getters: {
    filteredProducts: (state) => applyFilters(state.products, state.filters),
    categoryTree: (state) => buildCategoryTree(state.categories),
    featuredProducts: (state) => state.products.filter(p => p.isFeatured)
  },
  
  actions: {
    async fetchProducts(params?: ProductParams),
    async fetchProductById(id: number),
    async fetchCategories(),
    async searchProducts(query: string),
    setFilters(filters: ProductFilters),
    trackProductView(productId: number),
    trackProductClick(productId: number)
  }
})
```

---

## 🔧 后端架构设计

### 项目结构
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # 应用入口
│   ├── config.py                # 配置管理
│   ├── database.py              # 数据库连接
│   ├── dependencies.py          # 依赖注入
│   ├── models/                  # 数据模型
│   │   ├── __init__.py
│   │   ├── base.py             # 基础模型类
│   │   ├── user.py             # 用户模型
│   │   ├── product.py          # 产品模型
│   │   ├── tool_identification.py
│   │   ├── project_analysis.py
│   │   └── audit_log.py
│   ├── schemas/                 # Pydantic模式
│   │   ├── __init__.py
│   │   ├── base.py             # 基础模式
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── tool.py
│   │   ├── project.py
│   │   └── response.py         # 响应模式
│   ├── api/                     # API路由
│   │   ├── __init__.py
│   │   ├── deps.py             # API依赖
│   │   └── v1/                 # v1版本API
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── products.py
│   │       ├── tools.py
│   │       ├── projects.py
│   │       └── admin.py
│   ├── services/                # 业务逻辑服务
│   │   ├── __init__.py
│   │   ├── auth_service.py     # 认证服务
│   │   ├── user_service.py     # 用户服务
│   │   ├── product_service.py  # 产品服务
│   │   ├── ai_service.py       # AI服务
│   │   ├── file_service.py     # 文件服务
│   │   ├── notification_service.py
│   │   └── analytics_service.py
│   ├── core/                    # 核心模块
│   │   ├── __init__.py
│   │   ├── security.py         # 安全工具
│   │   ├── permissions.py      # 权限系统
│   │   ├── exceptions.py       # 异常处理
│   │   ├── middleware.py       # 中间件
│   │   └── logging.py          # 日志配置
│   ├── utils/                   # 工具模块
│   │   ├── __init__.py
│   │   ├── image_processor.py  # 图像处理
│   │   ├── validators.py       # 验证器
│   │   ├── helpers.py          # 辅助函数
│   │   └── cache.py            # 缓存工具
│   └── workers/                 # 后台任务
│       ├── __init__.py
│       ├── celery_app.py       # Celery配置
│       ├── ai_tasks.py         # AI处理任务
│       └── maintenance_tasks.py # 维护任务
├── migrations/                  # 数据库迁移
├── tests/                       # 测试代码
│   ├── __init__.py
│   ├── conftest.py             # 测试配置
│   ├── test_auth.py
│   ├── test_products.py
│   └── test_ai_services.py
├── scripts/                     # 脚本文件
│   ├── init_db.py              # 初始化数据库
│   ├── create_admin.py         # 创建管理员
│   └── migrate_data.py         # 数据迁移
├── requirements/                # 依赖文件
│   ├── base.txt                # 基础依赖
│   ├── dev.txt                 # 开发依赖
│   └── prod.txt                # 生产依赖
├── .env.example                # 环境变量示例
├── pyproject.toml              # 项目配置
└── README.md
```

### 服务层设计
```python
# services/ai_service.py - AI服务
class AIService:
    def __init__(self, openai_client: OpenAI):
        self.openai_client = openai_client
    
    async def identify_tool(
        self, 
        image_data: bytes, 
        user_id: int
    ) -> ToolIdentificationResult:
        """识别工具图像"""
        # 图像预处理
        processed_image = await self._preprocess_image(image_data)
        
        # 调用OpenAI Vision API
        result = await self._call_vision_api(processed_image)
        
        # 保存识别结果
        identification = await self._save_identification(result, user_id)
        
        # 生成产品推荐
        recommendations = await self._generate_recommendations(result)
        
        return ToolIdentificationResult(
            identification=identification,
            recommendations=recommendations
        )
    
    async def analyze_project(
        self, 
        images: List[bytes], 
        description: str,
        user_preferences: dict,
        user_id: int
    ) -> ProjectAnalysisResult:
        """分析DIY项目"""
        # 多图像处理
        processed_images = await self._preprocess_images(images)
        
        # 构建分析prompt
        prompt = self._build_analysis_prompt(description, user_preferences)
        
        # AI分析
        analysis = await self._call_analysis_api(processed_images, prompt)
        
        # 解析结果并验证
        parsed_result = await self._parse_analysis_result(analysis)
        
        # 保存分析结果
        project_analysis = await self._save_analysis(parsed_result, user_id)
        
        return ProjectAnalysisResult(
            analysis=project_analysis,
            recommendations=parsed_result.recommendations
        )

# services/user_service.py - 用户服务
class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def check_quota(
        self, 
        user_id: int, 
        service_type: str
    ) -> QuotaCheckResult:
        """检查用户配额"""
        user = await self._get_user(user_id)
        quota_config = get_quota_config(user.user_type)
        
        if quota_config[service_type]['daily_limit'] == -1:
            return QuotaCheckResult(allowed=True, remaining=-1)
        
        usage_today = await self._get_daily_usage(user_id, service_type)
        remaining = quota_config[service_type]['daily_limit'] - usage_today
        
        return QuotaCheckResult(
            allowed=remaining > 0,
            remaining=max(0, remaining)
        )
    
    async def record_usage(
        self, 
        user_id: int, 
        service_type: str
    ) -> None:
        """记录服务使用"""
        today = date.today()
        
        # 原子性操作：增加使用次数
        await self.db.execute(
            text("""
                INSERT INTO user_quotas (user_id, service_type, usage_date, usage_count)
                VALUES (:user_id, :service_type, :usage_date, 1)
                ON CONFLICT (user_id, service_type, usage_date)
                DO UPDATE SET usage_count = user_quotas.usage_count + 1
            """),
            {
                "user_id": user_id,
                "service_type": service_type,
                "usage_date": today
            }
        )
        await self.db.commit()
```

### 中间件设计
```python
# core/middleware.py - 自定义中间件
class AuthenticationMiddleware:
    """JWT认证中间件"""
    
    async def __call__(self, request: Request, call_next):
        # 获取token
        token = self._extract_token(request)
        
        if token:
            try:
                # 验证token
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                user_id = payload.get("sub")
                
                # 检查token是否被撤销
                if not await self._is_token_revoked(payload.get("jti")):
                    request.state.user_id = user_id
                    request.state.user = await get_user_by_id(user_id)
            except JWTError:
                pass  # 无效token，继续处理但不设置用户信息
        
        response = await call_next(request)
        return response

class RateLimitMiddleware:
    """API限流中间件"""
    
    def __init__(self, calls: int = 100, period: int = 3600):
        self.calls = calls
        self.period = period
        self.cache = {}
    
    async def __call__(self, request: Request, call_next):
        client_ip = self._get_client_ip(request)
        
        # 检查限流
        if await self._is_rate_limited(client_ip):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded"
            )
        
        # 记录请求
        await self._record_request(client_ip)
        
        response = await call_next(request)
        return response

class LoggingMiddleware:
    """请求日志中间件"""
    
    async def __call__(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        # 记录访问日志
        logger.info(
            f"{request.method} {request.url.path} - "
            f"{response.status_code} - {process_time:.3f}s"
        )
        
        return response
```

---

## 🚀 实施计划

### Phase 1: 项目初始化 (1天)
#### **环境搭建**
- 创建项目目录结构
- 设置Python虚拟环境和Node.js环境
- 配置开发工具 (VSCode, Git, Docker)
- 设置代码格式化 (Prettier, Black, isort)

#### **基础配置**
- 配置FastAPI项目基础结构
- 设置Vue 3项目脚手架
- 配置数据库连接 (PostgreSQL + SQLAlchemy)
- 设置基础的Docker容器

#### **开发流程**
- 配置Git工作流 (main/develop分支)
- 设置CI/CD基础配置 (GitHub Actions)
- 创建开发文档模板

### Phase 2: 核心后端开发 (2-3天)
#### **认证系统** (0.5天)
```python
# 实现JWT认证
- 用户注册/登录/登出
- Token刷新机制
- 密码重置流程
- 邮箱验证功能
```

#### **数据模型和API** (1天)
```python
# 创建核心数据模型
- User, Product, ToolIdentification, ProjectAnalysis模型
- 数据库迁移文件
- 基础CRUD操作
- 数据验证和序列化
```

#### **AI服务集成** (1天)
```python
# OpenAI API集成
- 图像预处理服务
- 工具识别API
- 项目分析API
- 错误处理和重试机制
```

#### **权限和配额系统** (0.5天)
```python
# 实现用户权限控制
- 基于角色的权限系统
- 使用配额检查和记录
- API限流机制
```

### Phase 3: 前端开发 (2天)
#### **基础架构** (0.5天)
```typescript
// 项目架构搭建
- Vue 3 + TypeScript + Vite配置
- Element Plus集成
- Pinia状态管理设置
- 路由配置和守卫
```

#### **核心页面** (1天)
```vue
<!-- 主要页面实现 -->
- 用户认证页面 (登录/注册)
- 工具识别界面
- 项目分析界面
- 产品浏览页面
```

#### **管理界面** (0.5天)
```vue
<!-- 管理员功能 -->
- 产品管理界面
- 用户管理界面
- 系统统计仪表板
```

### Phase 4: 集成测试和优化 (1天)
#### **功能测试**
- API端点集成测试
- 前后端数据流测试
- 用户权限测试
- 文件上传测试

#### **性能优化**
- 数据库查询优化
- 图像处理优化
- 前端代码分割
- API响应缓存

#### **安全加固**
- SQL注入防护
- XSS攻击防护
- CSRF保护
- 敏感信息加密

### Phase 5: 部署和监控 (0.5天)
#### **生产部署**
- Docker容器化
- 环境变量配置
- 数据库备份策略
- SSL证书配置

#### **监控和日志**
- 应用性能监控
- 错误追踪系统
- 日志收集和分析
- 健康检查端点

---

## 🔒 安全性考虑

### **认证和授权**
```python
# JWT安全实践
- 短期访问token (15分钟)
- 长期刷新token (7天)
- Token撤销机制
- 安全的密码存储 (bcrypt)

# 权限控制
- 基于角色的访问控制 (RBAC)
- API端点权限验证
- 资源级别权限检查
- 管理员操作审计
```

### **数据保护**
```python
# 敏感数据处理
- 个人信息加密存储
- 密码不可逆哈希
- 会话数据保护
- 数据备份加密

# API安全
- 请求频率限制
- 参数验证和清理
- SQL注入防护
- XSS攻击防护
```

### **文件安全**
```python
# 文件上传安全
- 文件类型验证
- 文件大小限制
- 病毒扫描集成
- 安全的文件存储路径
```

---

## 📊 性能优化策略

### **数据库优化**
```sql
-- 索引优化
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_active ON products(is_active) WHERE is_active = true;
CREATE INDEX idx_tool_identifications_user_created ON tool_identifications(user_id, created_at);

-- 查询优化
- 使用适当的索引
- 避免N+1查询问题
- 实现数据库连接池
- 查询结果缓存
```

### **API性能**
```python
# 缓存策略
- Redis缓存热点数据
- API响应缓存
- 数据库查询结果缓存
- 静态资源CDN

# 异步处理
- 使用异步I/O (asyncio)
- 后台任务队列 (Celery)
- 图像处理异步化
- AI API调用优化
```

### **前端性能**
```typescript
// 优化策略
- 代码分割和懒加载
- 组件级别的缓存
- 图片懒加载和压缩
- 虚拟滚动列表
- PWA支持
```

---

## 🔮 未来扩展方向

### **功能扩展**
- **社区功能**: 用户项目分享、评论、评分系统
- **视频分析**: 支持视频格式的项目分析
- **AR/VR集成**: 虚拟现实项目预览
- **移动应用**: React Native或Flutter移动端
- **语音助手**: 语音指令和回答

### **AI能力增强**
- **自定义模型**: 训练专门的工具识别模型
- **实时推荐**: 基于用户行为的智能推荐
- **价格预测**: 商品价格趋势分析
- **项目难度评估**: 智能难度评估系统

### **商业功能**
- **电商集成**: 直接购买功能
- **订阅服务**: 会员订阅系统
- **广告平台**: 商家广告投放
- **数据分析**: 用户行为分析仪表板

### **技术升级**
- **微服务架构**: 服务拆分和独立部署
- **GraphQL API**: 更灵活的API查询
- **实时通信**: WebSocket实时功能
- **边缘计算**: CDN边缘函数部署

---

## 📋 开发检查清单

### **开发阶段**
- [ ] 项目结构创建完成
- [ ] 开发环境搭建完成
- [ ] 数据库设计和迁移完成
- [ ] JWT认证系统实现
- [ ] 核心API端点开发完成
- [ ] AI服务集成完成
- [ ] 前端基础架构搭建
- [ ] 主要页面功能实现
- [ ] 管理员功能开发

### **测试阶段**
- [ ] 单元测试覆盖率 > 80%
- [ ] API集成测试通过
- [ ] 前端组件测试完成
- [ ] 安全性测试通过
- [ ] 性能测试达标
- [ ] 用户接受测试完成

### **部署阶段**
- [ ] 生产环境配置完成
- [ ] Docker镜像构建成功
- [ ] 数据库迁移完成
- [ ] SSL证书配置完成
- [ ] 监控和日志系统配置
- [ ] 备份策略实施
- [ ] 文档编写完成

---

## 🎯 成功指标

### **技术指标**
- **响应时间**: API平均响应时间 < 500ms
- **可用性**: 系统可用率 > 99.9%
- **性能**: 并发用户支持 > 1000
- **安全**: 无重大安全漏洞

### **用户体验指标**
- **加载速度**: 页面首屏加载 < 2秒
- **成功率**: AI识别准确率 > 85%
- **用户满意度**: 用户评分 > 4.5/5
- **转化率**: 注册转化率 > 15%

### **业务指标**
- **用户增长**: 月活跃用户增长率 > 20%
- **使用频率**: 日均使用次数 > 2次
- **功能采用率**: 核心功能使用率 > 60%
- **用户留存**: 30天用户留存率 > 40%

---

这个项目设计方案提供了一个现代化、可扩展、安全的DIY智能助手平台架构。通过合理的技术选择、清晰的模块划分和详细的实施计划，可以构建出一个高质量的产品，满足用户需求并具备良好的可维护性和扩展性。