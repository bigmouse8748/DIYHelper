# DIY Smart Assistant 🛠️

An intelligent DIY project analysis platform that combines Vue.js frontend with FastAPI backend and AI Agent-based architecture. Upload project images and get comprehensive DIY guidance including material lists, tool recommendations, safety notes, building steps, and intelligent shopping suggestions from US retailers.

**Live Demo**: [https://cheasydiy.com](https://cheasydiy.com)

## ✨ Features

### Core Functionality
✅ **AI-Powered Image Analysis**: Intelligent project recognition and analysis  
✅ **Smart Product Recommendations**: 3 products per tool/material with real brands  
✅ **US Retailer Integration**: Direct links to Home Depot, Lowes, Amazon, Walmart  
✅ **Bilingual Support**: Complete Chinese/English localization  
✅ **Agent-Based Architecture**: Modular, scalable AI agent system  
✅ **Modern Tech Stack**: Vue 3 + TypeScript + FastAPI + Python  

### New Features 🆕
🔐 **User Authentication System**: Secure JWT-based authentication  
👤 **User Management**: Register, login, and personalized dashboard  
🔧 **Tool Identification Agent**: AI-powered tool recognition from images  
💰 **Price Scraping Service**: Real-time price comparison across retailers  
📊 **Protected Routes**: Secure access to user-specific features  
🏪 **Vuex State Management**: Centralized state management for scalability  

## 🏗️ Architecture

### Frontend Stack
- **Vue 3** with Composition API
- **TypeScript** for type safety
- **Element Plus** UI components
- **Vue I18n** for internationalization
- **Vue Router** for navigation
- **Vuex** for state management
- **Vite** for fast development

### Backend Stack
- **FastAPI** for async REST APIs
- **Python 3.11+** with virtual environment
- **Pydantic** for data validation
- **JWT** for authentication
- **CORS** middleware for cross-origin requests
- **Agent-based architecture** with BaseAgent class

### AI Integration
- **ProductRecommendationAgent** with intelligent suggestions
- **ToolIdentificationAgent** for tool recognition
- **OpenAI GPT-4 Vision API** ready for integration
- **Intelligent product matching** with US retailer integration

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and npm
- Python 3.11+
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/bigmouse8748/DIYHelper.git
cd DIYList/diy-agent-system
```

2. **Backend Setup**
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

3. **Frontend Setup**
```bash
cd frontend
npm install
```

4. **Environment Configuration**
Create `.env` file in backend directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Running the Application

1. **Start Backend Server**
```bash
cd backend
.venv\Scripts\activate
python main_simple.py
```
Backend runs on: http://localhost:8001

2. **Start Frontend Development Server**
```bash
cd frontend
npm run dev
```
Frontend runs on: http://localhost:3002 (or auto-assigned port)

## 📡 API Endpoints

### Core Endpoints
- `POST /analyze-project` - Analyzes uploaded images and returns comprehensive DIY guidance
- `POST /agent/execute` - Execute specific agent tasks
- `GET /api/test` - Health check endpoint
- `GET /agents/status` - Get status of all registered agents

### Authentication Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/refresh` - Refresh JWT token

### Tool Identification
- `POST /api/tool-identification/analyze` - Analyze tools from uploaded images
- `GET /api/tool-identification/history` - Get user's tool analysis history


## 🔧 Key Components

### AI Agents

#### ProductRecommendationAgent
- AI-powered tool and material suggestions
- Real brand recommendations (DeWalt, Milwaukee, BLACK+DECKER, etc.)
- Intelligent prioritization based on project type and budget
- Guaranteed 3 products per tool/material category

#### ToolIdentificationAgent
- Computer vision-based tool recognition
- Brand and model identification
- Safety rating assessment
- Usage recommendations

### Features

#### 🌐 Bilingual Support
- Automatic language detection from browser
- Complete UI translations in English and Chinese
- Context-aware translations for technical terms
- Language switcher with persistent selection

#### 🏪 US Retailer Integration
- Amazon product search URLs
- Home Depot product linking
- Lowes marketplace integration
- Walmart product recommendations
- Real-time price comparison

#### 🔒 Authentication System
- JWT-based secure authentication
- User registration and login
- Protected routes and API endpoints
- Session management with refresh tokens

## Development

### 📁 File Structure
```
DIYList/
├── CLAUDE.md                      # Comprehensive development documentation
├── README.md                      # Project overview (this file)
└── diy-agent-system/              # Main application
    ├── frontend/                  # Vue 3 + TypeScript frontend
    │   ├── src/
    │   │   ├── api/              # API service modules
    │   │   ├── components/       # Reusable Vue components
    │   │   ├── locales/          # i18n translations (en, zh)
    │   │   ├── router/           # Vue Router configuration
    │   │   ├── stores/           # Vuex state management
    │   │   └── views/            # Page components
    │   │       ├── Home.vue
    │   │       ├── Login.vue
    │   │       ├── Register.vue
    │   │       ├── Dashboard.vue
    │   │       └── ToolIdentification.vue
    │   └── package.json
    └── backend/                   # FastAPI + Python backend
        ├── agents/                # AI agents
        │   ├── product_recommendation_agent.py
        │   └── tool_identification_agent.py
        ├── auth/                  # Authentication modules
        │   └── auth_handler.py
        ├── core/                  # Agent base classes
        ├── models/                # Data models
        │   ├── user_models.py
        │   └── tool_models.py
        ├── services/              # Business logic services
        │   └── price_scraper.py
        ├── main_simple.py         # Main API server
        ├── main_enhanced.py       # Enhanced server with auth
        └── requirements.txt
```

### Adding New Features
1. **New Agent**: Extend `BaseAgent` in `agents/` directory
2. **Frontend Component**: Add to `src/components/` with i18n support
3. **API Endpoint**: Add to `main_simple.py` with proper error handling
4. **Translations**: Update both `locales/en.ts` and `locales/zh.ts`

### 🧪 Testing

#### Backend Agent Testing
```bash
# Test ProductRecommendationAgent
cd backend
.venv\Scripts\activate
python test_product_recommendation.py

# Test ToolIdentificationAgent
python test_tool_identification.py

# Test Price Scraper Service
python test_price_scraper.py
```

#### Frontend Testing
```bash
cd frontend
npm run test:unit    # Unit tests
npm run test:e2e     # End-to-end tests
```

## 🚢 Production Deployment

### Environment Variables (Production)
```env
# API Keys
OPENAI_API_KEY=prod_api_key

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Authentication
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30

# CORS
CORS_ORIGINS=https://yourdomain.com

# Redis (Optional)
REDIS_URL=redis://localhost:6379
```

### Build Commands
```bash
# Frontend build
cd frontend
npm run build

# Backend deployment with authentication
cd backend
uvicorn main_enhanced:app --host 0.0.0.0 --port 8001 --workers 4

# Or use simple version without auth
uvicorn main_simple:app --host 0.0.0.0 --port 8001 --workers 4
```

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build individual containers
docker build -t diy-frontend ./frontend
docker build -t diy-backend ./backend
```

### 🔒 Security Considerations
- Always use HTTPS in production
- Set strong JWT secret keys
- Enable rate limiting
- Implement proper CORS policies
- Use environment variables for sensitive data
- Regular security audits and updates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow existing code style and conventions
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR
- Keep commits atomic and well-described

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 💬 Support

- **Documentation**: See [CLAUDE.md](CLAUDE.md) for detailed development information
- **Issues**: Create an issue in the [GitHub repository](https://github.com/bigmouse8748/DIYHelper/issues)
- **Discussions**: Join our [GitHub Discussions](https://github.com/bigmouse8748/DIYHelper/discussions)

## 🌟 Roadmap

### Completed ✅
- [x] User Authentication System (JWT-based)
- [x] Database persistence (PostgreSQL on AWS RDS)
- [x] Tool Identification Feature
- [x] AWS Deployment (ECS, CloudFront, RDS)
- [x] Production-ready infrastructure

### In Progress 🚧
- [ ] Real AI API integration (GPT-4 Vision)
- [ ] User project history and favorites

### Future Plans 📋
- [ ] Social features (share projects, reviews)
- [ ] Mobile application (React Native)
- [ ] Advanced price tracking and alerts
- [ ] 3D project visualization
- [ ] Video tutorial integration
- [ ] Amazon Cognito integration
- [ ] Real-time collaboration features

---

**Built with ❤️ using modern web technologies and AI-powered recommendations**

⭐ Star us on [GitHub](https://github.com/bigmouse8748/DIYHelper) if you find this project helpful!