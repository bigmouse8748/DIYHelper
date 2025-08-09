# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**DIY Smart Assistant** is a full-stack intelligent DIY project analysis platform that combines Vue.js frontend with FastAPI backend and an AI Agent-based architecture. The system analyzes uploaded project images and provides comprehensive DIY guidance including material lists, tool recommendations, safety notes, building steps, and intelligent shopping suggestions from US retailers.

## Architecture Overview

### Modern Technology Stack

**Frontend (Vue 3 + TypeScript):**
- Vue 3 with Composition API
- TypeScript for type safety
- Element Plus UI framework
- Vue I18n for bilingual support (Chinese/English)
- Vite for development and build

**Backend (FastAPI + Python):**
- FastAPI for async API endpoints
- Python 3.11+ with virtual environment
- Agent-based architecture with BaseAgent class
- Pydantic for data validation
- CORS enabled for cross-origin requests

**AI Integration:**
- ProductRecommendationAgent with AI-powered suggestions
- OpenAI GPT-4 Vision API for image analysis (configured but uses mock data)
- Intelligent product matching with US retailer integration

## Development Environment Setup

### Prerequisites
- Node.js 16+ and npm
- Python 3.11+
- Git

### Frontend Setup
```bash
cd diy-agent-system/frontend
npm install
```

### Backend Setup
```bash
cd diy-agent-system/backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install fastapi uvicorn python-multipart pydantic python-dotenv
```

### Environment Configuration
Create `.env` file in backend directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

## Running the Application

### Start Backend Server
```bash
cd diy-agent-system/backend
.venv\Scripts\activate
python main_simple.py
```
Backend runs on: http://localhost:8001

### Start Frontend Development Server
```bash
cd diy-agent-system/frontend
npm run dev
```
Frontend runs on: http://localhost:3002 (or auto-assigned port)

## Core Features Implementation

### 1. Intelligent Product Recommendations

**ProductRecommendationAgent (`agents/product_recommendation_agent.py`):**
- AI-powered tool and material suggestions
- Real brand recommendations (DeWalt, Milwaukee, BLACK+DECKER, etc.)
- Intelligent prioritization based on:
  - Project type (woodworking, electronics, crafts)
  - Budget level (entry-level to professional)
  - User skill level and project complexity
- Integration with US retailers: Amazon, Home Depot, Lowes, Walmart

**Key Methods:**
- `execute()`: Main recommendation logic
- `_get_ai_recommendations()`: AI-powered brand/model suggestions
- `_search_products()`: Generate real product links
- `_build_recommendation_prompt()`: LLM prompt engineering (ready for real API)

### 2. Bilingual Support (Chinese/English)

**Vue I18n Implementation:**
- Automatic language detection from browser
- Complete UI translations in `locales/en.ts` and `locales/zh.ts`
- Language switcher component with persistent selection
- Context-aware translations for technical terms

**Key Translation Areas:**
- Project analysis results
- Material and tool specifications
- Shopping recommendations and tips
- Safety notes and building steps

### 3. Agent-Based Architecture

**Core Agent System (`core/agent_base.py`):**
- `BaseAgent`: Abstract base class for all agents
- `AgentTask`: Task model with validation
- `AgentResult`: Standardized result format
- `AgentManager`: Orchestrates multiple agents

### 4. Modern Vue 3 Frontend

**Key Components:**
- `AnalysisResults.vue`: Main results display with bilingual support
- `LanguageSwitcher.vue`: Language toggle with Element Plus icons
- `ImageUpload.vue`: Drag-and-drop image upload interface

## API Endpoints

### Main Endpoints
- `POST /analyze-project`: Analyzes uploaded images and returns comprehensive DIY guidance
- `POST /agent/execute`: Execute specific agent tasks
- `GET /api/test`: Health check endpoint
- `GET /agents/status`: Get status of all registered agents

### Request/Response Format

**Analyze Project Request:**
```
Content-Type: multipart/form-data
- images: File[] (up to 4 images, JPG/PNG)
- description: string (optional project description)
- project_type: string (woodworking, electronics, etc.)
- budget_range: string (under50, 50to150, 150to300, etc.)
```

**Response Structure:**
```json
{
  "success": true,
  "results": [
    {
      "data": {
        "comprehensive_analysis": {
          "project_name": "DIY Project Name",
          "description": "Project analysis...",
          "materials": [...],
          "tools": [...],
          "difficulty_level": "medium",
          "estimated_time": "4-6 hours",
          "safety_notes": [...],
          "steps": [...]
        }
      }
    },
    {
      "data": {
        "assessed_results": [...],
        "overall_recommendations": {
          "total_products_assessed": 5,
          "average_quality_score": 4.4,
          "best_products": [...],
          "shopping_tips": [...],
          "quality_distribution": {...}
        }
      }
    }
  ]
}
```

## File Structure

```
DIYList/
├── diy-agent-system/
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── components/
│   │   │   │   ├── AnalysisResults.vue
│   │   │   │   ├── LanguageSwitcher.vue
│   │   │   │   └── ImageUpload.vue
│   │   │   ├── locales/
│   │   │   │   ├── en.ts
│   │   │   │   └── zh.ts
│   │   │   ├── i18n/
│   │   │   │   └── index.ts
│   │   │   └── main.ts
│   │   ├── package.json
│   │   └── vite.config.ts
│   └── backend/
│       ├── agents/
│       │   ├── __init__.py
│       │   └── product_recommendation_agent.py
│       ├── core/
│       │   ├── __init__.py
│       │   └── agent_base.py
│       ├── utils/
│       │   └── config.py
│       ├── main_simple.py
│       ├── requirements.txt
│       └── .env
├── index.html (legacy)
├── script.js (legacy) 
├── style.css (legacy)
├── server.js (legacy Node.js server)
└── CLAUDE.md
```

## Development Workflow

### Testing the System
```bash
# Test ProductRecommendationAgent
cd diy-agent-system/backend
.venv\Scripts\activate
python -c "
import asyncio
from agents.product_recommendation_agent import ProductRecommendationAgent
# ... test code
"
```

### Adding New Features
1. **New Agent**: Extend `BaseAgent` in `agents/` directory
2. **Frontend Component**: Add to `src/components/` with i18n support
3. **API Endpoint**: Add to `main_simple.py` with proper error handling
4. **Translations**: Update both `locales/en.ts` and `locales/zh.ts`

## Key Integration Points

### AI/LLM Integration
- Framework ready for OpenAI GPT-4, Anthropic Claude, or other LLMs
- Prompt engineering templates in `ProductRecommendationAgent`
- Structured AI response parsing
- Fallback mechanisms for API failures

### US Retailer Integration
- Amazon product search URLs
- Home Depot product linking
- Lowes marketplace integration  
- Walmart product recommendations
- Real product images via Unsplash API

### Cross-Origin Resource Sharing (CORS)
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Error Handling & Logging

- Comprehensive error handling in all API endpoints
- Python logging configured for debugging
- Frontend error states with user-friendly messages
- Graceful degradation when services are unavailable

## Future Enhancements

### Ready for Implementation:
1. **Real LLM Integration**: Replace mock responses with actual AI API calls
2. **User Authentication**: Add user accounts and project history
3. **Real-time Product Pricing**: Live price comparison across retailers
4. **Advanced Image Analysis**: Multi-angle project analysis
5. **Community Features**: Share projects and reviews

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
cd diy-agent-system/frontend
npm run build

# Backend deployment
cd diy-agent-system/backend
uvicorn main_simple:app --host 0.0.0.0 --port 8001 --workers 4
```

## Troubleshooting

### Common Issues:
1. **Port Conflicts**: Frontend auto-selects available ports (3000, 3001, 3002, etc.)
2. **CORS Errors**: Add your domain to allowed origins in backend
3. **Missing Dependencies**: Ensure virtual environment is activated
4. **Icon Import Errors**: Use existing Element Plus icons (Globe → Setting)

### Debug Commands:
```bash
# Check backend status
curl http://localhost:8001/api/test

# Check agent status
curl http://localhost:8001/agents/status

# Frontend development
npm run dev -- --host 0.0.0.0 --port 3002
```

This system represents a modern, scalable architecture ready for production deployment with intelligent AI-powered recommendations and comprehensive bilingual support.