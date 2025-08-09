# DIY Smart Assistant

An intelligent DIY project analysis platform that combines Vue.js frontend with FastAPI backend and AI Agent-based architecture. Upload project images and get comprehensive DIY guidance including material lists, tool recommendations, safety notes, building steps, and intelligent shopping suggestions from US retailers.

## Features

✅ **AI-Powered Image Analysis**: Intelligent project recognition and analysis  
✅ **Smart Product Recommendations**: 3 products per tool/material with real brands  
✅ **US Retailer Integration**: Direct links to Home Depot, Lowes, Amazon  
✅ **Bilingual Support**: Complete Chinese/English localization  
✅ **Agent-Based Architecture**: Modular, scalable AI agent system  
✅ **Modern Tech Stack**: Vue 3 + TypeScript + FastAPI + Python  

## Architecture

- **Frontend**: Vue 3 + TypeScript + Element Plus + Vue I18n
- **Backend**: FastAPI + Python 3.11+ + Agent-based system
- **AI Integration**: ProductRecommendationAgent with intelligent suggestions
- **Database**: SQLite for development
- **Containerization**: Docker with Docker Compose

## Quick Start

### Prerequisites
- Node.js 16+ and npm
- Python 3.11+
- Git

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
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

### API Endpoints

- `POST /analyze-project` - Analyzes uploaded images and returns comprehensive DIY guidance
- `GET /api/test` - Health check endpoint
- `GET /agents/status` - Get status of all registered agents

## Technology Stack

### Frontend
- **Vue 3** with Composition API
- **TypeScript** for type safety
- **Element Plus** UI framework
- **Vue I18n** for internationalization
- **Vite** for development and build

### Backend
- **FastAPI** for async API endpoints
- **Python 3.11+** with virtual environment
- **Pydantic** for data validation
- **Agent-based architecture** with BaseAgent class

### AI Integration
- **ProductRecommendationAgent** with AI-powered suggestions
- **OpenAI GPT-4 Vision API** ready for integration
- **Intelligent product matching** with US retailer integration

## Key Components

### ProductRecommendationAgent
- AI-powered tool and material suggestions
- Real brand recommendations (DeWalt, Milwaukee, BLACK+DECKER, etc.)
- Intelligent prioritization based on project type and budget
- Guaranteed 3 products per tool/material category

### Bilingual Support
- Automatic language detection from browser
- Complete UI translations in English and Chinese
- Context-aware translations for technical terms
- Language switcher with persistent selection

### US Retailer Integration
- Amazon product search URLs
- Home Depot product linking
- Lowes marketplace integration
- Walmart product recommendations

## Development

### File Structure
```
DIYList/
├── CLAUDE.md              # Comprehensive development documentation
├── README.md              # Project overview (this file)
└── diy-agent-system/      # Main application
    ├── frontend/           # Vue 3 + TypeScript frontend
    │   ├── src/
    │   │   ├── components/
    │   │   ├── locales/    # i18n translations
    │   │   └── views/
    │   └── package.json
    └── backend/            # FastAPI + Python backend
        ├── agents/         # AI agents
        ├── core/          # Agent base classes
        ├── main_simple.py  # Main API server
        └── requirements.txt
```

### Adding New Features
1. **New Agent**: Extend `BaseAgent` in `agents/` directory
2. **Frontend Component**: Add to `src/components/` with i18n support
3. **API Endpoint**: Add to `main_simple.py` with proper error handling
4. **Translations**: Update both `locales/en.ts` and `locales/zh.ts`

### Testing
```bash
# Test ProductRecommendationAgent
cd backend
.venv\Scripts\activate
python -c "
import asyncio
from agents.product_recommendation_agent import ProductRecommendationAgent
# ... test code
"
```

## Production Deployment

### Environment Variables (Production)
```env
OPENAI_API_KEY=prod_api_key
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
CORS_ORIGINS=https://yourdomain.com
```

### Build Commands
```bash
# Frontend build
cd frontend
npm run build

# Backend deployment
cd backend
uvicorn main_simple:app --host 0.0.0.0 --port 8001 --workers 4
```

### Docker Deployment
```bash
docker-compose up --build
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For detailed development information, see [CLAUDE.md](CLAUDE.md).

For issues and feature requests, please create an issue in the repository.

---

**Built with ❤️ using modern web technologies and AI-powered recommendations**