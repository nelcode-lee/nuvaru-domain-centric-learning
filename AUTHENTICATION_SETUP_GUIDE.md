# 🔐 Authentication Setup Guide

## Overview

Your Nuvaru platform already has a comprehensive authentication system implemented! This guide will help you complete the setup and test everything.

## ✅ What's Already Implemented

### Backend (FastAPI)
- ✅ JWT token authentication
- ✅ User registration and login
- ✅ Password hashing and validation
- ✅ Protected route middleware
- ✅ User management endpoints
- ✅ Token refresh functionality

### Frontend (React)
- ✅ AuthContext for state management
- ✅ AuthModal for login/registration
- ✅ API client with token handling
- ✅ Automatic token refresh
- ✅ Protected route components

## 🚀 Quick Setup

### 1. Start the Backend
```bash
python simple_backend.py
```

### 2. Test Authentication
```bash
python setup_authentication.py
```

### 3. Start the Frontend
```bash
cd react-frontend
npm start
```

## 📋 Authentication Endpoints

### Registration
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "Password123!",
  "full_name": "Full Name",
  "bio": "User bio"
}
```

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "username": "username",
  "password": "Password123!"
}
```

### Get Current User
```http
GET /auth/me
Authorization: Bearer <token>
```

### Refresh Token
```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "<refresh_token>"
}
```

### Logout
```http
POST /auth/logout
Authorization: Bearer <token>
```

## 🔧 Configuration

### Environment Variables
Add these to your `.env` file:

```bash
# JWT Configuration
SECRET_KEY="your-super-secret-key-change-this-in-production"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=10080

# Database
DATABASE_URL="postgresql://username:password@localhost:5432/nuvaru_db"
```

### Railway Production
Add these to your Railway environment variables:

```bash
SECRET_KEY="your-production-secret-key"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=10080
```

## 🧪 Testing Authentication

### 1. Backend Testing
```bash
# Test registration
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPassword123!",
    "full_name": "Test User"
  }'

# Test login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPassword123!"
  }'

# Test protected endpoint
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer <your-token>"
```

### 2. Frontend Testing
1. Open http://localhost:3000
2. Click "Sign In" or "Create Account"
3. Register a new user
4. Login with existing user
5. Test document upload and chat

## 🔒 Security Features

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

### JWT Token Security
- Access tokens expire in 30 minutes
- Refresh tokens expire in 7 days
- Tokens are signed with HMAC-SHA256
- Automatic token refresh on frontend

### User Management
- User accounts can be activated/deactivated
- Password change functionality
- User profile updates
- Last login tracking

## 🚀 Production Deployment

### 1. Update Railway Environment Variables
```bash
# Set strong secret key
SECRET_KEY="your-very-strong-secret-key-here"

# Configure token expiration
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=10080

# Database connection
NEON_DATABASE_URL="postgresql://..."
```

### 2. Update Frontend API URL
In `react-frontend/src/utils/authApi.ts`:
```typescript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://your-app.railway.app';
```

### 3. Configure CORS
In `simple_backend.py`, update CORS origins:
```python
cors_origins = [
    "https://your-frontend.vercel.app",
    "https://your-domain.com"
]
```

## 🐛 Troubleshooting

### Common Issues

1. **"Could not validate credentials"**
   - Check if token is expired
   - Verify SECRET_KEY is set correctly
   - Ensure token format is correct

2. **"Incorrect username or password"**
   - Check username/email spelling
   - Verify password requirements
   - Check if user account is active

3. **CORS errors**
   - Update CORS_ORIGINS in backend
   - Check frontend API_URL configuration

4. **Database connection errors**
   - Verify DATABASE_URL is correct
   - Check if database is running
   - Ensure tables are created

### Debug Commands
```bash
# Check backend logs
python simple_backend.py

# Test authentication
python setup_authentication.py

# Check database
python -c "from backend.app.database import init_db; init_db()"
```

## 📊 User Roles and Permissions

### Current Implementation
- **Regular Users**: Can upload documents, chat with AI, manage their own data
- **Superusers**: Full system access (future enhancement)

### Future Enhancements
- Role-based access control
- Team/organization management
- Document sharing permissions
- Admin dashboard

## 🔄 Token Refresh Flow

1. User logs in → receives access + refresh tokens
2. Access token expires (30 minutes)
3. Frontend automatically uses refresh token to get new access token
4. If refresh token expires → user must log in again

## 📱 Frontend Integration

### AuthContext Usage
```typescript
import { useAuth } from './contexts/AuthContext';

function MyComponent() {
  const { user, isAuthenticated, login, logout } = useAuth();
  
  if (!isAuthenticated) {
    return <LoginForm />;
  }
  
  return <Dashboard user={user} />;
}
```

### Protected Routes
```typescript
function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  return children;
}
```

## 🎯 Next Steps

1. **Test the complete flow** using the setup script
2. **Deploy to Railway** with authentication enabled
3. **Configure production settings** (CORS, secrets, etc.)
4. **Add user management features** (admin dashboard, user roles)
5. **Implement password reset** functionality
6. **Add social login** (Google, GitHub, etc.)

## 📞 Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Run the authentication setup script
3. Check backend and frontend logs
4. Verify environment variables are set correctly

---

**🎉 Your authentication system is ready to use!** The platform now supports secure user registration, login, and protected access to all features.
