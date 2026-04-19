from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Initialize Gemini
API_KEY = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
else:
    model = None

def chat_home(request):
    """Render the chat interface"""
    return render(request, 'chat/home.html')

@csrf_exempt
@require_http_methods(["POST"])
def send_message(request):
    """Handle chat messages"""
    try:
        if model is None:
            return JsonResponse({
                'success': False,
                'error': 'API key not configured'
            })
        
        data = json.loads(request.body)
        user_message = data.get('message', '')
        conversation_history = data.get('history', [])
        
        if not user_message:
            return JsonResponse({
                'success': False,
                'error': 'Message is empty'
            })
        
        # Build conversation context
        context = ""
        for msg in conversation_history[-10:]:
            role = "User" if msg.get('role') == 'user' else "Assistant"
            content = msg.get('content', '')
            context += f"{role}: {content}\n"
        
        prompt = f"""You are ChatGPT, a helpful AI assistant.

Current conversation:
{context}
User: {user_message}
Assistant:"""
        
        response = model.generate_content(prompt)
        
        return JsonResponse({
            'success': True,
            'response': response.text
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })