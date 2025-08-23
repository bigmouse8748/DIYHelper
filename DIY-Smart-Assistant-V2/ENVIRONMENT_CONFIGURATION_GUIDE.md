# 🔧 Environment Configuration Guide - DIY Smart Assistant V2

## 📋 Overview

This guide explains how to achieve seamless integration between local development and AWS production deployment through proper environment configuration management.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Local Development                        │
├─────────────────────────────────────────────────────────────┤
│  Backend:  http://localhost:8000                            │
│  Frontend: http://localhost:8080                            │
│  Database: SQLite (./diy_assistant.db)                      │
│  Debug:    Enabled                                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
                    [Git Push to aws-deployment]
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     AWS Production                           │
├─────────────────────────────────────────────────────────────┤
│  Backend:  https://api.cheasydiy.com                        │
│  Frontend: https://cheasydiy.com                            │
│  Database: PostgreSQL (AWS RDS)                             │
│  Debug:    Disabled                                         │
└─────────────────────────────────────────────────────────────┘
```

## 🔑 Key Configuration Differences

| Configuration | Local Development | AWS Production |
|--------------|-------------------|----------------|
| **Backend Port** | 8000 | 8000 (internal), 443 (external via ALB) |
| **Frontend Port** | 8080 | 80 (internal), 443 (external via CloudFront) |
| **API URL** | http://localhost:8000 | https://api.cheasydiy.com |
| **Database** | SQLite | PostgreSQL (RDS) |
| **CORS Origins** | localhost:8080,8086,5173 | cheasydiy.com |
| **Debug Mode** | true | false |
| **Secret Key** | Development key | Production secret (AWS Secrets Manager) |
| **File Storage** | Local filesystem | EFS or S3 |
| **Redis Cache** | Optional (local) | ElastiCache |

## 🚀 Local Development Setup

### 1. Backend Configuration

Create `backend/.env` from template:
```bash
cd DIY-Smart-Assistant-V2/backend
cp .env.example .env
# Or use the pre-configured local file:
cp .env.local .env
```

Key local settings:
```env
DATABASE_URL="sqlite:///./diy_assistant.db"
DEBUG=true
ALLOWED_ORIGINS="http://localhost:8080,http://localhost:8086,http://localhost:5173"
BASE_URL="http://localhost:8000"
```

### 2. Frontend Configuration

Create `frontend/.env.local`:
```bash
cd DIY-Smart-Assistant-V2/frontend
cp .env.example .env.local
```

Key local settings:
```env
VITE_API_URL=http://localhost:8000
VITE_ENABLE_DEBUG=true
```

### 3. Running Locally

```bash
# Terminal 1: Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements/base.txt
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm install
npm run dev  # Runs on port 8080
```

## ☁️ AWS Production Configuration

### 1. Environment Variables in ECS Task Definition

The backend receives configuration through ECS task environment variables:

```json
{
  "environment": [
    {"name": "DATABASE_URL", "value": "postgresql://user:pass@rds-host:5432/db"},
    {"name": "DEBUG", "value": "false"},
    {"name": "ALLOWED_ORIGINS", "value": "https://cheasydiy.com"},
    {"name": "BASE_URL", "value": "https://api.cheasydiy.com"}
  ],
  "secrets": [
    {"name": "SECRET_KEY", "valueFrom": "arn:aws:secretsmanager:..."},
    {"name": "OPENAI_API_KEY", "valueFrom": "arn:aws:secretsmanager:..."}
  ]
}
```

### 2. Frontend Build Configuration

Frontend is built with production API URL during CI/CD:

```dockerfile
# In Dockerfile
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL

# During build in GitHub Actions
docker build --build-arg VITE_API_URL=https://api.cheasydiy.com -t frontend .
```

## 🔄 Seamless Transition Mechanisms

### 1. **Dynamic Configuration Loading**

Backend (`app/config.py`):
```python
class Settings(BaseSettings):
    database_url: str = "sqlite:///./diy_assistant.db"
    
    class Config:
        env_file = ".env"  # Loads from .env file if exists
        case_sensitive = False
```

Frontend (`src/utils/api.ts`):
```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
```

### 2. **Database Abstraction**

Backend automatically adapts to database type:
```python
if settings.database_url.startswith("sqlite"):
    # SQLite configuration for local
    engine = create_async_engine(
        settings.database_url.replace("sqlite://", "sqlite+aiosqlite://")
    )
else:
    # PostgreSQL configuration for production
    engine = create_async_engine(
        settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
    )
```

### 3. **Port Configuration**

- **Local**: Direct access on configured ports
- **AWS**: 
  - Backend: ECS service exposes port 8000 internally, ALB maps to 443 externally
  - Frontend: Nginx serves on port 80 internally, CloudFront serves on 443 externally

### 4. **CORS Handling**

Dynamic CORS configuration based on environment:
```python
allowed_origins = settings.allowed_origins  # Parsed from comma-separated string
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

## 📝 Environment Files Summary

### Local Development Files
```
backend/
  ├── .env.example        # Template for all environments
  ├── .env.local          # Pre-configured for local development
  └── .env                # Your actual local configuration (gitignored)

frontend/
  ├── .env.example        # Template for all environments
  ├── .env.local          # Local development configuration
  └── .env.production     # Production build configuration (optional)
```

### AWS Deployment Configuration
- **Backend**: Environment variables set in ECS task definition
- **Frontend**: Build-time variables passed during Docker build
- **Secrets**: Stored in AWS Secrets Manager and injected at runtime

## 🛠️ Common Scenarios

### Switching Database from SQLite to PostgreSQL

1. **Local Testing with PostgreSQL**:
```env
# backend/.env
DATABASE_URL="postgresql://postgres:password@localhost:5432/diyassistant"
```

2. **Production PostgreSQL**:
```json
// ECS Task Definition
{"name": "DATABASE_URL", "value": "postgresql://user:pass@rds.amazonaws.com:5432/db"}
```

### Adding New Environment Variable

1. **Add to backend/app/config.py**:
```python
class Settings(BaseSettings):
    new_feature_enabled: bool = False
```

2. **Set in local .env**:
```env
NEW_FEATURE_ENABLED=true
```

3. **Set in ECS task definition**:
```json
{"name": "NEW_FEATURE_ENABLED", "value": "false"}
```

## 🚨 Important Notes

1. **Never commit sensitive data**: `.env` files with real credentials should be gitignored
2. **Use AWS Secrets Manager**: For production secrets like API keys and passwords
3. **Environment validation**: Backend validates required environment variables on startup
4. **Frontend variables**: Must be prefixed with `VITE_` to be accessible
5. **Build-time vs Runtime**: Frontend variables are set at build time, backend at runtime

## 🔍 Debugging Environment Issues

### Check Current Configuration

Backend:
```python
# Add temporary endpoint to check config (remove in production)
@app.get("/debug/config")
async def debug_config():
    return {
        "database_url": settings.database_url.split("@")[0],  # Hide password
        "debug": settings.debug,
        "allowed_origins": settings.allowed_origins
    }
```

Frontend:
```javascript
console.log('API URL:', import.meta.env.VITE_API_URL)
console.log('Debug Mode:', import.meta.env.VITE_ENABLE_DEBUG)
```

### Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| CORS errors in production | Origins mismatch | Update ALLOWED_ORIGINS in ECS task |
| Database connection fails | Wrong connection string | Verify DATABASE_URL format |
| API calls fail from frontend | Wrong API URL | Check VITE_API_URL in build |
| Port conflicts locally | Port already in use | Change PORT in .env |

## 📚 Quick Reference

### Local Development Command
```bash
# Start everything locally
cd backend && uvicorn app.main:app --reload &
cd ../frontend && npm run dev
```

### Production Deployment Command
```bash
# Deploy to AWS
git checkout aws-deployment
git merge local-v2
git push origin aws-deployment
# GitHub Actions handles the rest
```

## 🎯 Best Practices

1. **Keep configurations minimal**: Only override what's necessary
2. **Use defaults wisely**: Set sensible defaults in code
3. **Document changes**: Update .env.example when adding new variables
4. **Test configuration changes**: Verify locally before deploying
5. **Monitor after deployment**: Check logs for configuration issues

---

This configuration strategy ensures that your application works seamlessly across environments while maintaining security and flexibility.