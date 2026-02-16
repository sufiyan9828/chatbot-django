# Chatbot Application - Troubleshooting Guide

This guide helps you diagnose and fix common issues with the Django chatbot application.

## Quick Start

### For Development
```bash
# Run with startup validation
python validate_startup.py

# Or start normally
python manage.py runserver 127.0.0.1:8000
```

### For Production-like Environment
```bash
# Linux/macOS
chmod +x start_server.sh
./start_server.sh

# Windows
start_server.bat
```

## Common Issues and Solutions

### 1. "Sorry, something went wrong" Error

**Symptoms**: Generic error page without details

**Causes & Solutions**:

- **Debug Mode**: Check if `DEBUG = True` in `chatbot_project/settings.py`
- **Logs**: Check `logs/errors.log` for detailed error information
- **Environment**: Verify `.env` file exists and contains `GEMINI_API_KEY`

**Debug Steps**:
1. Visit `http://127.0.0.1:8000/system/` (only available in DEBUG mode)
2. Check `logs/debug.log` for full stack traces
3. Run `python validate_startup.py` for comprehensive health check

### 2. Server Won't Start

**Symptoms**: Server fails to start or crashes immediately

**Debug Steps**:
```bash
# Run validation script
python validate_startup.py

# Check Django system checks
python manage.py check

# Test database connection
python manage.py dbshell
```

**Common Fixes**:
- Missing dependencies: `pip install -r requirements.txt`
- Invalid environment variables: Check `.env` file
- Database issues: `python manage.py migrate`
- Port conflicts: Change port or kill conflicting process

### 3. Database Connection Issues

**Symptoms**: Database-related errors in logs

**Solutions**:
```bash
# Recreate database
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser

# Check database integrity
python manage.py dbshell
.schema
```

### 4. Static Files Not Loading

**Symptoms**: CSS/JS files missing, broken styling

**Solutions**:
```bash
# Collect static files
python manage.py collectstatic

# Check static file configuration
# Verify STATIC_URL and STATIC_ROOT in settings.py
```

### 5. API Key Issues

**Symptoms**: Gemini API errors, chatbot not responding

**Solutions**:
1. Verify `GEMINI_API_KEY` in `.env` file
2. Check API key validity with Google AI Studio
3. Review API quota and usage limits

## Monitoring and Health Checks

### Health Endpoints

- **Health Check**: `http://127.0.0.1:8000/health/`
  - Returns system status, database connectivity, environment variables
  - Status 200 for healthy, 503 for unhealthy

- **System Info**: `http://127.0.0.1:8000/system/` (DEBUG mode only)
  - Detailed Django settings and request information

### Log Files

All logs are stored in the `logs/` directory:

- **`debug.log`**: All application logs with full details
- **`errors.log`**: Error-level logs only
- **`access.log`**: Web server access logs (when using process manager)

### Log Format
```
[2025-02-14T12:30:45.123Z] INFO | module:function:line | Message content
```

## Performance Monitoring

### System Metrics
The health endpoint provides:
- Memory usage percentage
- Disk usage percentage  
- CPU count
- Database connectivity status

### Request Logging
All requests are logged with:
- HTTP method and path
- Response status code
- Request duration in milliseconds

## Security Considerations

### Environment Variables
- Never commit `.env` files to version control
- Use strong, unique API keys
- Rotate keys regularly

### Debug Mode
- Always set `DEBUG = False` in production
- Use proper error handling middleware
- Log errors securely without exposing sensitive data

## Process Management

### Automatic Restart
The process manager scripts provide:
- Automatic restart on crashes
- Maximum restart limits to prevent infinite loops
- Graceful shutdown handling
- PID file management

### Manual Control
```bash
# Check if server is running
curl http://127.0.0.1:8000/health/

# Stop server (Linux/macOS)
kill $(cat server.pid)

# Stop server (Windows)
taskkill /f /im python.exe
```

## Development Workflow

### Before Starting Server
1. Run `python validate_startup.py`
2. Check all validations pass
3. Review any warnings
4. Start server using appropriate method

### During Development
1. Monitor `logs/debug.log` for issues
2. Use health endpoint to verify status
3. Test error scenarios with `DEBUG = True`
4. Verify error handling with `DEBUG = False`

### Before Deployment
1. Set `DEBUG = False`
2. Configure proper `ALLOWED_HOSTS`
3. Test with production settings
4. Verify all environment variables
5. Run full validation suite

## Getting Help

If issues persist:

1. **Check Logs**: Always start with `logs/errors.log`
2. **Run Validation**: `python validate_startup.py`
3. **Health Check**: Visit `/health/` endpoint
4. **System Info**: Visit `/system/` endpoint (DEBUG mode)
5. **Django Checks**: `python manage.py check --deploy`

## Emergency Recovery

If the application becomes completely unresponsive:

```bash
# Emergency reset (development only)
rm -rf logs/
rm db.sqlite3
python manage.py migrate
python validate_startup.py
```

This will:
- Clear all logs
- Recreate the database
- Run full validation
- Start fresh
