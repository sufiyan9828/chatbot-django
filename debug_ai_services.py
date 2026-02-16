#!/usr/bin/env python3
"""
Debug script to test AI service initialization
"""

import os
import sys
import django

# Setup Django
sys.path.append('c:\\Users\\admin\\Desktop\\chatbot')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_project.settings')
django.setup()

from chatbot_app.ai_services import AIServiceManager

def test_ai_services():
    print("🔍 Debugging AI Services...")
    print("=" * 50)
    
    # Check environment variables
    gemini_key = os.getenv('GEMINI_API_KEY')
    groq_key = os.getenv('GROQ_API_KEY')
    openrouter_key = os.getenv('OPENROUTER_API_KEY')
    
    print(f"GEMINI_API_KEY: {'✅ Set' if gemini_key else '❌ Not set'}")
    print(f"GROQ_API_KEY: {'✅ Set' if groq_key else '❌ Not set'}")
    print(f"OPENROUTER_API_KEY: {'✅ Set' if openrouter_key else '❌ Not set'}")
    
    print("\n🤖 Initializing AI Service Manager...")
    
    try:
        manager = AIServiceManager()
        print(f"Services initialized: {len(manager.services)}")
        
        for i, service in enumerate(manager.services):
            service_name = service.__class__.__name__
            print(f"  {i+1}. {service_name}")
        
        if manager.services:
            print(f"\n✅ AI Services Available: {len(manager.services)}")
            print(f"Current service index: {manager.current_service_index}")
            
            # Test generating a response
            import asyncio
            
            async def test_response():
                try:
                    response = await manager.generate_response("Hello! How are you?")
                    print(f"\n🎯 Test Response: {response}")
                    return True
                except Exception as e:
                    print(f"\n❌ Test Failed: {e}")
                    return False
            
            success = asyncio.run(test_response())
            return success
            
        else:
            print("\n❌ No AI Services Available!")
            return False
            
    except Exception as e:
        print(f"\n❌ Initialization Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_ai_services()
    print("\n" + "=" * 50)
    if success:
        print("🎉 AI Services Working!")
    else:
        print("🔧 AI Services Need Fixing")
