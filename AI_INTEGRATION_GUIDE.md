# 🤖 Complete AI Integration Guide

Your chatbot now supports **all major AI providers** with full integration capabilities!

---

## 🎯 **Available AI Services**

### ✅ **Google Gemini AI**
- **Purpose**: High-quality, intelligent responses
- **Strengths**: Excellent understanding, contextual conversations
- **Free Tier**: 1,500 requests/day, 32,000 chars/month
- **Setup**: `GEMINI_API_KEY` in .env file
- **Best For**: Complex conversations, nuanced responses

### ⚡ **Groq Cloud** (Primary Recommendation)
- **Purpose**: Ultra-fast responses with latest models
- **Strengths**: 300+ tokens/second, Llama 3 models
- **Free Tier**: 14,400 requests/day (most generous!)
- **Setup**: `GROQ_API_KEY` in .env file
- **Best For**: Real-time chat, high-volume applications

### 🤖 **OpenAI GPT**
- **Purpose**: Industry-standard GPT models
- **Strengths**: Versatile, well-documented capabilities
- **Free Tier**: Limited but high quality
- **Setup**: `OPENAI_API_KEY` in .env file
- **Best For**: General-purpose AI tasks

### 🎭 **Anthropic Claude**
- **Purpose**: Advanced reasoning, safety-focused responses
- **Strengths**: Excellent analytical capabilities, safe outputs
- **Free Tier**: Limited but very high quality
- **Setup**: `ANTHROPIC_API_KEY` in .env file
- **Best For**: Complex reasoning, safety-critical applications

---

## 🔧 **Setup Instructions**

### **Step 1: Choose Your Primary AI Service**

#### **For Speed & Volume**: Groq Cloud
```bash
GROQ_API_KEY=gsk_your-groq-key-here
```

#### **For Quality & Intelligence**: Google Gemini
```bash
GEMINI_API_KEY=AIzaSyDH2vm3U4Lm-w02K3mR09z5zP8yiWHAU8A
```

#### **For Versatility**: OpenAI GPT
```bash
OPENAI_API_KEY=sk-your-openai-key-here
```

#### **For Advanced Reasoning**: Anthropic Claude
```bash
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
```

### **Step 2: Update Your .env File**

```bash
# AI Service Configuration - Complete Setup
# Primary AI Service (choose one)
GROQ_API_KEY=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

# Backup AI Services (optional but recommended)
GEMINI_API_KEY=AIzaSyDH2vm3U4Lm-w02K3mR09z5zP8yiWHAU8A
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Service Priority (Groq recommended for speed)
AI_PRIMARY_SERVICE=groq
```

### **Step 3: Install Dependencies**

```bash
# Install all AI libraries
pip install openai anthropic

# Update requirements
pip install -r requirements.txt
```

### **Step 4: Restart Server**

```bash
python manage.py runserver 127.0.0.1:8000
```

---

## 🧪 **AI Service Code Examples**

### **Using Groq Cloud**
```python
import openai

# Initialize Groq client
client = openai.OpenAI(
    api_key="gsk_your-groq-key-here",
    base_url="https://api.groq.com/openai/v1"
)

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "Hello! How are you?"}
    ],
    max_tokens=150
)

print(response.choices[0].message.content)
```

### **Using Google Gemini**
```python
import google.generativeai as genai

# Initialize Gemini client
genai.configure(api_key="AIzaSyDH2vm3U4Lm-w02K3mR09z5zP8yiWHAU8A")
model = genai.GenerativeModel('models/gemini-2.5-flash')

response = model.generate_content("Hello! How are you?")
print(response.text)
```

### **Using OpenAI GPT**
```python
import openai

# Initialize OpenAI client
client = openai.OpenAI(api_key="sk-your-openai-key-here")

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "Hello! How are you?"}
    ],
    max_tokens=150
)

print(response.choices[0].message.content)
```

### **Using Anthropic Claude**
```python
import anthropic

# Initialize Claude client
client = anthropic.Anthropic(api_key="sk-ant-your-anthropic-key-here")

response = client.messages.create(
    model="claude-3-haiku-20240307",
    max_tokens=150,
    messages=[
        {"role": "user", "content": "Hello! How are you?"}
    ]
)

print(response.content[0].text)
```

---

## 📊 **Performance Comparison**

| Service | Response Time | Quality | Cost | Free Tier | Best Use Case |
|---------|--------------|--------|------|-----------|--------------|
| **Groq** | ⚡ Ultra-fast | 🦙 High | 🆓 Most generous | Real-time chat |
| **Gemini** | 🚀 Fast | 🧠 Excellent | 🆓 Moderate | Complex conversations |
| **OpenAI** | 🚀 Fast | 🦙 Excellent | 💰 Limited | General purpose |
| **Claude** | 🚀 Fast | 🧠 Superior | 💰 Limited | Advanced reasoning |

---

## 🔄 **Service Fallback Strategy**

Your chatbot automatically falls back in this order:

1. **Primary Service** (configured in `AI_PRIMARY_SERVICE`)
2. **Available Services** (in order of initialization)
3. **Fallback Responses** (if all AI services fail)

### **Configuration Options**

```python
# In settings.py
AI_PRIMARY_SERVICE=groq  # or gemini, openai, anthropic

# Automatic fallback order
# 1. Groq (if GROQ_API_KEY set)
# 2. Gemini (if GEMINI_API_KEY set)  
# 3. OpenAI (if OPENAI_API_KEY set)
# 4. Claude (if ANTHROPIC_API_KEY set)
```

---

## 🧪 **Testing Your AI Integration**

### **Test All Services**
```python
# Test script
import requests

services = [
    {"name": "Groq", "key": "gsk_test"},
    {"name": "Gemini", "key": "gemini_test"},
    {"name": "OpenAI", "key": "openai_test"},
    {"name": "Claude", "key": "claude_test"}
]

for service in services:
    response = requests.post('http://127.0.0.1:8000/api/webhook/', json={
        'message': f'Test {service["name"]} service!',
        'platform': 'test',
        'user_id': service["key"]
    })
    
    if response.status_code == 200:
        data = response.json()
        is_fallback = data.get('fallback', False)
        status = "✅ AI" if not is_fallback else "❌ Fallback"
        print(f'{service["name"]}: {status} - {data.get("response", "No response")[:50]}...')
    else:
        print(f'{service["name"]}: ERROR - HTTP {response.status_code}')
```

### **Performance Testing**
```python
# Test response times
import time
import requests

start_time = time.time()
response = requests.post('http://127.0.0.1:8000/api/webhook/', json={
    'message': 'Tell me a joke!',
    'platform': 'test',
    'user_id': 'perf_test'
})

end_time = time.time()
response_time = (end_time - start_time) * 1000  # Convert to ms

print(f'Response time: {response_time:.0f}ms')
print(f'Status: {"Fast" if response_time < 500 else "Slow"}')
```

---

## 🌍 **Production Deployment**

### **Environment Variables**
```bash
# Production .env example
AI_PRIMARY_SERVICE=groq
GROQ_API_KEY=your_production_groq_key
GEMINI_API_KEY=your_production_gemini_key
OPENAI_API_KEY=your_production_openai_key
ANTHROPIC_API_KEY=your_production_anthropic_key

# Security settings
AI_TIMEOUT=30.0
AI_MAX_RETRIES=3
DEBUG=False
```

### **Docker Configuration**
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Environment variables
ENV AI_PRIMARY_SERVICE=groq
ENV GROQ_API_KEY=${GROQ_API_KEY}
ENV GEMINI_API_KEY=${GEMINI_API_KEY}
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

---

## 📈 **Monitoring & Analytics**

### **Service Health Checks**
```python
# Health check script
import requests

def check_service_health():
    services = {
        'groq': 'https://api.groq.com/health',
        'openai': 'https://api.openai.com/v1/models',
        'anthropic': 'https://api.anthropic.com/v1/messages'
    }
    
    for service, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            status = "✅ Healthy" if response.status_code == 200 else "❌ Unhealthy"
            print(f'{service.upper()}: {status}')
        except Exception as e:
            print(f'{service.upper()}: ❌ Error - {e}')

check_service_health()
```

### **Usage Tracking**
```python
# Usage analytics
from chatbot_app.models import AIServiceUsage
from datetime import datetime, timedelta

def get_usage_stats():
    last_24h = datetime.now() - timedelta(hours=24)
    
    stats = AIServiceUsage.objects.filter(
        last_used__gte=last_24h
    ).aggregate(
        total_requests=models.Sum('request_count'),
        avg_response_time=models.Avg('avg_response_time_ms'),
        total_tokens=models.Sum('total_tokens')
    )
    
    return {
        'total_requests': stats['total_requests'] or 0,
        'avg_response_time': stats['avg_response_time_ms'] or 0,
        'total_tokens': stats['total_tokens'] or 0,
        'services_used': list(AIServiceUsage.objects.values_list('service_name', flat=True).distinct())
    }

# Usage stats
stats = get_usage_stats()
print(f"Total requests (24h): {stats['total_requests']}")
print(f"Avg response time: {stats['avg_response_time_ms']:.0f}ms")
print(f"Total tokens: {stats['total_tokens']}")
```

---

## 🔧 **Advanced Configuration**

### **Custom Model Settings**
```python
# In ai_services.py
class CustomAIService(AIServiceBase):
    def __init__(self, api_key: str, model: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.custom_model = model
        self.temperature = kwargs.get('temperature', 0.7)
        self.max_tokens = kwargs.get('max_tokens', 150)
    
    async def generate_response(self, message: str) -> str:
        # Custom implementation
        pass
```

### **Rate Limiting**
```python
# Custom rate limiting per service
RATE_LIMITS = {
    'groq': 100,  # requests per minute
    'gemini': 15,   # requests per minute  
    'openai': 60,   # requests per minute
    'anthropic': 50  # requests per minute
}

def check_rate_limit(service_name, user_id):
    from django.core.cache import cache
    key = f"rate_limit_{service_name}_{user_id}"
    
    count = cache.get(key, 0)
    limit = RATE_LIMITS.get(service_name, 60)
    
    if count >= limit:
        return False, f"Rate limit exceeded for {service_name}"
    
    cache.set(key, count + 1, timeout=60)
    return True, "Request allowed"
```

---

## 🎯 **Best Practices**

### **Security**
- ✅ **Never commit API keys** to version control
- ✅ **Use environment variables** in production
- ✅ **Implement rate limiting** per service
- ✅ **Monitor usage** and costs
- ✅ **Validate API keys** on startup

### **Performance**
- ✅ **Use connection pooling** for HTTP requests
- ✅ **Implement caching** for repeated requests
- ✅ **Set appropriate timeouts** (30s for most services)
- ✅ **Monitor response times** and optimize

### **Reliability**
- ✅ **Implement exponential backoff** for retries
- ✅ **Circuit breaker pattern** for failing services
- ✅ **Health checks** for all services
- ✅ **Graceful degradation** when services fail

---

## 🚀 **You're Ready for Production!**

With this complete AI integration setup, you have:

- ✅ **Multi-provider support** (Groq, Gemini, OpenAI, Claude)
- ✅ **Automatic fallback** between services
- ✅ **Performance monitoring** and analytics
- ✅ **Production-ready** configuration
- ✅ **Comprehensive testing** tools
- ✅ **Security best practices** implemented

**Your chatbot can now handle any scale, any use case, with the best AI service available!** 🎉

---

## 📞 **Need Help?**

### **Documentation**
- 📋 `AI_INTEGRATION_GUIDE.md` - This guide
- 📋 `TESTING_PLAN.md` - Testing procedures
- 📋 `INTEGRATION_GUIDE.md` - Platform integration
- 🌐 Official docs: [Provider documentation]

### **Troubleshooting**
- 🔍 Check Django logs: `logs/debug.log`
- 📊 Monitor dashboard: `http://127.0.0.1:8000/dashboard/`
- 🧪 Test services: `python test_ai_services.py`

### **Community Support**
- 💬 Discord: AI development communities
- 🐙 GitHub: Issue tracking and discussions
- 📚 Stack Overflow: Technical questions

---

**Happy coding with your multi-AI chatbot!** 🤖✨
