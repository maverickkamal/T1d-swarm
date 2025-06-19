# T1D-Swarm Access Control Setup

This document explains how to set up and configure the access control system for the T1D-Swarm application.

## Overview

The access control system provides:
- **Judge Access**: Unlimited access to all features for authorized judges
- **Demo Access**: One-time limited access for public demonstrations
- **Blocked State**: Prevents abuse after demo usage

## Backend Setup

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Judge Codes

Create a `.env` file in the frontend directory:

```bash
# .env file
JUDGE_CODES=YOUR_SECRET_CODE1,YOUR_SECRET_CODE2,ADMIN_CODE
PORT=8001
```

### 3. Start Authentication Server

```bash
python judge-auth-backend.py
```

The server will start on http://localhost:8001

## Frontend Integration

The Angular frontend automatically:
1. Shows access prompt on first load
2. Stores judge codes in localStorage for future sessions
3. Tracks demo usage to prevent abuse
4. Displays appropriate banners for access level

## Access Levels

### Judge Access
- **Trigger**: Valid judge code entered
- **Features**: Full application functionality
- **Persistence**: Stored in browser localStorage
- **Visual**: Green banner "✅ Judge Access - All features enabled"

### Demo Access
- **Trigger**: Empty code submitted (or invalid code)
- **Features**: Limited functionality for evaluation
- **Limitations**: One-time use per browser/device
- **Visual**: Yellow banner "⚠️ Demo Mode - Limited functionality"

### Blocked Access
- **Trigger**: Demo already used on device
- **Features**: No access to application
- **Recovery**: Only through judge code
- **Visual**: Full-screen blocked message

## Security Features

1. **Rate Limiting**: Server logs all verification attempts
2. **IP Tracking**: Failed attempts are logged with IP addresses
3. **Persistence**: Demo usage tracked in localStorage
4. **Validation**: Server-side code verification

## Development/Testing

For development, the default judge codes are:
- `JUDGE2025`
- `T1D_ADMIN` 
- `DEMO_JUDGE`

**Note**: Change these for production use!

## Production Deployment

1. Set secure judge codes in environment variables
2. Configure CORS appropriately in backend
3. Use HTTPS for production
4. Consider adding rate limiting middleware
5. Set up logging and monitoring

## API Endpoints

- `POST /api/verify-judge` - Verify judge access code
- `GET /api/health` - Health check
- `GET /` - Service information

## Troubleshooting

### Clear Access State
To reset the access control state for testing:

```javascript
// In browser console
localStorage.removeItem('demo_usage_count');
localStorage.removeItem('judge_access_code');
location.reload();
```

### Backend Issues
- Check server logs for detailed error information
- Verify judge codes are properly set in environment
- Ensure CORS is configured for your frontend domain

### Frontend Issues
- Check browser console for API errors
- Verify backend is running on correct port
- Check network requests in browser DevTools 