"""
Fallback response system for when the Gemini API is unavailable.
Provides basic conversational responses with personality.
"""

import random
from typing import Dict, List

class FallbackResponses:
    """Fallback response generator for basic chatbot functionality."""
    
    def __init__(self):
        self.responses = {
            'greetings': [
                "👋 Hey there! Welcome! I'm so excited to help you today! What can I do for you?",
                "Hi! Welcome to our space! I'm here and ready to assist you. What brings you here?",
                "Hello! Welcome! I'm your friendly assistant, ready to help. How can I make your day better?",
                "Hey! Welcome! I'm thrilled you're here! What can I help you with today?",
            ],
            'goodbyes': [
                "Bye! Have an amazing day! Come back anytime! 😊",
                "See you later! Take care and stay awesome! 👋",
                "Farewell! Feel free to visit us again soon! 🌟",
                "Bye! It was great chatting with you! Have a wonderful day! 💫",
            ],
            'thanks': [
                "You're absolutely welcome! Is there anything else I can help you with? 😊",
                "My pleasure! What else would you love to know? 🤗",
                "You're so welcome! How else can I assist you today? 💝",
                "Happy to help! What's next on your mind? 🎯",
            ],
            'how_are_you': [
                "I'm feeling fantastic! Thanks for asking! Ready to help you with anything! 🚀",
                "I'm doing great! Fully charged and ready to assist! What can I help you with? ⚡",
                "I'm awesome! Thanks for checking! How can I make your day better? ✨",
                "I'm doing wonderfully! Ready to rock and roll! What do you need? 🎸",
            ],
            'help': [
                "🤝 I'm here to help! You can ask me about: Contact info, Services, Hours, Location, or connect with a human! What interests you?",
                "I'm your friendly assistant! I can help with contact details, services, business hours, location, and more! What's on your mind?",
                "Ready to help! I've got info on contact, services, hours, location, and human support! What would you like to explore?",
                "I'm here for you! Ask me about our contact info, services, hours, location, or talk to a human! What sounds good?",
            ],
            'main_menu': [
                "🏠 Here's our main menu! Pick your adventure: 📞 Contact | 💼 Services | ⏰ Hours | 📍 Location | 💬 Human Support. What's your choice?",
                "Welcome! Let's get you sorted! Choose: Contact, Services, Hours, Location, or Human Support! What sounds good?",
                "Hey! What can I help you with today? 📞 Contact | 💼 Services | ⏰ Hours | 📍 Location | 💬 Human Support! Pick one!",
                "Ready to assist! Choose your path: Contact info, Services, Hours, Location, or Human Support! What would you like?",
            ],
            'contact': [
                "📞 Here's how to reach us! 📧 support@example.com | 📱 +1 (555) 123-4567 | 🕐 Mon-Fri 9AM-6PM EST | 📍 123 Business Street, Suite 100. Need more info?",
                "Get in touch! 📧 support@example.com | 📱 +1 (555) 123-4567 | 📍 123 Business Street, Suite 100. We're here Mon-Fri 9AM-6PM EST! How else can I help?",
            ],
            'services': [
                "💼 We offer amazing services! 🎯 Consulting | 🔧 24/7 Tech Support | 📊 Data Analysis | 🚀 Project Management | 💡 Training. Which one sparks your interest?",
                "Our services rock! We do consulting, tech support, data analysis, project management, and training! What would you like to know more about?",
            ],
            'hours': [
                "⏰ Our hours! 📅 Mon-Fri 9AM-6PM EST | 🌙 Sat 10AM-4PM EST | ❌ Sun Closed | 🚨 Emergency support: 24/7 for premium clients! When works for you?",
                "Here's when we're open! Mon-Fri 9AM-6PM EST, Sat 10AM-4PM EST, closed Sundays. Premium clients get 24/7 emergency support! When would you like to connect?",
            ],
            'location': [
                "📍 Find us at 123 Business Street, Suite 100! 🚗 Free parking | 🚌 Bus stop 2 blocks away | ✈️ 15 min from airport. Need directions from your spot?",
                "We're at 123 Business Street, Suite 100! Free parking available, bus stop nearby, close to airport! Need specific directions?",
            ],
            'human_support': [
                "💬 Let's connect you with a human! 📞 +1 (555) 123-4567 (Mon-Fri 9AM-6PM EST) | 📧 support@example.com | 💻 Live chat on our website! They'll give you personalized help! Anything else while you wait?",
                "I'll get you to a human! Call +1 (555) 123-4567 or email support@example.com! Our team is amazing and ready to help Mon-Fri 9AM-6PM EST! What can I help with in the meantime?",
            ],
            'unknown': [
                "That sounds interesting! Tell me more about that! 🤔",
                "I'd love to help with that! Can you give me more details? 💭",
                "Great question! Let me think about how I can best assist you! 🤗",
                "I'm here to help! Could you rephrase that or give me more context? 🎯",
                "Thanks for sharing! What would you like to know about it? 🌟",
                "That's fascinating! How can I help you with this topic? ✨",
            ]
        }
    
    def get_response(self, user_input: str) -> str:
        """Get a fallback response based on user input."""
        user_input_lower = user_input.lower().strip()
        
        # Check for greetings
        if any(word in user_input_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return random.choice(self.responses['greetings'])
        
        # Check for goodbyes
        if any(word in user_input_lower for word in ['bye', 'goodbye', 'see you', 'farewell']):
            return random.choice(self.responses['goodbyes'])
        
        # Check for thanks
        if any(word in user_input_lower for word in ['thank', 'thanks', 'appreciate']):
            return random.choice(self.responses['thanks'])
        
        # Check for "how are you"
        if any(phrase in user_input_lower for phrase in ['how are you', 'how do you do', 'how are you doing']):
            return random.choice(self.responses['how_are_you'])
        
        # Check for main menu requests
        if any(word in user_input_lower for word in ['menu', 'main menu', 'options', 'start', 'begin']):
            return random.choice(self.responses['main_menu'])
        
        # Check for contact information
        if any(word in user_input_lower for word in ['contact', 'phone', 'email', 'address', 'reach']):
            return random.choice(self.responses['contact'])
        
        # Check for services
        if any(word in user_input_lower for word in ['service', 'services', 'offer', 'provide', 'consulting', 'support']):
            return random.choice(self.responses['services'])
        
        # Check for business hours
        if any(word in user_input_lower for word in ['hours', 'time', 'schedule', 'open', 'close', 'available']):
            return random.choice(self.responses['hours'])
        
        # Check for location
        if any(word in user_input_lower for word in ['location', 'direction', 'address', 'where', 'find', 'parking']):
            return random.choice(self.responses['location'])
        
        # Check for human support
        if any(word in user_input_lower for word in ['human', 'person', 'agent', 'representative', 'talk to someone', 'live person']):
            return random.choice(self.responses['human_support'])
        
        # Check for help requests
        if any(word in user_input_lower for word in ['help', 'assist', 'support']):
            return random.choice(self.responses['help'])
        
        # Default response for unknown inputs
        return random.choice(self.responses['unknown'])

# Global instance
fallback = FallbackResponses()
