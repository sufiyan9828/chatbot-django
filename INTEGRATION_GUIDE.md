# 🚀 Chatbot Integration Guide

Connect your chatbot to multiple platforms and reach users everywhere!

## 🌐 Website Integration (Easiest)

### Quick Embed Code
```html
<!-- Add this before your closing </body> tag -->
<script src="http://127.0.0.1:8000/embed/"></script>
```

### What it does:
- ✅ Floating chat widget on your website
- ✅ Matches your chatbot's personality and design
- ✅ Works on all devices (mobile, tablet, desktop)
- ✅ No coding required - just copy & paste

### Customization Options:
- Position (bottom-right, bottom-left, etc.)
- Colors and branding
- Size and animations
- Welcome message

---

## 📱 Facebook Messenger Integration

### Setup Steps:

1. **Create Facebook Assets**
   - Go to [Facebook Developers](https://developers.facebook.com/)
   - Create a new app with "Messenger" product
   - Create a Facebook Page for your business

2. **Configure Webhook**
   - Webhook URL: `http://127.0.0.1:8000/api/webhook/`
   - Verify token: `your_verification_token_here`
   - Subscribe to: `messages`, `messaging_postbacks`

3. **Get Access Token**
   - Generate Page Access Token
   - Store it securely in your environment

4. **Test Integration**
   - Send a message to your Facebook Page
   - Should receive responses from your chatbot

### Required Files:
```python
# Add to your .env file
FACEBOOK_PAGE_ACCESS_TOKEN=your_page_access_token
FACEBOOK_VERIFY_TOKEN=your_verify_token
```

---

## 📞 WhatsApp Business Integration

### Setup Steps:

1. **Get WhatsApp Business API**
   - Apply for [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp/)
   - Get approved for business use
   - Set up WhatsApp Business Account

2. **Configure Webhook**
   - Webhook URL: `http://127.0.0.1:8000/api/webhook/`
   - Set up phone number and message templates

3. **Test Messages**
   - Send test messages via WhatsApp
   - Verify webhook receives messages

### Message Templates Required:
- `welcome_message` - Initial greeting
- `response_message` - Chatbot responses
- `fallback_message` - Error handling

---

## 🔌 Direct API Integration

### Endpoint Information:
- **URL**: `http://127.0.0.1:8000/api/webhook/`
- **Method**: `POST`
- **Content-Type**: `application/json`

### Request Format:
```json
{
  "message": "Hello, how can you help me?",
  "platform": "custom_platform",
  "user_id": "user_12345"
}
```

### Response Format:
```json
{
  "response": "Hey there! I'm here to help you with...",
  "platform": "custom_platform",
  "user_id": "user_12345",
  "timestamp": "2026-02-14T15:30:00Z"
}
```

### Integration Examples:

#### Python
```python
import requests

def send_message_to_chatbot(message, user_id):
    response = requests.post(
        'http://127.0.0.1:8000/api/webhook/',
        json={
            'message': message,
            'platform': 'python_app',
            'user_id': user_id
        }
    )
    return response.json()
```

#### JavaScript
```javascript
async function sendMessage(message, userId) {
    const response = await fetch('http://127.0.0.1:8000/api/webhook/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: message,
            platform: 'web_app',
            user_id: userId
        })
    });
    return await response.json();
}
```

#### cURL
```bash
curl -X POST http://127.0.0.1:8000/api/webhook/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello bot!",
    "platform": "curl_test",
    "user_id": "test_user"
  }'
```

---

## 🛠️ Advanced Integration Options

### Custom Platform Integration
- Use the API endpoint for any custom platform
- Support for Slack, Discord, Telegram, etc.
- Custom branding and user experience

### Enterprise Features
- Rate limiting and throttling
- User authentication and sessions
- Analytics and usage tracking
- Custom AI model integration

### Deployment Considerations
- Use HTTPS in production
- Set up proper CORS headers
- Implement authentication
- Monitor webhook health

---

## 📊 Testing Your Integration

### Test API Endpoint:
```bash
# Test the webhook directly
curl -X POST http://127.0.0.1:8000/api/webhook/ \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "platform": "test", "user_id": "test"}'
```

### Test Embed Code:
1. Create a simple HTML file
2. Add the embed script
3. Open in browser
4. Test sending messages

### Monitor Integration:
- Check Django admin for message logs
- Monitor API response times
- Track user engagement
- Set up error alerts

---

## 🆘 Troubleshooting

### Common Issues:
1. **CORS Errors**: Add CORS headers to your Django app
2. **SSL/HTTPS**: Required for Facebook/WhatsApp in production
3. **Webhook Verification**: Ensure tokens match exactly
4. **Rate Limits**: Don't exceed platform limits

### Debug Tools:
- Django admin logs
- Browser developer tools
- API testing tools (Postman, Insomnia)
- Platform developer dashboards

---

## 📞 Need Help?

- **Documentation**: Check the `README_TROUBLESHOOTING.md`
- **API Testing**: Visit `/integrations/` endpoint for live testing
- **Health Check**: Monitor `/health/` endpoint
- **Support**: Check logs in Django admin

---

## 🎉 Ready to Launch!

Your chatbot is now ready to connect with users across multiple platforms! Choose the integration that best fits your needs and start engaging with your audience.

**Recommended Order:**
1. Start with Website Embed (easiest)
2. Add Facebook Messenger (largest audience)
3. Consider WhatsApp (business users)
4. Build custom integrations (advanced)

Happy chatting! 🚀
