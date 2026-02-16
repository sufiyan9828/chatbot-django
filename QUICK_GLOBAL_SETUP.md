# 🚀 Quick Global Setup - 5 Minutes!

Region restrictions? No problem! You're getting an even better setup with global AI services.

---

## ⚡ Step 1: Get Groq API Key (2 minutes)

**Go to**: https://console.groq.com/

1. Click **"Sign up"** (instant approval)
2. Verify your email
3. Click **"Keys"** in sidebar
4. Click **"Create New Key"**
5. Name it: "Chatbot Key"
6. **Copy the key** (starts with `gsk_...`)

---

## 🤖 Step 2: Get OpenRouter API Key (2 minutes)

**Go to**: https://openrouter.ai/

1. Click **"Sign up"** (instant approval)
2. Verify your email
3. Click **"API Keys"** in sidebar
4. Click **"Create Key"**
5. **Copy the key** (starts with `sk-or-v1-...`)

---

## 🔧 Step 3: Update Your .env File (1 minute)

Replace the placeholder keys in your `.env` file:

```bash
# Groq Cloud API (Primary - Ultra Fast)
GROQ_API_KEY=gsk_your-actual-groq-key-here

# OpenRouter API (Backup - Multiple Models)
OPENROUTER_API_KEY=sk-or-v1-your-actual-openrouter-key-here

# Gemini API (Skip if not available in your region)
# GEMINI_API_KEY=
```

---

## 🔄 Step 4: Restart Server (30 seconds)

```bash
# Stop current server (Ctrl+C)
# Then restart:
python manage.py runserver 127.0.0.1:8000
```

---

## ✅ Step 5: Test Your Setup (30 seconds)

Run this test to verify AI responses are working:

```python
import requests

response = requests.post('http://127.0.0.1:8000/api/webhook/', json={
    'message': 'Hello, how are you?',
    'platform': 'test',
    'user_id': 'test'
})

data = response.json()
print('Status:', 'AI Working!' if not data.get('fallback') else 'Setup API keys')
print('Response:', data.get('response', 'No response')[:50] + '...')
```

---

## 🎉 You're Done! 

**Total Time: Less than 5 minutes!**

### What You Get:
- ⚡ **Ultra-fast responses** (300+ tokens/second)
- 🆓 **14,400 free requests/day** (10x Gemini!)
- 🌍 **Global access** (works anywhere)
- 🤖 **Latest Llama 3 models**
- 🔄 **Backup service** for reliability

### Why This is Better:
- **6x faster** than Gemini
- **10x more free requests**
- **Works globally** (no restrictions)
- **Multiple models** available

---

## 🎯 Success Indicators

✅ **Test shows "AI Working!"** instead of fallback  
✅ **Response time under 1 second**  
✅ **Intelligent, contextual responses**  
✅ **No "fallback mode" messages**

---

## 🔧 Troubleshooting

**If still showing fallback:**
1. Check API keys start with correct prefixes:
   - Groq: `gsk_...`
   - OpenRouter: `sk-or-v1-...`
2. Ensure no extra spaces in .env file
3. Restart Django server
4. Test again

---

## 🌟 You're Actually Lucky!

Being in a restricted region means you discovered **better alternatives** that many people miss!

**Enjoy your ultra-fast, globally accessible AI chatbot!** 🚀✨
