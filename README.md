# Smart WhatsApp Chatbot

A fully functional WhatsApp chatbot that runs **100% locally** without any external AI APIs. Built with Python, Flask, and Twilio for a university presentation demo.

## Key Features

- **No AI APIs Required** - Runs entirely on local pattern matching and NLP techniques
- **Extensive Knowledge Base** - 30+ topic categories with hundreds of response patterns
- **Fuzzy Matching** - Handles typos and variations using difflib similarity matching
- **Spelling Correction** - Automatically corrects common misspellings
- **Context Awareness** - Remembers conversation history for follow-up responses
- **Math Calculator** - Evaluates mathematical expressions (basic and complex)
- **Sentiment Analysis** - Detects positive, negative, and neutral messages
- **Response Caching** - Improves performance with intelligent caching
- **Real-time Dashboard** - Beautiful web interface showing live statistics
- **WhatsApp Integration** - Works with Twilio's WhatsApp API

## How It Works

The chatbot uses a multi-layered approach to generate intelligent responses:

1. **Pattern Matching** - Searches the knowledge base for exact pattern matches
2. **Fuzzy Matching** - Falls back to similarity matching for close matches (65%+ threshold)
3. **Spelling Correction** - Corrects common typos before processing
4. **Context Extraction** - Analyzes conversation history for better responses
5. **Math Evaluation** - Detects and calculates mathematical expressions
6. **Dynamic Responses** - Generates real-time data (time, date)

## Project Structure

```
chat-bot/
├── chat.py          # Main application file
├── README.md        # This documentation
└── requirements.txt # Python dependencies (optional)
```

## Requirements

- Python 3.8+
- Flask
- Twilio (for WhatsApp integration)

## Installation

1. **Clone or download the project**

2. **Create a virtual environment** (recommended):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**:
   ```powershell
   pip install flask twilio
   ```

## Running the Bot

Start the application:

```powershell
python chat.py
```

You'll see:
```
======================================================================
  🧠 SMART WHATSAPP CHATBOT - 100% LOCAL INTELLIGENCE
======================================================================

⚡ Mode: Smart Local Engine

📱 Features Enabled:
  ✅ Pattern matching with extensive knowledge base
  ✅ Fuzzy matching for typos and variations
  ✅ Spelling correction
  ✅ Context-aware responses
  ✅ Math calculator (basic & complex expressions)
  ✅ Dynamic time/date responses
  ✅ Conversation memory
  ✅ Sentiment analysis
  ✅ Response caching for performance
  ✅ Real-time web dashboard

🌐 Access Points:
  Dashboard: http://localhost:5000
  Webhook:   http://localhost:5000/whatsapp
  Health:    http://localhost:5000/health
  Test:      http://localhost:5000/test-response?message=hello

💡 NO EXTERNAL AI APIs REQUIRED!
   This bot runs entirely on local pattern matching and NLP.
======================================================================
```

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web dashboard with live statistics |
| `/whatsapp` | POST | Twilio webhook for WhatsApp messages |
| `/health` | GET | Health check endpoint (JSON) |
| `/test-response` | GET | Test response generation without Twilio |

## WhatsApp Integration with Twilio

1. **Set up Twilio Sandbox**:
   - Go to [Twilio Console](https://console.twilio.com/)
   - Navigate to Messaging > Try it out > Send a WhatsApp message
   - Follow the sandbox setup instructions

2. **Expose your local server**:
   ```powershell
   ngrok http 5000
   ```

3. **Configure Twilio webhook**:
   - Set the "When a message comes in" URL to: `https://<your-ngrok-url>/whatsapp`

## Bot Commands

Users can send these commands:

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and introduction |
| `/help` | Show available commands and examples |
| `/reset` | Clear conversation history |
| `/stats` | View bot statistics |

## What the Bot Can Do

### Conversation
- Greetings and farewells
- How are you responses
- Compliments and thanks

### Knowledge
- World capitals (USA, UK, France, Nigeria, Japan, etc.)
- Geography questions
- Science topics (physics, chemistry, biology)
- Technology explanations (AI, programming, Python)

### Entertainment
- 14+ jokes with emojis
- 14+ fun facts
- Motivational quotes

### Utilities
- Current time and date
- Math calculations (25 * 4, 100 / 5, etc.)
- Basic Q&A

## Testing Without Twilio

Use the test endpoint to verify responses:

```
http://localhost:5000/test-response?message=tell%20me%20a%20joke
```

Response:
```json
{
  "status": "success",
  "test_message": "tell me a joke",
  "bot_response": "Why don't scientists trust atoms? Because they make up everything! 😄",
  "sentiment": "😐 Neutral",
  "response_length": 67,
  "mode": "Smart Local Engine"
}
```

## Customization

### Adding New Knowledge

Edit the `KNOWLEDGE_BASE` dictionary in `chat.py`:

```python
"new_topic": {
    "patterns": ["pattern1", "pattern2", "pattern3"],
    "responses": [
        "Response 1",
        "Response 2",
    ]
}
```

### Adding Spelling Corrections

Add entries to `SPELLING_CORRECTIONS`:

```python
SPELLING_CORRECTIONS = {
    "misspeled": "misspelled",
    "wrng": "wrong",
}
```

### Adjusting Fuzzy Match Threshold

Change the threshold in `get_smart_response()`:

```python
best_match, score = fuzzy_match(message_lower, all_patterns, threshold=0.65)
```

## Dashboard Features

The web dashboard at `http://localhost:5000` shows:

- **Uptime** - How long the bot has been running
- **Total Messages** - Number of messages processed
- **Active Users** - Unique users who have chatted
- **Smart Responses** - Responses generated by the engine
- **Cached Responses** - Responses served from cache
- **Pattern Matches** - Exact pattern matches
- **Fuzzy Matches** - Similarity-based matches
- **Recent Messages** - Last 10 conversations

## Technical Details

### Response Priority

1. Math expressions (if detected)
2. "Another/more" context requests
3. Exact pattern matches
4. Fuzzy matches (65%+ similarity)
5. Context-aware default responses

### Caching

- Responses are cached for 5 minutes (configurable via `CACHE_DURATION`)
- Cache key is MD5 hash of lowercase message
- Improves response time for repeated questions

### Conversation Memory

- Stores last 10 messages per user
- Used for context-aware responses
- Enables "tell me another joke" functionality

## Troubleshooting

### Bot not responding
1. Check if Flask is running (`python chat.py`)
2. Verify the webhook URL in Twilio console
3. Check ngrok is running and URL is correct

### Twilio errors
- **63038**: Daily message limit reached (trial accounts have 50/day limit)
- **21608**: Invalid phone number format
- Wait 24 hours or upgrade your Twilio account

### Test locally first
Always test using `/test-response` endpoint before connecting Twilio:
```
http://localhost:5000/test-response?message=hello
```

## License

This project is for educational purposes (university presentation).

## Author

Built for a university demonstration of chatbot technology using Python and Flask.

---

**Note**: This chatbot runs entirely on local pattern matching and NLP techniques. No external AI APIs (like OpenAI, Google AI, etc.) are required, making it cost-free and privacy-friendly!
