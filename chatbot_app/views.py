from django.shortcuts import render
from django.conf import settings
import google.generativeai as genai
from django.http import JsonResponse

# Create your views here.

def index(request):
    genai.configure(api_key=settings.GEMINI_API_KEY)
    if request.method == 'GET':
        return render(request, 'chatbot_app/index.html')

    elif request.method == 'POST':
       user_input = request.POST.get('user-input')

       model = genai.GenerativeModel('gemini-1.5-flash-latest')

       response = model.generate_content(user_input)

       gemini_response = response.text

       return JsonResponse({'message': gemini_response})