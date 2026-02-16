# 🔑 API Key Setup Guide

Get your free API keys and unlock the full power of your chatbot!

---

## 🌟 Google Gemini API (Recommended - Most Generous)

### Step 1: Get Your API Key
1. **Visit**: https://aistudio.google.com/
2. **Sign in** with your Google account
3. **Click "Get API Key"** in the left sidebar
4. **Select "Create API Key"**
5. **Name your key**: "My Chatbot"
6. **Copy the key** (starts with `AIza...`)

### Step 2: Free Tier Benefits
- ✅ **15 requests per minute**
- ✅ **1,500 requests per day** 
- ✅ **32,000 characters per month**
- ✅ **Multiple models** (Gemini Pro, Gemini Flash)
- ✅ **High quality responses**

### Step 3: Add to Your .env File
```bash
# Replace AIza-your-gemini-key-here with your actual key
GEMINI_API_KEY=AIzaSyDxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## ⚡ Groq Cloud (Ultra-Fast Alternative)

### Step 1: Get Your API Key
1. **Visit**: https://console.groq.com/
2. **Click "Sign up"** for free account
3. **Verify your email**
4. **Go to "Keys" section**
5. **Click "Create New Key"**
6. **Name your key**: "Chatbot Key"
7. **Copy the key** (starts with `gsk_...`)

### Step 2: Free Tier Benefits
- ✅ **14,400 requests per day**
- ✅ **Ultra-fast inference** (300+ tokens/second)
- ✅ **Meta Llama 3 models**
- ✅ **Mixtral models**
- ✅ **Excellent for chatbots**

### Step 3: Add to Your .env File
```bash
# Replace gsk_your-groq-key-here with your actual key
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 🔧 Complete Setup Instructions

### 1. Update Your .env File
Open your `.env` file and replace the placeholder keys:

```bash
# AI Service Configuration
# Add your API keys below

# Google Gemini API (get from: https://aistudio.google.com/)
GEMINI_API_KEY=AIza-your-actual-gemini-key-here

# Groq Cloud API (get from: https://console.groq.com/)
GROQ_API_KEY=gsk_your-actual-groq-key-here

# OpenRouter API (backup option)
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-key-here
```

### 2. Restart Your Chatbot
```bash
# Stop the current server (Ctrl+C)
# Then restart:
python manage.py runserver 127.0.0.1:8000
```

### 3. Test Your API Keys
```bash
# Test the chatbot with real AI responses
python simple_test.py
```

---

## 🎯 Which API Should You Use?

### 🥇 First Choice: Google Gemini
**Best for:** High-quality, intelligent responses
- **Most generous free tier**
- **Excellent understanding**
- **Great for complex conversations**

### 🥈 Second Choice: Groq Cloud  
**Best for:** Speed and efficiency
- **Ultra-fast responses**
- **Great for real-time chat**
- **Reliable performance**

### 🥉 Backup: OpenRouter
**Best for:** Multiple model options
- **Access to many AI models**
- **Good fallback option**
- **Flexible model selection**

---

## 🚀 Quick Start Checklist

### ✅ Pre-Launch Checklist
- [ ] **Get Gemini API key** from https://aistudio.google.com/
- [ ] **Get Groq API key** from https://console.groq.com/
- [ ] **Update .env file** with your actual keys
- [ ] **Restart Django server**
- [ ] **Test with `python simple_test.py`**
- [ ] **Verify AI responses** (not fallback)

### ✅ Success Indicators
- Chatbot responds with intelligent, contextual answers
- Response times under 2 seconds
- No "fallback mode" messages
- Emoji and personality working correctly

---

## 🔍 Troubleshooting

### Gemini API Issues
**Problem**: "API key format appears invalid"
**Solution**: Ensure key starts with `AIza` and is copied correctly

**Problem**: "The read operation timed out"
**Solution**: Check internet connection, try again

### Groq API Issues  
**Problem**: "Invalid API key"
**Solution**: Ensure key starts with `gsk_` and has no extra spaces

**Problem**: "Rate limit exceeded"
**Solution**: Wait a few minutes, free tier has limits

### General Issues
**Problem**: Still using fallback responses
**Solution**: 
1. Check .env file has correct keys
2. Restart Django server
3. Check server logs for errors

---

## 📊 API Usage Monitoring

### Check Your Usage
- **Gemini**: https://aistudio.google.com/apiusage
- **Groq**: https://console.groq.com/usage
- **Dashboard**: http://127.0.0.1:8000/dashboard/

### Free Tier Limits
| Service | Daily Limit | Monthly Limit | Speed |
|---------|-------------|---------------|-------|
| Gemini | 1,500 requests | 32,000 chars | Fast |
| Groq | 14,400 requests | Unlimited | Ultra-Fast |
| OpenRouter | Varies | Varies | Fast |

---

## 🎉 Next Steps

### After Setting Up API Keys
1. **Test thoroughly** with different conversation flows
2. **Monitor usage** to stay within free limits
3. **Choose primary service** based on performance
4. **Set up alerts** for usage monitoring
5. **Plan for scaling** when you exceed free tiers

### Pro Tips
- **Start with Gemini** for best quality
- **Add Groq as backup** for speed
- **Monitor usage daily** at first
- **Keep keys secure** - never share them
- **Test regularly** to ensure services work

---

## 🔐 Security Best Practices

### Protect Your API Keys
- ✅ **Never commit** .env files to Git
- ✅ **Use environment variables** in production
- ✅ **Rotate keys** every 90 days
- ✅ **Monitor usage** for unusual activity
- ✅ **Use separate keys** for different projects

### Production Deployment
```bash
# Set environment variables instead of .env file
export GEMINI_API_KEY=your_production_key
export GROQ_API_KEY=your_production_key
export OPENROUTER_API_KEY=your_production_key
```

---

## 📞 Need Help?

### API Key Issues
- **Gemini Support**: https://aistudio.google.com/support
- **Groq Support**: https://console.groq.com/support
- **OpenRouter Support**: https://openrouter.ai/support

### Chatbot Issues
- **Check logs**: `logs/debug.log`
- **Test API**: `python simple_test.py`
- **Dashboard**: http://127.0.0.1:8000/dashboard/
- **Health check**: http://127.0.0.1:8000/health/

---

## 🎯 You're Ready to Go!

Once you have your API keys set up:

1. **Update your .env file** with real keys
2. **Restart the server**
3. **Test with real AI responses**
4. **Enjoy your intelligent chatbot!**

Your chatbot will go from basic fallback responses to intelligent, contextual conversations that delight your users! 🚀

---

**Quick Links:**
- 🌟 **Gemini Studio**: https://aistudio.google.com/
- ⚡ **Groq Console**: https://console.groq.com/
- 📊 **Your Dashboard**: http://127.0.0.1:8000/dashboard/
- 🧪 **Test Script**: `python simple_test.py`

**Happy coding! 🤖**
