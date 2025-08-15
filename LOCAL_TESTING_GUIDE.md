# 🧪 Local Testing Guide

## 🚀 Current Status
- **Backend**: http://localhost:8001
- **Frontend**: http://localhost:3001  
- **API Docs**: http://localhost:8001/docs

## 👥 Test Users Available
- **Demo User**: username: `demo`, password: `demo123` (Premium member)

## 🧪 Test Cases

### 1. Home Page Testing
Visit: http://localhost:3001

**Expected Behavior:**
- [ ] Shows feature showcase instead of direct upload
- [ ] "Get Started" button for non-authenticated users
- [ ] Features show "Login Required" when not logged in
- [ ] Examples section displays correctly
- [ ] Authentication prompt shown for unauthenticated users
- [ ] Language switcher works (EN/中文)

### 2. Authentication Flow
**Register New User:**
- [ ] Click "Sign Up Free" → `/register`
- [ ] Create account with email/username/password
- [ ] Should auto-login after registration

**Login Existing User:**
- [ ] Click "Login" → `/login`
- [ ] Use demo account: `demo` / `demo123`
- [ ] Should redirect to home page after login

**Post-Login Home Page:**
- [ ] Shows "Welcome back, [username]!" message
- [ ] "Try Now" buttons are enabled
- [ ] Navigation shows protected routes (DIY Assistant, Tool ID)

### 3. Protected Routes Testing
**Before Login:**
- [ ] Direct access to `/diy-assistant` redirects to login
- [ ] Direct access to `/tool-identification` redirects to login

**After Login:**
- [ ] Can access `/diy-assistant` 
- [ ] Can access `/tool-identification`
- [ ] Navigation menu shows these options

### 4. DIY Assistant Testing
Navigate to: http://localhost:3001/diy-assistant (after login)

**Expected Behavior:**
- [ ] Upload interface works
- [ ] Can select project type and budget
- [ ] Analysis button works (may use mock data without OpenAI key)
- [ ] Results display correctly
- [ ] Product recommendations shown

### 5. Tool Identification Testing  
Navigate to: http://localhost:3001/tool-identification (after login)

**Expected Behavior:**
- [ ] Image upload works
- [ ] Daily quota system works (premium user has 50/day)
- [ ] Tool identification results display
- [ ] Shopping recommendations provided

### 6. User Dashboard
Navigate to: http://localhost:3001/dashboard (after login)

**Expected Behavior:**
- [ ] Shows user info and membership
- [ ] Displays usage statistics
- [ ] Shows identification history (currently empty)

### 7. Admin Features Testing
**Create First Admin User:**
```bash
curl -X POST http://localhost:8001/api/setup/create-first-admin \
  -F "admin_email=admin@localhost.com" \
  -F "admin_username=admin" \
  -F "admin_password=admin123" \
  -F "setup_key=setup_admin_2025"
```

**Admin Testing:**
- [ ] Login as admin user
- [ ] Has unlimited quotas
- [ ] Can create other admin users via API

### 8. API Testing
**Backend Health Check:**
```bash
curl http://localhost:8001/api/test
```

**Database Connection:**
```bash
curl http://localhost:8001/api/test/db-connection
```

**User Count:**
```bash
curl http://localhost:8001/api/test/user-count
```

## 🔧 Common Issues & Solutions

### Frontend Issues:
- **CORS Errors**: Backend CORS is configured for localhost:3001
- **Build Errors**: Run `npm run build` to check for compilation errors
- **Route Issues**: Check browser console for routing errors

### Backend Issues:
- **Database**: Using SQLite (local_test.db file created)
- **Missing Dependencies**: Install with `pip install [package-name]`
- **OpenAI API**: Works with mock data if no API key provided

### Authentication Issues:
- **JWT Errors**: Using local JWT secret key
- **Session Issues**: Check browser local storage for token
- **Login Loops**: Clear browser cache/local storage

## 🚀 Next Steps After Local Testing

1. **If everything works locally:**
   - Add your OpenAI API key to test real AI features
   - Deploy to AWS ECS production environment
   - Update production secrets with OpenAI key

2. **If issues found:**
   - Check browser console for frontend errors
   - Check backend logs in terminal
   - Test individual API endpoints with curl
   - Verify database connections

## 🔄 Restart Services

**Restart Backend:**
- Stop: Ctrl+C in backend terminal
- Start: `cd backend && python run_local.py`

**Restart Frontend:**  
- Stop: Ctrl+C in frontend terminal
- Start: `cd frontend && npm run dev`

## 🐛 Debug Mode

**Enable Backend SQL Logging:**
Edit `database.py`, set `echo=True` in engine creation

**Enable Frontend Debug:**
Check browser Developer Tools → Console for errors