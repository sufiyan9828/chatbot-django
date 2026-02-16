from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Avg
from datetime import datetime, timedelta
import json
import logging
import traceback
import asyncio
from .fallback_responses import fallback
from .ai_services import ai_manager, orchestrator
from .models import ChatMessage, ChatSession, AIServiceUsage

logger = logging.getLogger(__name__)


def index(request):
    if request.method == "GET":
        return render(request, "chatbot_app/index.html")

    elif request.method == "POST":
        user_input = (request.POST.get("user-input") or "").strip()

        if not user_input:
            return JsonResponse(
                {
                    "message": fallback.get_response("help"),
                    "fallback": True,
                    "fallback_reason": "empty_input",
                },
                status=200,
            )

        try:
            # Use the Orchestrator to route and generate response
            result = asyncio.run(orchestrator.route_and_generate(user_input))

            return JsonResponse(
                {"message": result["response"], "agent": result["agent"]}
            )

        except Exception as e:
            # Log the error with traceback and use fallback response
            logger.error(f"AI service error: {str(e)}\n{traceback.format_exc()}")
            fallback_message = fallback.get_response(user_input)
            return JsonResponse(
                {
                    "message": fallback_message,
                    "fallback": True,
                    "fallback_reason": str(e),
                },
                status=200,
            )


@csrf_exempt
@require_http_methods(["POST"])
def api_webhook(request):
    """API endpoint for external platform integrations"""
    try:
        data = json.loads(request.body)

        # Extract message and platform info
        message = data.get("message", "")
        platform = data.get("platform", "unknown")
        user_id = data.get("user_id", "anonymous")

        if not message:
            return JsonResponse({"error": "No message provided"}, status=400)

        # Use the Orchestrator to route and generate response
        result = asyncio.run(orchestrator.route_and_generate(message))

        return JsonResponse(
            {
                "response": result["response"],
                "agent": result["agent"],
                "suggestions": result.get("suggestions", []),
                "charts": result.get("charts", []),
                "platform": platform,
                "user_id": user_id,
                "timestamp": json.dumps({"timestamp": "auto"}),
            }
        )

    except Exception as e:
        logger.error(f"Webhook error: {str(e)}\n{traceback.format_exc()}")
        user_msg = message if "message" in locals() else "hello"
        fallback_message = fallback.get_response(user_msg)
        return JsonResponse(
            {"response": fallback_message, "fallback": True, "fallback_reason": str(e)},
            status=200,
        )

        return JsonResponse(
            {"response": fallback_message, "fallback": True, "fallback_reason": str(e)},
            status=200,
        )


@csrf_exempt
@require_http_methods(["POST"])
def transcribe_audio(request):
    """API endpoint for audio transcription"""
    try:
        if "audio" not in request.FILES:
            return JsonResponse({"error": "No audio file provided"}, status=400)

        audio_file = request.FILES["audio"]

        # Use the AI manager to transcribe
        text = asyncio.run(ai_manager.transcribe_audio(audio_file))

        return JsonResponse({"text": text})

    except Exception as e:
        logger.error(f"Transcription error: {str(e)}\n{traceback.format_exc()}")
        return JsonResponse({"error": str(e)}, status=500)


def embed_code(request):
    """Return HTML embed code for websites"""
    embed_script = """
<!-- Chatbot Embed Code -->
<script>
(function() {
    var chatbotContainer = document.createElement('div');
    chatbotContainer.id = 'chatbot-embed';
    chatbotContainer.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 350px;
        height: 500px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.12);
        z-index: 10000;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        transition: all 0.3s ease;
    `;
    
    chatbotContainer.innerHTML = `
        <style>
            .chat-widget { height: 100%; display: flex; flex-direction: column; }
            .chat-header { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; padding: 15px; border-radius: 12px 12px 0 0;
                display: flex; justify-content: space-between; align-items: center;
            }
            .chat-body { flex: 1; padding: 15px; overflow-y: auto; }
            .chat-input { 
                padding: 15px; border-top: 1px solid #eee; 
                display: flex; gap: 10px; 
            }
            .chat-input input { flex: 1; padding: 8px; border: 1px solid #ddd; border-radius: 20px; }
            .chat-input button { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; border: none; padding: 8px 15px; border-radius: 20px; cursor: pointer;
            }
            .minimize-btn { background: none; border: none; color: white; cursor: pointer; font-size: 18px; }
            .chat-message { 
                margin: 10px 0; padding: 8px 12px; border-radius: 12px; max-width: 80%;
            }
            .user-message { background: #e3f2fd; margin-left: auto; text-align: right; }
            .bot-message { background: #f3e5f5; }
        </style>
        <div class="chat-widget">
            <div class="chat-header">
                <span>🤖 Your Assistant</span>
                <button class="minimize-btn" onclick="toggleChat()">−</button>
            </div>
            <div class="chat-body" id="chat-messages">
                <div class="chat-message bot-message">👋 Hey there! How can I help you today?</div>
            </div>
            <div class="chat-input">
                <input type="text" id="chat-input" placeholder="Type a message..." onkeypress="if(event.key==='Enter') sendMessage()">
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(chatbotContainer);
    
    window.toggleChat = function() {
        var container = document.getElementById('chatbot-embed');
        if (container.style.height === '60px') {
            container.style.height = '500px';
        } else {
            container.style.height = '60px';
        }
    };
    
    window.sendMessage = function() {
        var input = document.getElementById('chat-input');
        var messages = document.getElementById('chat-messages');
        var message = input.value.trim();
        
        if (!message) return;
        
        // Add user message
        var userMsg = document.createElement('div');
        userMsg.className = 'chat-message user-message';
        userMsg.textContent = message;
        messages.appendChild(userMsg);
        
        input.value = '';
        
        // Send to server
        fetch('YOUR_CHATBOT_URL/api/webhook/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                platform: 'website',
                user_id: 'website_user'
            })
        })
        .then(response => response.json())
        .then(data => {
            var botMsg = document.createElement('div');
            botMsg.className = 'chat-message bot-message';
            botMsg.textContent = data.response || 'Sorry, I had trouble processing that.';
            messages.appendChild(botMsg);
            messages.scrollTop = messages.scrollHeight;
        })
        .catch(error => {
            var botMsg = document.createElement('div');
            botMsg.className = 'chat-message bot-message';
            botMsg.textContent = 'Connection error. Please try again.';
            messages.appendChild(botMsg);
        });
        
        messages.scrollTop = messages.scrollHeight;
    };
})();
</script>
<!-- End Chatbot Embed Code -->
    """

    return HttpResponse(embed_script, content_type="text/html")


def integration_guide(request):
    """Return integration guide for different platforms"""
    guide = {
        "website": {
            "embed_code": f'<script src="{request.build_absolute_uri()}/embed/"></script>',
            "instructions": "Add this script to your website HTML before the closing </body> tag",
        },
        "facebook_messenger": {
            "webhook_url": f"{request.build_absolute_uri()}/api/webhook/",
            "instructions": [
                "1. Create a Facebook Page and Facebook Developer account",
                "2. Create a Facebook App with Messenger product",
                "3. Set webhook URL to: "
                + f"{request.build_absolute_uri()}/api/webhook/",
                "4. Verify webhook with your verification token",
                "5. Get Page Access Token and configure",
            ],
        },
        "whatsapp": {
            "webhook_url": f"{request.build_absolute_uri()}/api/webhook/",
            "instructions": [
                "1. Create a WhatsApp Business Account",
                "2. Get WhatsApp Business API access",
                "3. Set webhook URL to: "
                + f"{request.build_absolute_uri()}/api/webhook/",
                "4. Configure phone number and message templates",
                "5. Test webhook endpoints",
            ],
        },
        "api": {
            "endpoint": f"{request.build_absolute_uri()}/api/webhook/",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "body_format": {
                "message": "user message",
                "platform": "platform_name",
                "user_id": "unique_user_identifier",
            },
        },
    }

    return JsonResponse(guide)


def dashboard_stats(request):
    """Return real-time dashboard statistics"""
    now = datetime.now()
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)

    # Message statistics
    messages_24h = ChatMessage.objects.filter(timestamp__gte=last_24h)
    messages_7d = ChatMessage.objects.filter(timestamp__gte=last_7d)

    # Session statistics
    active_sessions_24h = ChatSession.objects.filter(updated_at__gte=last_24h).count()
    total_sessions_7d = ChatSession.objects.filter(created_at__gte=last_7d).count()

    # AI Service statistics
    ai_services = AIServiceUsage.objects.all()

    # Performance metrics
    avg_response_time = (
        ai_services.aggregate(avg_time=Avg("avg_response_time_ms"))["avg_time"] or 0
    )

    # Error rate
    total_messages = messages_24h.count()
    fallback_messages = messages_24h.filter(is_fallback=True).count()
    error_rate = (fallback_messages / total_messages * 100) if total_messages > 0 else 0

    # Popular conversation flows
    popular_flows = {}
    user_messages = messages_24h.filter(message_type="user")

    flow_keywords = {
        "contact": ["contact", "phone", "email", "address"],
        "services": ["service", "offer", "provide"],
        "hours": ["hours", "time", "open", "close"],
        "location": ["location", "where", "direction"],
        "human": ["human", "person", "agent"],
    }

    for flow, keywords in flow_keywords.items():
        count = 0
        for msg in user_messages:
            if any(keyword in msg.content.lower() for keyword in keywords):
                count += 1
        popular_flows[flow] = count

    # AI Service status
    ai_status = {
        "gemini_available": getattr(ai_manager, "gemini_available", False),
        "openrouter_available": getattr(ai_manager, "openrouter_available", False),
        "fallback_active": not (
            getattr(ai_manager, "gemini_available", False)
            or getattr(ai_manager, "openrouter_available", False)
        ),
    }

    stats = {
        "messages": {
            "last_24h": total_messages,
            "last_7d": messages_7d.count(),
            "error_rate": round(error_rate, 2),
        },
        "sessions": {"active_24h": active_sessions_24h, "total_7d": total_sessions_7d},
        "performance": {
            "avg_response_time_ms": round(avg_response_time, 2),
            "total_requests": sum(service.request_count for service in ai_services),
        },
        "popular_flows": popular_flows,
        "ai_services": ai_status,
        "last_updated": now.isoformat(),
    }

    return JsonResponse(stats)


def dashboard_view(request):
    """Render dashboard HTML page"""
    return render(request, "chatbot_app/dashboard.html")
