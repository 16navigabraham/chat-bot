"""
Enhanced WhatsApp Chatbot for University Presentation
Smart fallback system - Works even without AI APIs!
Looks impressive for demo even if quota is exhausted
"""

from flask import Flask, request, render_template_string
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime, timedelta
import json
import random
import re
import time
import hashlib

app = Flask(__name__)

# Try to import AI libraries (optional)
AI_AVAILABLE = False
try:
    from google import genai
    from google.genai.types import GenerateContentConfig
    GEMINI_API_KEY = "your gemini api key here"
    client = genai.Client(api_key=GEMINI_API_KEY)
    AI_AVAILABLE = True
    AI_PROVIDER = "Gemini"
except:
    print("⚠️  AI API not available - Running in Smart Fallback Mode")
    AI_PROVIDER = "Smart Fallback"

# Data storage
conversations = {}
message_log = []
stats = {
    "total_messages": 0,
    "total_users": 0,
    "total_ai_calls": 0,
    "total_fallback_calls": 0,
    "total_cached_calls": 0,
    "total_rate_limited": 0,
    "start_time": datetime.now()
}

# Rate Limiting & Caching
RATE_LIMIT = {
    "max_requests_per_minute": 10,  # Adjust based on your quota
    "max_requests_per_hour": 100,   # Adjust based on your quota
    "request_timestamps": [],
    "cooldown_until": None,
    "api_disabled_until": None,
    "consecutive_failures": 0,
    "backoff_seconds": 60
}

RESPONSE_CACHE = {}  # Cache responses to reduce API calls
CACHE_DURATION = 300  # 5 minutes cache

FEATURES = {
    "sentiment": True,
    "quick_replies": True,
    "typing_indicator": True,
    "rate_limiting": True,
    "response_caching": True,
}


# ==================================================================
# INTELLIGENT RESPONSE SYSTEM - Works without AI!
# ==================================================================

KNOWLEDGE_BASE = {
    # Greetings
    "greeting": {
        "patterns": ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "howdy", "sup", "yo"],
        "responses": [
            "👋 Hello! I'm your AI assistant. How can I help you today?",
            "Hi there! 😊 What can I do for you?",
            "Hey! Great to hear from you! What's on your mind?",
            "Hello! 🌟 Ready to assist you. What do you need?",
        ]
    },
    
    # Questions about AI/Bot
    "who_are_you": {
        "patterns": ["who are you", "what are you", "tell me about yourself", "your name"],
        "responses": [
            "I'm an AI-powered WhatsApp chatbot! 🤖 I can answer questions, have conversations, and help with various tasks. What would you like to know?",
            "I'm your friendly AI assistant! Built with Python, Flask, and powered by machine learning. How can I assist you today? 😊",
        ]
    },
    
    # General Knowledge
    "geography": {
        "patterns": ["usa in africa", "is usa in africa", "where is usa", "usa location", "america continent"],
        "responses": [
            "No, the USA is not in Africa! 🌍 The United States is in North America, while Africa is a separate continent. They're on different sides of the Atlantic Ocean. Would you like to know more about geography?",
        ]
    },
    
    "capitals": {
        "patterns": ["capital of", "capital city"],
        "responses": [
            "🏛️ I can help with capitals! Some examples: USA - Washington D.C., UK - London, France - Paris, Nigeria - Abuja. Which country's capital would you like to know?",
        ]
    },
    
    # Jokes
    "joke": {
        "patterns": ["joke", "make me laugh", "funny", "humor"],
        "responses": [
            "Why don't scientists trust atoms? Because they make up everything! 😄",
            "What do you call a bear with no teeth? A gummy bear! 🐻",
            "Why did the scarecrow win an award? He was outstanding in his field! 🌾",
            "What do you call a fake noodle? An impasta! 🍝",
            "Why don't eggs tell jokes? They'd crack each other up! 🥚",
            "What did the ocean say to the beach? Nothing, it just waved! 🌊",
        ]
    },
    
    # Facts
    "fact": {
        "patterns": ["fact", "tell me something interesting", "did you know"],
        "responses": [
            "🧠 Did you know? Honey never spoils! Archaeologists have found 3000-year-old honey in Egyptian tombs that's still edible!",
            "🌊 Fun fact: The Atlantic Ocean is saltier than the Pacific Ocean!",
            "🐙 Cool fact: Octopuses have three hearts and blue blood!",
            "☀️ Amazing fact: It takes sunlight 8 minutes and 20 seconds to reach Earth!",
            "🦒 Interesting fact: A giraffe's tongue is about 20 inches long!",
        ]
    },
    
    # Help with topics
    "explain": {
        "patterns": ["explain", "what is", "define", "tell me about", "how does"],
        "responses": [
            "I'd be happy to explain! 📚 Could you be more specific about what topic you'd like me to explain? For example, ask 'What is AI?' or 'Explain how computers work'.",
        ]
    },
    
    # Time/Date
    "time": {
        "patterns": ["time", "what time", "current time"],
        "responses": [
            f"⏰ The current time is: {datetime.now().strftime('%I:%M %p')}",
        ]
    },
    
    "date": {
        "patterns": ["date", "what date", "today", "day"],
        "responses": [
            f"📅 Today is: {datetime.now().strftime('%B %d, %Y (%A)')}",
        ]
    },
    
    # Math help
    "math": {
        "patterns": ["calculate", "math", "plus", "minus", "times", "divide", "+", "-", "*", "/"],
        "responses": [
            "🔢 I can help with math! Try asking me something like '2 + 2' or 'what is 15 times 3?'",
        ]
    },
    
    # Thanks
    "thanks": {
        "patterns": ["thank", "thanks", "thx", "appreciate"],
        "responses": [
            "You're welcome! 😊 Happy to help!",
            "No problem! That's what I'm here for! 🙌",
            "Anytime! Feel free to ask more questions! 💪",
        ]
    },
    
    # Goodbye
    "goodbye": {
        "patterns": ["bye", "goodbye", "see you", "later", "gotta go"],
        "responses": [
            "Goodbye! 👋 Have a great day!",
            "See you later! Come back anytime! 😊",
            "Take care! 🌟 Feel free to chat again soon!",
        ]
    },
}


def log_message(phone, message, response, msg_type="user"):
    """Log all messages for analytics"""
    message_log.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "phone": phone[-4:],
        "type": msg_type,
        "message": message,
        "response": response
    })
    stats["total_messages"] += 1


def get_sentiment(text):
    """Simple sentiment analysis"""
    positive_words = ["good", "great", "awesome", "excellent", "happy", "love", "best", "thanks"]
    negative_words = ["bad", "terrible", "awful", "hate", "worst", "sad", "angry", "disappointed"]
    
    text_lower = text.lower()
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)
    
    if pos_count > neg_count:
        return "😊 Positive"
    elif neg_count > pos_count:
        return "😔 Negative"
    return "😐 Neutral"


def calculate_expression(message):
    """Try to solve simple math expressions"""
    try:
        # Extract numbers and operators
        pattern = r'(\d+\.?\d*)\s*([\+\-\*/])\s*(\d+\.?\d*)'
        match = re.search(pattern, message)
        
        if match:
            num1, operator, num2 = float(match.group(1)), match.group(2), float(match.group(3))
            
            if operator == '+':
                result = num1 + num2
            elif operator == '-':
                result = num1 - num2
            elif operator == '*' or operator == 'x':
                result = num1 * num2
            elif operator == '/':
                result = num1 / num2 if num2 != 0 else "undefined (can't divide by zero)"
            
            return f"🔢 {num1} {operator} {num2} = {result}"
    except:
        pass
    return None


def get_cache_key(message):
    """Generate cache key from message"""
    return hashlib.md5(message.lower().strip().encode()).hexdigest()


def get_cached_response(message):
    """Check if we have a cached response"""
    if not FEATURES["response_caching"]:
        return None
    
    cache_key = get_cache_key(message)
    if cache_key in RESPONSE_CACHE:
        cached = RESPONSE_CACHE[cache_key]
        if datetime.now() < cached["expires"]:
            stats["total_cached_calls"] += 1
            print("✅ Using cached response")
            return cached["response"]
        else:
            del RESPONSE_CACHE[cache_key]
    return None


def cache_response(message, response):
    """Cache a response"""
    if not FEATURES["response_caching"]:
        return
    
    cache_key = get_cache_key(message)
    RESPONSE_CACHE[cache_key] = {
        "response": response,
        "expires": datetime.now() + timedelta(seconds=CACHE_DURATION)
    }


def is_rate_limited():
    """Check if we're currently rate limited"""
    if not FEATURES["rate_limiting"]:
        return False
    
    now = datetime.now()
    
    # Check if API is disabled due to quota exhaustion
    if RATE_LIMIT["api_disabled_until"]:
        if now < RATE_LIMIT["api_disabled_until"]:
            remaining = (RATE_LIMIT["api_disabled_until"] - now).total_seconds()
            print(f"⏳ API disabled for {int(remaining)}s due to quota exhaustion")
            return True
        else:
            # Re-enable API
            RATE_LIMIT["api_disabled_until"] = None
            RATE_LIMIT["consecutive_failures"] = 0
            RATE_LIMIT["backoff_seconds"] = 60
            print("✅ API re-enabled after cooldown")
    
    # Check cooldown
    if RATE_LIMIT["cooldown_until"]:
        if now < RATE_LIMIT["cooldown_until"]:
            remaining = (RATE_LIMIT["cooldown_until"] - now).total_seconds()
            print(f"⏳ Rate limit cooldown: {int(remaining)}s remaining")
            return True
        else:
            RATE_LIMIT["cooldown_until"] = None
    
    # Clean old timestamps
    cutoff_minute = now - timedelta(minutes=1)
    cutoff_hour = now - timedelta(hours=1)
    RATE_LIMIT["request_timestamps"] = [
        ts for ts in RATE_LIMIT["request_timestamps"] 
        if ts > cutoff_hour
    ]
    
    # Check per-minute limit
    recent_minute = [ts for ts in RATE_LIMIT["request_timestamps"] if ts > cutoff_minute]
    if len(recent_minute) >= RATE_LIMIT["max_requests_per_minute"]:
        RATE_LIMIT["cooldown_until"] = now + timedelta(seconds=10)
        print(f"⚠️  Per-minute rate limit hit ({len(recent_minute)} requests)")
        stats["total_rate_limited"] += 1
        return True
    
    # Check per-hour limit
    recent_hour = RATE_LIMIT["request_timestamps"]
    if len(recent_hour) >= RATE_LIMIT["max_requests_per_hour"]:
        RATE_LIMIT["cooldown_until"] = now + timedelta(minutes=5)
        print(f"⚠️  Per-hour rate limit hit ({len(recent_hour)} requests)")
        stats["total_rate_limited"] += 1
        return True
    
    return False


def record_api_request():
    """Record an API request"""
    RATE_LIMIT["request_timestamps"].append(datetime.now())


def handle_api_error(error_msg):
    """Handle API errors and implement exponential backoff"""
    RATE_LIMIT["consecutive_failures"] += 1
    
    # Check for quota exhaustion
    if "429" in str(error_msg) or "RESOURCE_EXHAUSTED" in str(error_msg) or "quota" in str(error_msg).lower():
        # Increase backoff exponentially
        backoff = min(RATE_LIMIT["backoff_seconds"] * (2 ** (RATE_LIMIT["consecutive_failures"] - 1)), 3600)
        RATE_LIMIT["api_disabled_until"] = datetime.now() + timedelta(seconds=backoff)
        RATE_LIMIT["backoff_seconds"] = backoff
        stats["total_rate_limited"] += 1
        print(f"🚫 Quota exhausted! API disabled for {int(backoff)}s (attempt {RATE_LIMIT['consecutive_failures']})")
    elif RATE_LIMIT["consecutive_failures"] >= 3:
        # After 3 consecutive failures, temporary disable
        RATE_LIMIT["api_disabled_until"] = datetime.now() + timedelta(seconds=120)
        print(f"🚫 Multiple API failures! Disabling for 2 minutes")


def get_smart_response(message, phone):
    """Intelligent response without AI API"""
    message_lower = message.lower()
    
    # Try to calculate if it's math
    math_result = calculate_expression(message)
    if math_result:
        return math_result
    
    # Check knowledge base
    for category, data in KNOWLEDGE_BASE.items():
        for pattern in data["patterns"]:
            if pattern in message_lower:
                response = random.choice(data["responses"])
                
                # Handle dynamic responses
                if category == "time":
                    response = f"⏰ The current time is: {datetime.now().strftime('%I:%M %p')}"
                elif category == "date":
                    response = f"📅 Today is: {datetime.now().strftime('%B %d, %Y (%A)')}"
                
                return response
    
    # Default intelligent response
    default_responses = [
        "That's an interesting question! 🤔 While I don't have specific information about that right now, I'm here to help with general questions, jokes, facts, and math!",
        "I understand your query! While my knowledge is limited in that area, try asking me for a joke, a fact, or some simple math! 📚",
        f"You asked: '{message}' - Great question! Try asking about time, date, jokes, or facts. I'm constantly learning! 🧠",
    ]
    
    return random.choice(default_responses)


def get_ai_response(message, phone):
    """Try AI first, fall back to smart responses"""
    try:
        # Initialize conversation
        if phone not in conversations:
            conversations[phone] = []
            stats["total_users"] += 1
        
        sentiment = get_sentiment(message) if FEATURES["sentiment"] else ""
        
        # Check cache first
        cached_response = get_cached_response(message)
        if cached_response:
            conversations[phone].append({"role": "user", "content": message})
            conversations[phone].append({"role": "assistant", "content": cached_response})
            conversations[phone] = conversations[phone][-10:]
            log_message(phone, message, cached_response + " [CACHED]", "cached")
            return cached_response, sentiment
        
        # Check if rate limited
        if is_rate_limited():
            smart_response = get_smart_response(message, phone)
            stats["total_fallback_calls"] += 1
            conversations[phone].append({"role": "user", "content": message})
            conversations[phone].append({"role": "assistant", "content": smart_response})
            conversations[phone] = conversations[phone][-10:]
            log_message(phone, message, smart_response + " [RATE LIMITED]", "smart")
            return smart_response, sentiment
        
        # Try AI if available
        if AI_AVAILABLE:
            conversation_history = ""
            for msg in conversations[phone][-6:]:
                role = "User" if msg["role"] == "user" else "Assistant"
                conversation_history += f"{role}: {msg['content']}\n"
            
            prompt = f"""You are a friendly and helpful AI assistant in a WhatsApp chat. 
Keep responses concise (2-3 sentences max). 
Use emojis occasionally. Be conversational and warm.

Previous conversation:
{conversation_history}

Current message from User: {message}

Your response:"""
            
            # Record request for rate limiting
            record_api_request()
            
            response = client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=prompt,
                config=GenerateContentConfig(
                    temperature=0.8,
                    max_output_tokens=200,
                )
            )
            
            ai_message = response.text.strip()
            stats["total_ai_calls"] += 1
            RATE_LIMIT["consecutive_failures"] = 0  # Reset failure counter on success
            
            # Cache the response
            cache_response(message, ai_message)
            
            conversations[phone].append({"role": "user", "content": message})
            conversations[phone].append({"role": "assistant", "content": ai_message})
            conversations[phone] = conversations[phone][-10:]
            
            log_message(phone, message, ai_message, "ai")
            return ai_message, sentiment
        
    except Exception as e:
        error_msg = str(e)
        print(f"⚠️  AI error: {error_msg[:200]}")
        handle_api_error(error_msg)
    
    # Smart fallback (looks like AI!)
    smart_response = get_smart_response(message, phone)
    stats["total_fallback_calls"] += 1
    
    conversations[phone].append({"role": "user", "content": message})
    conversations[phone].append({"role": "assistant", "content": smart_response})
    conversations[phone] = conversations[phone][-10:]
    
    log_message(phone, message, smart_response, "smart")
    return smart_response, sentiment


@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    """Handle incoming WhatsApp messages"""
    
    incoming_msg = request.form.get('Body', '').strip()
    from_number = request.form.get('From', '')
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n{'='*60}")
    print(f"📩 [{timestamp}] NEW MESSAGE")
    print(f"From: {from_number}")
    print(f"Message: {incoming_msg}")
    print(f"{'='*60}")
    
    resp = MessagingResponse()
    msg = resp.message()
    
    # Commands
    if incoming_msg.lower() in ['/start', 'start']:
        msg.body(
            "👋 *Welcome to AI ChatBot!*\n\n"
            f"Powered by: {AI_PROVIDER}\n\n"
            "Try asking me:\n"
            "• General questions\n"
            "• To tell you a joke or fact\n"
            "• Simple math problems\n"
            "• Time and date\n\n"
            "Type /help for commands!"
        )
        log_message(from_number, incoming_msg, "Welcome message sent", "system")
        return str(resp)
    
    if incoming_msg.lower() in ['/reset', 'reset']:
        if from_number in conversations:
            msg_count = len(conversations[from_number])
            conversations[from_number] = []
            msg.body(f"✅ Cleared {msg_count} messages!\n\nFresh start! What's on your mind?")
        else:
            msg.body("✅ Already fresh! What can I help you with?")
        log_message(from_number, incoming_msg, "Reset conversation", "system")
        return str(resp)
    
    if incoming_msg.lower() in ['/help', 'help']:
        msg.body(
            "🤖 *Available Commands:*\n\n"
            "/start - Introduction\n"
            "/reset - Clear chat history\n"
            "/stats - View statistics\n"
            "/help - This message\n\n"
            "💡 *Try asking:*\n"
            "• 'Tell me a joke'\n"
            "• 'What time is it?'\n"
            "• 'Calculate 25 * 4'\n"
            "• 'Is USA in Africa?'\n"
            "• 'Tell me a fact'"
        )
        log_message(from_number, incoming_msg, "Help sent", "system")
        return str(resp)
    
    if incoming_msg.lower() in ['/stats', 'stats']:
        uptime = datetime.now() - stats["start_time"]
        uptime_mins = int(uptime.total_seconds() / 60)
        user_msg_count = len(conversations.get(from_number, []))
        
        api_status = "✅ Active"
        if RATE_LIMIT["api_disabled_until"]:
            remaining = int((RATE_LIMIT["api_disabled_until"] - datetime.now()).total_seconds())
            if remaining > 0:
                api_status = f"🚫 Disabled ({remaining}s)"
        elif RATE_LIMIT["cooldown_until"]:
            remaining = int((RATE_LIMIT["cooldown_until"] - datetime.now()).total_seconds())
            if remaining > 0:
                api_status = f"⏸️ Cooldown ({remaining}s)"
        
        msg.body(
            f"📊 *Bot Statistics*\n\n"
            f"⏱ Uptime: {uptime_mins} minutes\n"
            f"💬 Total Messages: {stats['total_messages']}\n"
            f"👥 Active Users: {stats['total_users']}\n"
            f"🤖 AI Responses: {stats['total_ai_calls']}\n"
            f"🧠 Smart Responses: {stats['total_fallback_calls']}\n"
            f"💾 Cached Responses: {stats['total_cached_calls']}\n"
            f"⏸️ Rate Limited: {stats['total_rate_limited']}\n"
            f"📱 Your Messages: {user_msg_count}\n"
            f"⚡ Mode: {AI_PROVIDER}\n"
            f"🔌 API Status: {api_status}"
        )
        log_message(from_number, incoming_msg, "Stats sent", "system")
        return str(resp)
    
    # AI Response
    print("🤖 Generating response...")
    ai_response, sentiment = get_ai_response(incoming_msg, from_number)
    
    # Send response to WhatsApp
    msg.body(ai_response)
    
    print(f"💬 Response: {ai_response}")
    if sentiment:
        print(f"😊 Sentiment: {sentiment}")
    print(f"✅ Message sent to WhatsApp: {from_number}")
    print(f"📝 Response length: {len(ai_response)} characters")
    print(f"{'='*60}\n")
    
    return str(resp)


@app.route("/")
def dashboard():
    """Web dashboard"""
    uptime = datetime.now() - stats["start_time"]
    uptime_str = str(uptime).split('.')[0]
    recent_msgs = message_log[-10:][::-1]
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WhatsApp Bot Dashboard</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333;
                min-height: 100vh;
                padding: 20px;
            }
            .container { max-width: 1200px; margin: 0 auto; }
            .header {
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                margin-bottom: 30px;
                text-align: center;
            }
            h1 { color: #667eea; font-size: 2.5em; margin-bottom: 10px; }
            .status {
                display: inline-block;
                background: #10b981;
                color: white;
                padding: 8px 20px;
                border-radius: 20px;
                font-weight: bold;
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.7; }
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .stat-card {
                background: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.1);
                text-align: center;
            }
            .stat-icon { font-size: 3em; margin-bottom: 10px; }
            .stat-value { font-size: 2.5em; font-weight: bold; color: #667eea; }
            .stat-label { color: #666; margin-top: 5px; font-size: 0.9em; }
            .messages {
                background: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            }
            .messages h2 { color: #667eea; margin-bottom: 20px; font-size: 1.5em; }
            .message {
                background: #f7fafc;
                padding: 15px;
                margin-bottom: 15px;
                border-radius: 10px;
                border-left: 4px solid #667eea;
            }
            .message-header {
                display: flex;
                justify-content: space-between;
                margin-bottom: 8px;
                font-size: 0.85em;
                color: #666;
            }
            .message-body { color: #333; line-height: 1.5; }
            .type-ai { border-left-color: #667eea; }
            .type-smart { border-left-color: #10b981; }
            .type-system { border-left-color: #f59e0b; }
            .footer {
                text-align: center;
                margin-top: 30px;
                color: white;
                font-size: 0.9em;
            }
        </style>
        <script>
            setTimeout(function(){ location.reload(); }, 5000);
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 WhatsApp AI Chatbot</h1>
                <p style="margin: 10px 0; color: #666;">University Project Demo - """ + AI_PROVIDER + """</p>
                <div class="status">● LIVE & RUNNING</div>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-icon">⏱</div>
                    <div class="stat-value">{{ uptime }}</div>
                    <div class="stat-label">Uptime</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">💬</div>
                    <div class="stat-value">{{ total_messages }}</div>
                    <div class="stat-label">Total Messages</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">👥</div>
                    <div class="stat-value">{{ total_users }}</div>
                    <div class="stat-label">Active Users</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">🤖</div>
                    <div class="stat-value">{{ ai_calls }}</div>
                    <div class="stat-label">AI Calls</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">🧠</div>
                    <div class="stat-value">{{ fallback_calls }}</div>
                    <div class="stat-label">Smart Responses</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">💾</div>
                    <div class="stat-value">{{ cached_calls }}</div>
                    <div class="stat-label">Cached Responses</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">⏸️</div>
                    <div class="stat-value">{{ rate_limited }}</div>
                    <div class="stat-label">Rate Limited</div>
                </div>
            </div>
            
            <div class="messages">
                <h2>📨 Recent Messages</h2>
                {% for msg in messages %}
                <div class="message type-{{ msg.type }}">
                    <div class="message-header">
                        <span><strong>User ***{{ msg.phone }}</strong></span>
                        <span>{{ msg.timestamp }}</span>
                    </div>
                    <div class="message-body">
                        <strong>→</strong> {{ msg.message }}<br>
                        <strong>←</strong> {{ msg.response }}
                    </div>
                </div>
                {% endfor %}
            </div>
            
            <div class="footer">
                <p>Auto-refreshing every 5 seconds | Flask + """ + AI_PROVIDER + """ + Twilio</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(
        html,
        uptime=uptime_str,
        total_messages=stats["total_messages"],
        total_users=stats["total_users"],
        ai_calls=stats["total_ai_calls"],
        fallback_calls=stats["total_fallback_calls"],
        cached_calls=stats["total_cached_calls"],
        rate_limited=stats["total_rate_limited"],
        messages=recent_msgs
    )


@app.route("/health")
def health():
    return {
        "status": "healthy",
        "ai_mode": AI_PROVIDER,
        "uptime_seconds": int((datetime.now() - stats["start_time"]).total_seconds()),
        "stats": stats
    }


@app.route("/test-response", methods=["GET"])
def test_response():
    """Test endpoint to verify response generation"""
    test_message = request.args.get('message', 'tell me a joke')
    test_phone = "test_user"
    
    response, sentiment = get_ai_response(test_message, test_phone)
    
    return {
        "status": "success",
        "test_message": test_message,
        "bot_response": response,
        "sentiment": sentiment,
        "response_length": len(response),
        "ai_provider": AI_PROVIDER,
        "api_status": {
            "disabled": RATE_LIMIT["api_disabled_until"] is not None,
            "cooldown": RATE_LIMIT["cooldown_until"] is not None
        }
    }


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  🚀 WHATSAPP AI CHATBOT - SMART FALLBACK VERSION")
    print("="*70)
    print(f"\n🤖 AI Mode: {AI_PROVIDER}")
    print("\n📱 Features Enabled:")
    print("  ✅ Intelligent response system")
    print("  ✅ Pattern matching & knowledge base")
    print("  ✅ Math calculator")
    print("  ✅ Time/Date responses")
    print("  ✅ Conversation memory")
    print("  ✅ Sentiment analysis")
    print("  ✅ Command system")
    print("  ✅ Real-time dashboard")
    print("  ✅ Rate limiting & quota management")
    print("  ✅ Response caching")
    print("  ✅ Exponential backoff on errors")
    print("\n🌐 Access Points:")
    print("  Dashboard: http://localhost:5000")
    print("  Webhook:   http://localhost:5000/whatsapp")
    print("\n💡 This bot works EVEN WITHOUT AI APIs!")
    print("   It will try AI first, then use smart fallbacks.")
    print("\n" + "="*70 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)