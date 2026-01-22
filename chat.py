"""
Smart WhatsApp Chatbot for University Presentation
100% Local Intelligence - No AI APIs Required!
Fully functional chatbot using pattern matching, NLP techniques, and knowledge bases
"""

from flask import Flask, request, render_template_string
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime, timedelta
import random
import re
import hashlib
import difflib
import string

app = Flask(__name__)

# System Configuration
AI_PROVIDER = "Smart Local Engine"
print("🧠 Running Smart Local Engine - No external AI APIs needed!")

# Data storage
conversations = {}
message_log = []
stats = {
    "total_messages": 0,
    "total_users": 0,
    "total_smart_calls": 0,
    "total_cached_calls": 0,
    "total_pattern_matches": 0,
    "total_fuzzy_matches": 0,
    "start_time": datetime.now()
}

# Response Cache for performance
RESPONSE_CACHE = {}
CACHE_DURATION = 300  # 5 minutes cache

FEATURES = {
    "sentiment": True,
    "context_awareness": True,
    "fuzzy_matching": True,
    "response_caching": True,
    "spelling_correction": True,
    "entity_extraction": True,
}


# ==================================================================
# EXPANDED KNOWLEDGE BASE - Comprehensive Local Intelligence
# ==================================================================

KNOWLEDGE_BASE = {
    # Greetings
    "greeting": {
        "patterns": ["hello", "hi", "hey", "good morning", "good afternoon", "good evening",
                     "howdy", "sup", "yo", "hola", "greetings", "what's up", "whats up"],
        "responses": [
            "👋 Hello! I'm your smart assistant. How can I help you today?",
            "Hi there! 😊 What can I do for you?",
            "Hey! Great to hear from you! What's on your mind?",
            "Hello! 🌟 Ready to assist you. What do you need?",
            "Hi! 👋 I'm here to help. Ask me anything!",
        ]
    },

    # Questions about Bot
    "who_are_you": {
        "patterns": ["who are you", "what are you", "tell me about yourself", "your name",
                     "introduce yourself", "what can you do", "your capabilities"],
        "responses": [
            "I'm a smart WhatsApp chatbot! 🤖 I use advanced pattern matching and local intelligence to help you. I can answer questions, tell jokes, do math, share facts, and have conversations!",
            "I'm your friendly assistant! Built with Python and powered by smart algorithms - no cloud AI needed! 😊 Ask me about time, weather, math, jokes, facts, or just chat!",
        ]
    },

    # How are you
    "how_are_you": {
        "patterns": ["how are you", "how r u", "how do you do", "are you okay", "you good",
                     "how's it going", "hows it going", "wassup", "what's good"],
        "responses": [
            "I'm doing great, thanks for asking! 😊 Ready to help you with anything!",
            "I'm excellent! Running smoothly and ready to chat! 🚀 How about you?",
            "All systems operational! 💪 What can I help you with today?",
        ]
    },

    # Geography Knowledge
    "geography": {
        "patterns": ["usa in africa", "is usa in africa", "where is usa", "usa location",
                     "america continent", "united states continent"],
        "responses": [
            "No, the USA is not in Africa! 🌍 The United States is in North America, while Africa is a separate continent. They're on different sides of the Atlantic Ocean!",
        ]
    },

    # Capitals Database
    "capitals": {
        "patterns": ["capital of", "capital city", "what is the capital"],
        "responses": [
            "🏛️ I know many world capitals! Here are some:\n• USA - Washington D.C.\n• UK - London\n• France - Paris\n• Germany - Berlin\n• Japan - Tokyo\n• Nigeria - Abuja\n• Egypt - Cairo\n• India - New Delhi\n• China - Beijing\n• Brazil - Brasília\n\nAsk me about a specific country!",
        ]
    },

    # Specific Capitals
    "capital_usa": {
        "patterns": ["capital of usa", "capital of america", "capital of united states", "us capital"],
        "responses": ["🏛️ The capital of the United States is Washington D.C.!"]
    },
    "capital_uk": {
        "patterns": ["capital of uk", "capital of england", "capital of britain", "uk capital"],
        "responses": ["🏛️ The capital of the United Kingdom is London!"]
    },
    "capital_france": {
        "patterns": ["capital of france", "french capital"],
        "responses": ["🏛️ The capital of France is Paris! 🗼"]
    },
    "capital_nigeria": {
        "patterns": ["capital of nigeria", "nigerian capital"],
        "responses": ["🏛️ The capital of Nigeria is Abuja!"]
    },
    "capital_japan": {
        "patterns": ["capital of japan", "japanese capital"],
        "responses": ["🏛️ The capital of Japan is Tokyo! 🗾"]
    },

    # Jokes - Expanded
    "joke": {
        "patterns": ["joke", "make me laugh", "funny", "humor", "tell me a joke", "another joke"],
        "responses": [
            "Why don't scientists trust atoms? Because they make up everything! 😄",
            "What do you call a bear with no teeth? A gummy bear! 🐻",
            "Why did the scarecrow win an award? He was outstanding in his field! 🌾",
            "What do you call a fake noodle? An impasta! 🍝",
            "Why don't eggs tell jokes? They'd crack each other up! 🥚",
            "What did the ocean say to the beach? Nothing, it just waved! 🌊",
            "Why did the bicycle fall over? Because it was two-tired! 🚲",
            "What do you call a fish without eyes? A fsh! 🐟",
            "Why don't skeletons fight each other? They don't have the guts! 💀",
            "What do you call a lazy kangaroo? A pouch potato! 🦘",
            "Why did the math book look so sad? Because it had too many problems! 📚",
            "What do you call a dog that does magic? A Labracadabrador! 🐕",
            "Why did the coffee file a police report? It got mugged! ☕",
            "What do you call a sleeping dinosaur? A dino-snore! 🦕",
        ]
    },

    # Facts - Expanded
    "fact": {
        "patterns": ["fact", "tell me something interesting", "did you know", "random fact",
                     "interesting fact", "fun fact", "cool fact"],
        "responses": [
            "🧠 Did you know? Honey never spoils! Archaeologists have found 3000-year-old honey in Egyptian tombs that's still edible!",
            "🌊 Fun fact: The Atlantic Ocean is saltier than the Pacific Ocean!",
            "🐙 Cool fact: Octopuses have three hearts and blue blood!",
            "☀️ Amazing fact: It takes sunlight 8 minutes and 20 seconds to reach Earth!",
            "🦒 Interesting fact: A giraffe's tongue is about 20 inches long!",
            "🐝 Did you know? Bees can recognize human faces!",
            "🌙 Fun fact: A day on Venus is longer than a year on Venus!",
            "🦈 Cool fact: Sharks have been around longer than trees!",
            "🧊 Amazing: Hot water freezes faster than cold water (Mpemba effect)!",
            "🐘 Elephants are the only animals that can't jump!",
            "🍯 A group of flamingos is called a 'flamboyance'! 🦩",
            "💎 Diamonds can be made from peanut butter!",
            "🌍 Russia has a larger surface area than Pluto!",
            "🐌 Snails can sleep for up to 3 years!",
        ]
    },

    # Science Topics
    "science": {
        "patterns": ["what is science", "explain science", "science definition"],
        "responses": [
            "🔬 Science is the systematic study of the natural world through observation and experimentation! It helps us understand how things work, from tiny atoms to massive galaxies. The main branches are Physics, Chemistry, Biology, and Earth Sciences.",
        ]
    },

    "physics": {
        "patterns": ["what is physics", "explain physics", "physics definition"],
        "responses": [
            "⚛️ Physics is the study of matter, energy, and how they interact! It covers everything from the motion of planets to the behavior of subatomic particles. Famous physicists include Einstein, Newton, and Hawking!",
        ]
    },

    "chemistry": {
        "patterns": ["what is chemistry", "explain chemistry", "chemistry definition"],
        "responses": [
            "🧪 Chemistry is the science of matter and its transformations! It studies atoms, molecules, and how substances react with each other. Everything around you - from your phone to the air you breathe - involves chemistry!",
        ]
    },

    "biology": {
        "patterns": ["what is biology", "explain biology", "biology definition"],
        "responses": [
            "🧬 Biology is the study of life and living organisms! It covers everything from tiny bacteria to giant whales, including how they grow, reproduce, and evolve. Sub-fields include genetics, ecology, and anatomy!",
        ]
    },

    # Technology Topics
    "what_is_ai": {
        "patterns": ["what is ai", "what is artificial intelligence", "explain ai", "ai definition"],
        "responses": [
            "🤖 Artificial Intelligence (AI) is technology that enables computers to simulate human intelligence! This includes learning from data, recognizing patterns, making decisions, and understanding language. AI powers everything from voice assistants to self-driving cars!",
        ]
    },

    "what_is_programming": {
        "patterns": ["what is programming", "what is coding", "explain programming"],
        "responses": [
            "💻 Programming is the art of giving instructions to computers! Developers write code in languages like Python, JavaScript, or Java to create apps, websites, games, and more. It's like writing a recipe that computers can follow!",
        ]
    },

    "what_is_python": {
        "patterns": ["what is python", "python programming", "explain python"],
        "responses": [
            "🐍 Python is a popular programming language known for being easy to read and learn! It's used for web development, data science, AI, automation, and much more. This very chatbot is built with Python!",
        ]
    },

    # Weather (Simulated)
    "weather": {
        "patterns": ["weather", "what's the weather", "how's the weather", "temperature outside"],
        "responses": [
            "🌤️ I don't have access to real-time weather data, but you can check your local weather app or visit weather.com! Pro tip: Ask me about anything else - jokes, facts, math, or just chat!",
        ]
    },

    # Motivational
    "motivation": {
        "patterns": ["motivate me", "inspire me", "i need motivation", "feeling down",
                     "cheer me up", "sad", "depressed", "unhappy"],
        "responses": [
            "💪 You've got this! Remember: Every expert was once a beginner. Keep pushing forward!",
            "🌟 Believe in yourself! The only limit to your potential is the one you set for yourself.",
            "🚀 Every day is a new opportunity to grow. You're stronger than you think!",
            "✨ Tough times don't last, but tough people do! Keep your head up!",
            "🌈 After every storm comes a rainbow. Better days are ahead!",
        ]
    },

    # Compliments
    "compliment": {
        "patterns": ["you're great", "you're awesome", "good job", "well done", "nice",
                     "you're smart", "love you", "you're the best"],
        "responses": [
            "Aww, thank you so much! 😊 You just made my day!",
            "You're too kind! 💖 I'm here to help anytime!",
            "Thanks! You're pretty awesome yourself! 🌟",
        ]
    },

    # Help with topics
    "explain": {
        "patterns": ["explain", "what is", "define", "tell me about", "how does", "meaning of"],
        "responses": [
            "I'd be happy to help! 📚 Could you be more specific? For example, try:\n• 'What is AI?'\n• 'What is Python?'\n• 'What is physics?'\n• 'Capital of France'",
        ]
    },

    # Time/Date - Dynamic
    "time": {
        "patterns": ["time", "what time", "current time", "time now", "what's the time"],
        "responses": ["__TIME__"]  # Placeholder for dynamic response
    },

    "date": {
        "patterns": ["date", "what date", "today", "what day", "today's date", "current date"],
        "responses": ["__DATE__"]  # Placeholder for dynamic response
    },

    # Math help
    "math_help": {
        "patterns": ["help with math", "math help", "mathematics"],
        "responses": [
            "🔢 I can help with math! Try expressions like:\n• '25 + 17'\n• '100 - 45'\n• '12 * 8'\n• '144 / 12'\n• '15 + 3 * 4'\n\nJust type the calculation!",
        ]
    },

    # Thanks
    "thanks": {
        "patterns": ["thank", "thanks", "thx", "appreciate", "ty", "thank you"],
        "responses": [
            "You're welcome! 😊 Happy to help!",
            "No problem! That's what I'm here for! 🙌",
            "Anytime! Feel free to ask more questions! 💪",
            "Glad I could help! 🌟",
        ]
    },

    # Goodbye
    "goodbye": {
        "patterns": ["bye", "goodbye", "see you", "later", "gotta go", "cya", "gtg", "good night"],
        "responses": [
            "Goodbye! 👋 Have a great day!",
            "See you later! Come back anytime! 😊",
            "Take care! 🌟 Feel free to chat again soon!",
            "Bye! It was nice chatting with you! 💬",
        ]
    },

    # Yes/No responses
    "yes": {
        "patterns": ["yes", "yeah", "yep", "sure", "okay", "ok", "yup", "affirmative"],
        "responses": [
            "Great! 👍 What else can I help you with?",
            "Awesome! Let me know if you need anything else! 😊",
        ]
    },

    "no": {
        "patterns": ["no", "nope", "nah", "negative", "not really"],
        "responses": [
            "No problem! Let me know if you change your mind! 😊",
            "Alright! I'm here if you need anything! 👍",
        ]
    },

    # Age question
    "age": {
        "patterns": ["how old are you", "your age", "when were you born", "when were you created"],
        "responses": [
            "I was just created for this demo! 🎂 But I have the wisdom of thousands of patterns in my knowledge base! Age is just a number anyway, right? 😄",
        ]
    },

    # Creator question
    "creator": {
        "patterns": ["who made you", "who created you", "who built you", "your creator", "your developer"],
        "responses": [
            "I was built by a talented developer for a university presentation! 🎓 I'm a demonstration of smart chatbot technology using Python and Flask!",
        ]
    },

    # Help
    "help": {
        "patterns": ["help", "what can you do", "commands", "options", "menu"],
        "responses": [
            "🤖 *Here's what I can do:*\n\n💬 Chat & Conversation\n🔢 Math calculations\n😄 Tell jokes\n📚 Share fun facts\n⏰ Tell time & date\n🌍 Answer questions\n🧠 General knowledge\n\n*Try saying:*\n• 'Tell me a joke'\n• '25 * 4'\n• 'What is AI?'\n• 'Capital of France'",
        ]
    },
}

# Common misspellings dictionary
SPELLING_CORRECTIONS = {
    "helo": "hello",
    "hii": "hi",
    "heloo": "hello",
    "thnks": "thanks",
    "thanx": "thanks",
    "plz": "please",
    "pls": "please",
    "u": "you",
    "ur": "your",
    "r": "are",
    "wat": "what",
    "wats": "what's",
    "dont": "don't",
    "cant": "can't",
    "wont": "won't",
    "im": "i'm",
    "thats": "that's",
    "whats": "what's",
    "hows": "how's",
    "theyre": "they're",
    "youre": "you're",
    "were": "we're",
    "jok": "joke",
    "fakt": "fact",
    "tyme": "time",
    "calculat": "calculate",
}


# ==================================================================
# SMART RESPONSE FUNCTIONS
# ==================================================================

def log_message(phone, message, response, msg_type="user"):
    """Log all messages for analytics"""
    message_log.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "phone": phone[-4:] if len(phone) >= 4 else phone,
        "type": msg_type,
        "message": message,
        "response": response[:100] + "..." if len(response) > 100 else response
    })
    stats["total_messages"] += 1


def get_sentiment(text):
    """Enhanced sentiment analysis"""
    positive_words = ["good", "great", "awesome", "excellent", "happy", "love", "best",
                      "thanks", "amazing", "wonderful", "fantastic", "brilliant", "perfect",
                      "nice", "cool", "super", "beautiful", "excited", "glad", "pleased"]
    negative_words = ["bad", "terrible", "awful", "hate", "worst", "sad", "angry",
                      "disappointed", "horrible", "disgusting", "annoying", "frustrated",
                      "upset", "unhappy", "depressed", "boring", "stupid", "ugly"]

    text_lower = text.lower()
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)

    if pos_count > neg_count:
        return "😊 Positive"
    elif neg_count > pos_count:
        return "😔 Negative"
    return "😐 Neutral"


def correct_spelling(message):
    """Apply spelling corrections"""
    if not FEATURES["spelling_correction"]:
        return message

    words = message.lower().split()
    corrected = []
    for word in words:
        clean_word = word.strip(string.punctuation)
        if clean_word in SPELLING_CORRECTIONS:
            corrected.append(SPELLING_CORRECTIONS[clean_word])
        else:
            corrected.append(word)
    return " ".join(corrected)


def calculate_expression(message):
    """Enhanced math expression calculator"""
    try:
        # Clean the message
        text = message.lower()
        text = text.replace("what is", "").replace("calculate", "").replace("compute", "")
        text = text.replace("what's", "").replace("whats", "")
        text = text.replace("x", "*").replace("×", "*").replace("÷", "/")
        text = text.replace("plus", "+").replace("minus", "-")
        text = text.replace("times", "*").replace("divided by", "/")
        text = text.replace("multiplied by", "*")

        # Try to find and evaluate expression
        # Pattern for basic math: number operator number
        pattern = r'(-?\d+\.?\d*)\s*([\+\-\*/\^])\s*(-?\d+\.?\d*)'
        match = re.search(pattern, text)

        if match:
            num1, operator, num2 = float(match.group(1)), match.group(2), float(match.group(3))

            if operator == '+':
                result = num1 + num2
            elif operator == '-':
                result = num1 - num2
            elif operator == '*':
                result = num1 * num2
            elif operator == '/':
                if num2 == 0:
                    return "🔢 Can't divide by zero! That's undefined in mathematics."
                result = num1 / num2
            elif operator == '^':
                result = num1 ** num2

            # Format result nicely
            if result == int(result):
                result = int(result)
            else:
                result = round(result, 4)

            return f"🔢 {int(num1) if num1 == int(num1) else num1} {operator} {int(num2) if num2 == int(num2) else num2} = {result}"

        # Try to evaluate simple expressions with multiple operators
        expr_pattern = r'^[\d\s\+\-\*/\.\(\)]+$'
        clean_text = re.sub(r'[^\d\s\+\-\*/\.\(\)]', '', text).strip()
        if clean_text and re.match(expr_pattern, clean_text):
            try:
                # Safe evaluation of basic math
                result = eval(clean_text, {"__builtins__": {}}, {})
                if isinstance(result, (int, float)):
                    if result == int(result):
                        result = int(result)
                    else:
                        result = round(result, 4)
                    return f"🔢 {clean_text} = {result}"
            except:
                pass

    except Exception as e:
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


def fuzzy_match(message, patterns, threshold=0.7):
    """Find best fuzzy match for message against patterns"""
    if not FEATURES["fuzzy_matching"]:
        return None, 0

    message_lower = message.lower()
    best_match = None
    best_score = 0

    for pattern in patterns:
        # Calculate similarity ratio
        ratio = difflib.SequenceMatcher(None, message_lower, pattern.lower()).ratio()
        if ratio > best_score and ratio >= threshold:
            best_score = ratio
            best_match = pattern

    return best_match, best_score


def extract_context(message, conversation_history):
    """Extract context from conversation for better responses"""
    context = {
        "is_question": "?" in message or any(q in message.lower() for q in ["what", "who", "where", "when", "why", "how"]),
        "is_greeting": any(g in message.lower() for g in ["hello", "hi", "hey"]),
        "is_farewell": any(f in message.lower() for f in ["bye", "goodbye", "later"]),
        "recent_topic": None
    }

    # Check recent conversation for context
    if conversation_history and len(conversation_history) >= 2:
        last_exchange = conversation_history[-2:]
        for msg in last_exchange:
            if msg.get("role") == "assistant":
                content = msg.get("content", "").lower()
                if "joke" in content:
                    context["recent_topic"] = "jokes"
                elif "fact" in content:
                    context["recent_topic"] = "facts"

    return context


def get_smart_response(message, phone):
    """Intelligent response using pattern matching and fuzzy logic"""

    # Apply spelling correction
    corrected_message = correct_spelling(message)
    message_lower = corrected_message.lower().strip()
    original_lower = message.lower().strip()

    # Check for math expressions first
    math_result = calculate_expression(message)
    if math_result:
        stats["total_pattern_matches"] += 1
        return math_result

    # Get conversation context
    conversation_history = conversations.get(phone, [])
    context = extract_context(message, conversation_history)

    # Handle "another" or "more" requests based on context
    if any(word in message_lower for word in ["another", "more", "again", "one more"]):
        if context["recent_topic"] == "jokes":
            data = KNOWLEDGE_BASE.get("joke", {})
            if data.get("responses"):
                stats["total_pattern_matches"] += 1
                return random.choice(data["responses"])
        elif context["recent_topic"] == "facts":
            data = KNOWLEDGE_BASE.get("fact", {})
            if data.get("responses"):
                stats["total_pattern_matches"] += 1
                return random.choice(data["responses"])

    # Exact pattern matching in knowledge base
    for category, data in KNOWLEDGE_BASE.items():
        for pattern in data["patterns"]:
            if pattern in message_lower or pattern in original_lower:
                response = random.choice(data["responses"])

                # Handle dynamic responses
                if response == "__TIME__":
                    response = f"⏰ The current time is: {datetime.now().strftime('%I:%M %p')}"
                elif response == "__DATE__":
                    response = f"📅 Today is: {datetime.now().strftime('%B %d, %Y (%A)')}"

                stats["total_pattern_matches"] += 1
                return response

    # Fuzzy matching for close matches
    all_patterns = []
    pattern_to_category = {}
    for category, data in KNOWLEDGE_BASE.items():
        for pattern in data["patterns"]:
            all_patterns.append(pattern)
            pattern_to_category[pattern] = category

    best_match, score = fuzzy_match(message_lower, all_patterns, threshold=0.65)
    if best_match and score >= 0.65:
        category = pattern_to_category[best_match]
        data = KNOWLEDGE_BASE[category]
        response = random.choice(data["responses"])

        # Handle dynamic responses
        if response == "__TIME__":
            response = f"⏰ The current time is: {datetime.now().strftime('%I:%M %p')}"
        elif response == "__DATE__":
            response = f"📅 Today is: {datetime.now().strftime('%B %d, %Y (%A)')}"

        stats["total_fuzzy_matches"] += 1
        return response

    # Context-aware default responses
    if context["is_question"]:
        default_responses = [
            f"🤔 Interesting question! While I don't have specific information about that, I can help with jokes, facts, math, time, and general knowledge!",
            f"📚 That's a great question! Try asking me:\n• 'Tell me a joke'\n• 'What is AI?'\n• 'Calculate 25 * 4'\n• 'Capital of France'",
            f"🧠 I'm still learning about that topic! But I'm great at jokes, facts, math, and answering questions about science and technology!",
        ]
    else:
        default_responses = [
            f"👋 I'm here to help! Try asking me for a joke, a fact, or a math calculation!",
            f"🌟 Not sure about that one! But I can tell you jokes, facts, the time, or help with math!",
            f"💬 I'd love to help! Here are things I'm good at:\n• Jokes & facts\n• Math calculations\n• Time & date\n• General knowledge\n\nJust ask!",
        ]

    return random.choice(default_responses)


def get_response(message, phone):
    """Main response function with caching and conversation memory"""

    # Initialize conversation for new users
    if phone not in conversations:
        conversations[phone] = []
        stats["total_users"] += 1

    # Get sentiment
    sentiment = get_sentiment(message) if FEATURES["sentiment"] else ""

    # Check cache first
    cached_response = get_cached_response(message)
    if cached_response:
        conversations[phone].append({"role": "user", "content": message})
        conversations[phone].append({"role": "assistant", "content": cached_response})
        conversations[phone] = conversations[phone][-10:]  # Keep last 10 messages
        log_message(phone, message, cached_response, "cached")
        return cached_response, sentiment

    # Generate smart response
    response = get_smart_response(message, phone)
    stats["total_smart_calls"] += 1

    # Cache the response
    cache_response(message, response)

    # Update conversation history
    conversations[phone].append({"role": "user", "content": message})
    conversations[phone].append({"role": "assistant", "content": response})
    conversations[phone] = conversations[phone][-10:]  # Keep last 10 messages

    log_message(phone, message, response, "smart")
    return response, sentiment


# ==================================================================
# FLASK ROUTES
# ==================================================================

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
            "👋 *Welcome to Smart ChatBot!*\n\n"
            f"Powered by: {AI_PROVIDER}\n\n"
            "I can help you with:\n"
            "• 💬 General conversation\n"
            "• 😄 Jokes and fun facts\n"
            "• 🔢 Math calculations\n"
            "• ⏰ Time and date\n"
            "• 🌍 General knowledge\n\n"
            "Type /help for all commands!"
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

    if incoming_msg.lower() in ['/help', 'help', '/commands']:
        msg.body(
            "🤖 *Smart ChatBot Commands:*\n\n"
            "/start - Introduction\n"
            "/reset - Clear chat history\n"
            "/stats - View statistics\n"
            "/help - This message\n\n"
            "💡 *Try asking:*\n"
            "• 'Tell me a joke'\n"
            "• 'What time is it?'\n"
            "• 'Calculate 25 * 4'\n"
            "• 'Capital of France'\n"
            "• 'What is AI?'\n"
            "• 'Tell me a fact'\n"
            "• 'Motivate me'"
        )
        log_message(from_number, incoming_msg, "Help sent", "system")
        return str(resp)

    if incoming_msg.lower() in ['/stats', 'stats']:
        uptime = datetime.now() - stats["start_time"]
        uptime_mins = int(uptime.total_seconds() / 60)
        user_msg_count = len(conversations.get(from_number, []))

        msg.body(
            f"📊 *Bot Statistics*\n\n"
            f"⏱ Uptime: {uptime_mins} minutes\n"
            f"💬 Total Messages: {stats['total_messages']}\n"
            f"👥 Active Users: {stats['total_users']}\n"
            f"🧠 Smart Responses: {stats['total_smart_calls']}\n"
            f"💾 Cached Responses: {stats['total_cached_calls']}\n"
            f"🎯 Pattern Matches: {stats['total_pattern_matches']}\n"
            f"🔍 Fuzzy Matches: {stats['total_fuzzy_matches']}\n"
            f"📱 Your Messages: {user_msg_count}\n"
            f"⚡ Mode: {AI_PROVIDER}"
        )
        log_message(from_number, incoming_msg, "Stats sent", "system")
        return str(resp)

    # Generate Response
    print("🧠 Generating smart response...")
    response, sentiment = get_response(incoming_msg, from_number)

    # Send response
    msg.body(response)

    print(f"💬 Response: {response}")
    if sentiment:
        print(f"😊 Sentiment: {sentiment}")
    print(f"✅ Message sent!")
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
        <title>Smart ChatBot Dashboard</title>
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
            .badge {
                display: inline-block;
                background: #f0f4ff;
                color: #667eea;
                padding: 5px 15px;
                border-radius: 15px;
                font-size: 0.85em;
                margin-top: 10px;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
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
            .stat-icon { font-size: 2.5em; margin-bottom: 10px; }
            .stat-value { font-size: 2em; font-weight: bold; color: #667eea; }
            .stat-label { color: #666; margin-top: 5px; font-size: 0.85em; }
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
                border-left: 4px solid #10b981;
            }
            .message-header {
                display: flex;
                justify-content: space-between;
                margin-bottom: 8px;
                font-size: 0.85em;
                color: #666;
            }
            .message-body { color: #333; line-height: 1.5; }
            .type-smart { border-left-color: #10b981; }
            .type-cached { border-left-color: #667eea; }
            .type-system { border-left-color: #f59e0b; }
            .footer {
                text-align: center;
                margin-top: 30px;
                color: white;
                font-size: 0.9em;
            }
            .no-api {
                background: #10b981;
                color: white;
                padding: 10px 20px;
                border-radius: 10px;
                margin-top: 15px;
                display: inline-block;
            }
        </style>
        <script>
            setTimeout(function(){ location.reload(); }, 5000);
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧠 Smart WhatsApp ChatBot</h1>
                <p style="margin: 10px 0; color: #666;">University Project Demo</p>
                <div class="status">● LIVE & RUNNING</div>
                <br>
                <div class="no-api">✨ 100% Local Intelligence - No AI APIs Required!</div>
                <br>
                <span class="badge">""" + AI_PROVIDER + """</span>
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
                    <div class="stat-icon">🧠</div>
                    <div class="stat-value">{{ smart_calls }}</div>
                    <div class="stat-label">Smart Responses</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">💾</div>
                    <div class="stat-value">{{ cached_calls }}</div>
                    <div class="stat-label">Cached</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">🎯</div>
                    <div class="stat-value">{{ pattern_matches }}</div>
                    <div class="stat-label">Pattern Matches</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">🔍</div>
                    <div class="stat-value">{{ fuzzy_matches }}</div>
                    <div class="stat-label">Fuzzy Matches</div>
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
                {% if not messages %}
                <p style="color: #666; text-align: center;">No messages yet. Send a message to the bot!</p>
                {% endif %}
            </div>

            <div class="footer">
                <p>Auto-refreshing every 5 seconds | Flask + Smart Local Engine + Twilio</p>
                <p style="margin-top: 10px; opacity: 0.8;">No external AI APIs used - 100% local processing!</p>
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
        smart_calls=stats["total_smart_calls"],
        cached_calls=stats["total_cached_calls"],
        pattern_matches=stats["total_pattern_matches"],
        fuzzy_matches=stats["total_fuzzy_matches"],
        messages=recent_msgs
    )


@app.route("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "mode": AI_PROVIDER,
        "uptime_seconds": int((datetime.now() - stats["start_time"]).total_seconds()),
        "features": FEATURES,
        "stats": stats
    }


@app.route("/test-response", methods=["GET"])
def test_response():
    """Test endpoint to verify response generation"""
    test_message = request.args.get('message', 'tell me a joke')
    test_phone = "test_user"

    response, sentiment = get_response(test_message, test_phone)

    return {
        "status": "success",
        "test_message": test_message,
        "bot_response": response,
        "sentiment": sentiment,
        "response_length": len(response),
        "mode": AI_PROVIDER,
        "stats": {
            "pattern_matches": stats["total_pattern_matches"],
            "fuzzy_matches": stats["total_fuzzy_matches"],
            "cached_calls": stats["total_cached_calls"]
        }
    }


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  🧠 SMART WHATSAPP CHATBOT - 100% LOCAL INTELLIGENCE")
    print("="*70)
    print(f"\n⚡ Mode: {AI_PROVIDER}")
    print("\n📱 Features Enabled:")
    print("  ✅ Pattern matching with extensive knowledge base")
    print("  ✅ Fuzzy matching for typos and variations")
    print("  ✅ Spelling correction")
    print("  ✅ Context-aware responses")
    print("  ✅ Math calculator (basic & complex expressions)")
    print("  ✅ Dynamic time/date responses")
    print("  ✅ Conversation memory")
    print("  ✅ Sentiment analysis")
    print("  ✅ Response caching for performance")
    print("  ✅ Real-time web dashboard")
    print("\n🌐 Access Points:")
    print("  Dashboard: http://localhost:5000")
    print("  Webhook:   http://localhost:5000/whatsapp")
    print("  Health:    http://localhost:5000/health")
    print("  Test:      http://localhost:5000/test-response?message=hello")
    print("\n💡 NO EXTERNAL AI APIs REQUIRED!")
    print("   This bot runs entirely on local pattern matching and NLP.")
    print("\n" + "="*70 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True)
