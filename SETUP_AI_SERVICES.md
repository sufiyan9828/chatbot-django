# AI Services Setup Guide

This guide helps you configure AI services for your chatbot application.

## Current Status
- ✅ **Gemini API**: Configured but experiencing timeouts
- ❌ **OpenRouter API**: Not configured (recommended free alternative)

## Recommended Solution: OpenRouter

OpenRouter provides access to multiple AI models with a free tier and is more reliable than the current Gemini setup.

### Step 1: Get OpenRouter API Key

1. Visit [OpenRouter.ai](https://openrouter.ai/)
2. Sign up for a free account
3. Navigate to the API Keys section
4. Create a new API key
5. Copy the API key

### Step 2: Update Environment Variables

Add the OpenRouter API key to your `.env` file:

```bash
# Existing Gemini key (keep as backup)
GEMINI_API_KEY=your_existing_gemini_key

# Add OpenRouter key
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-key-here
```

### Step 3: Restart the Server

```bash
# Stop the current server (Ctrl+C in terminal)
# Then restart:
python manage.py runserver 127.0.0.1:8000
```

### Step 4: Verify Configuration

Check the server logs for:
```
AI Services - Gemini: ✓, OpenRouter: ✓
```

## Available Models

### OpenRouter Free Models:
- `anthropic/claude-3-haiku` (recommended - fast and reliable)
- `google/gemini-flash-1.5` (if Gemini API is working)
- `meta-llama/llama-3.1-8b-instruct` (open source alternative)

### Model Configuration

You can change the model in `chatbot_project/settings.py`:

```python
# OpenRouter model options
OPENROUTER_MODEL = "anthropic/claude-3-haiku"  # Default (recommended)
# OPENROUTER_MODEL = "google/gemini-flash-1.5"  # Alternative
# OPENROUTER_MODEL = "meta-llama/llama-3.1-8b-instruct"  # Open source
```

## Features Enabled

### ✅ Automatic Fallback
- If OpenRouter fails, automatically tries Gemini
- If both fail, uses intelligent fallback responses
- No more "Sorry, something went wrong" messages

### ✅ Exponential Backoff Retries
- Automatically retries failed requests with increasing delays
- Prevents overwhelming the API during temporary issues

### ✅ Performance Monitoring
- Tracks response times and success rates
- Logs which service is being used
- Provides usage statistics

### ✅ Input Validation & Rate Limiting
- 10 requests per minute per IP address
- Input sanitization and length limits
- Protection against injection attempts

## Troubleshooting

### API Key Issues

**Invalid Gemini Key:**
```
WARNING: GEMINI_API_KEY format appears invalid. Gemini keys typically start with 'AIza'
```
- Gemini keys should start with "AIza"
- Get a new key from [Google AI Studio](https://aistudio.google.com/)

**Invalid OpenRouter Key:**
```
WARNING: OPENROUTER_API_KEY appears too short
```
- OpenRouter keys should start with "sk-or-v1-"
- Get a new key from [OpenRouter Dashboard](https://openrouter.ai/keys)

### Service Unavailable

If both services fail:
1. Check internet connection
2. Verify API keys are valid
3. Check service status pages:
   - [Google AI Status](https://status.cloud.google.com/)
   - [OpenRouter Status](https://status.openrouter.ai/)

### Performance Issues

**Slow Responses:**
- Try switching to a faster model (claude-3-haiku)
- Check timeout settings in `settings.py`
- Monitor logs for retry patterns

## Advanced Configuration

### Custom Timeout Settings
```python
# In chatbot_project/settings.py
AI_TIMEOUT = 45.0  # Increase timeout to 45 seconds
AI_MAX_RETRIES = 2  # Reduce retries to avoid long waits
```

### Rate Limiting
```python
# In chatbot_project/settings.py
RATE_LIMIT = 20  # Increase to 20 requests per minute
```

### Database Persistence
The application now stores:
- Chat sessions and messages
- AI service usage statistics
- System performance metrics

View this data in the Django admin: `http://127.0.0.1:8000/admin/`

## Next Steps

1. **Immediate**: Configure OpenRouter API key
2. **Short Term**: Test with different models
3. **Medium Term**: Monitor usage in admin dashboard
4. **Long Term**: Consider deploying to cloud for better reliability

## Support

- **OpenRouter Documentation**: https://openrouter.ai/docs
- **Gemini API Documentation**: https://ai.google.dev/docs
- **Application Issues**: Check `logs/debug.log` for detailed error information
