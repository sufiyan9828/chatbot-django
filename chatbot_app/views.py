from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from google import genai
from google.genai import errors
import httpx
import traceback

def index(request):
    if request.method == 'GET':
        return render(request, 'chatbot_app/index.html')

    elif request.method == 'POST':
        user_input = request.POST.get('user-input')
        
        try:
            # Increase timeout to 60s to handle the SSL handshake timeout
            client = genai.Client(
                api_key=settings.GEMINI_API_KEY,
                http_options={'timeout': 60.0}
            )
            
            # Use the stable gemini-2.0-flash model from your dashboard
            response = client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=user_input
            )
            
            return JsonResponse({'message': response.text})
            
        except (httpx.ConnectTimeout, httpx.ReadTimeout):
            # Prevents 500 error when the network handshakes fail
            return JsonResponse({
                'error': 'Connection timed out. Please check your network and retry.'
            }, status=504)
            
        except errors.ClientError as e:
            # Specifically handles the 429 RESOURCE_EXHAUSTED error
            if e.status_code == 429:
                return JsonResponse({
                    'error': 'Quota exceeded. Please wait 30 seconds.'
                }, status=429)
            return JsonResponse({'error': f"API Error: {str(e)}"}, status=e.status_code)
            
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'error': 'An internal server error occurred.'}, status=500)