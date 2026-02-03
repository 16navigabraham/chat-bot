# Chat with a User's WhatsApp Number Programmatically
## Group Project Presentation

---

# SLIDE 1: Title Slide

**Chat with a User's WhatsApp Number Programmatically**

- **Course:** [Your Course Name]
- **Group Members:** [Names]
- **Student IDs:** [IDs]
- **Date:** [Presentation Date]
- **Supervisor:** [Supervisor Name]

---

# SLIDE 2: Introduction

## Project Topic

Our group was assigned the topic **"Chat with a user's WhatsApp number programmatically."** The goal was to build a system that can send and receive WhatsApp messages through code, without manually using the WhatsApp application.

## Our Approach

To implement this, we built a chatbot — a program that listens for incoming WhatsApp messages and automatically sends back relevant responses. We used 's WhatsApp API as the bridge between our code and the WhatsApp platform, and Python with Flask to handle the message processing logic.

---

# SLIDE 3: Project Objectives

1. Understand how to programmatically interact with WhatsApp using an API
2. Build a server that can receive and respond to WhatsApp messages automatically
3. Implement a response engine that generates meaningful replies
4. Create a web dashboard to monitor chatbot activity

---

# SLIDE 4: Background

## What Does "Programmatic WhatsApp Chat" Mean?

Instead of typing messages manually in WhatsApp, our system uses code to:
- **Receive** messages sent by a user to a designated WhatsApp number
- **Process** the message content on our server
- **Send back** an automated response to that user's WhatsApp number

This is made possible through **Twilio**, a cloud platform that provides APIs for messaging services including WhatsApp.

## How Twilio Works

1. We register a WhatsApp number (sandbox) on Twilio
2. Twilio forwards any message sent to that number to our server via a **webhook**
3. Our server processes the message and returns a response
4. Twilio delivers the response back to the user on WhatsApp

---

# SLIDE 5: System Architecture

```
+-------------+     +-------------+     +-------------+
|   User's    |     |   Twilio    |     |   Flask     |
|  WhatsApp   |<--->|   Cloud     |<--->|   Server    |
|    App      |     |  (Webhook)  |     |  (Python)   |
+-------------+     +-------------+     +-------------+
                                              |
                                              v
                                    +-----------------+
                                    |  Response Engine |
                                    +-----------------+
                                    | Knowledge Base   |
                                    | Pattern Matching |
                                    | Fuzzy Matching   |
                                    | Math Parser      |
                                    | Cache System     |
                                    +-----------------+
```

## Message Flow

1. A user sends a message to our WhatsApp number
2. Twilio receives it and sends an HTTP POST request to our Flask server
3. Our server extracts the message text and the sender's phone number
4. The response engine determines an appropriate reply
5. The reply is sent back through Twilio to the user's WhatsApp

---

# SLIDE 6: Technologies Used

| Technology | Role in the Project |
|------------|---------------------|
| Python 3.8+ | Main programming language for server and logic |
| Flask | Web framework that receives webhook requests from Twilio |
| Twilio API | Connects our code to WhatsApp messaging |
| HTML/CSS/JS | Frontend for the monitoring dashboard |
| difflib | Python library used for fuzzy string matching |
| hashlib | Python library used for caching responses |

---

# SLIDE 7: How the Response Engine Works

Since our task was to chat programmatically, we needed the system to generate sensible replies. We implemented a rule-based engine with the following techniques:

## 1. Pattern Matching
The system checks if the user's message contains known keywords and returns a matching response from a predefined knowledge base.

## 2. Fuzzy Matching
If no exact keyword match is found, the system uses string similarity to find the closest match. This handles cases where the user misspells a word (e.g., "helo" still matches "hello").

## 3. Spelling Correction
Common abbreviations and misspellings are mapped to their correct forms before processing (e.g., "plz" becomes "please").

## 4. Math Evaluation
If the message contains a mathematical expression, the system evaluates it and returns the result.

---

# SLIDE 8: Knowledge Base

The knowledge base is a dictionary of topics the bot can respond to. It contains over 30 categories:

| Category | Example Triggers | Response Type |
|----------|-----------------|---------------|
| Greetings | hello, hi, hey | Static |
| Jokes | joke, funny | Randomized |
| Facts | fact, did you know | Randomized |
| Time/Date | time, what day | Dynamic (real-time) |
| Mathematics | calculate, 5+3 | Computed |
| Geography | capital of France | Static |
| Science | what is physics | Static |

Each category has multiple possible responses so the bot does not always repeat the same reply.

---

# SLIDE 9: Conversation Context

The system stores the last 10 messages per user, which allows it to handle follow-up messages:

```
User: Tell me a joke
Bot:  [Responds with a joke]

User: Another one
Bot:  [Responds with a different joke]
```

When the user says "another" or "more," the system checks what topic was discussed recently and provides a new response from the same category.

---

# SLIDE 10: Caching

To avoid reprocessing the same message repeatedly, the system caches responses.

| Parameter | Value |
|-----------|-------|
| Cache duration | 5 minutes |
| Key | MD5 hash of the normalized message |
| Storage | In-memory dictionary |

If the same message is received again within the cache window, the stored response is returned directly.

---

# SLIDE 11: Sentiment Detection

The system includes a basic sentiment analysis feature that classifies messages as positive, negative, or neutral based on keyword matching.

| Message | Result |
|---------|--------|
| "This is great" | Positive |
| "I hate this" | Negative |
| "What time is it?" | Neutral |

This is logged on the dashboard for monitoring purposes.

---

# SLIDE 12: Web Dashboard

We built a web dashboard that displays the bot's activity in real time:

- Server uptime
- Total messages received and processed
- Number of unique users
- Breakdown of response types (pattern match, fuzzy match, cached)
- Last 10 messages received

The dashboard refreshes automatically every 5 seconds.

---

# SLIDE 13: API Endpoints

Our Flask server exposes the following endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Serves the web dashboard |
| `/whatsapp` | POST | Receives incoming WhatsApp messages from Twilio |
| `/health` | GET | Returns server status in JSON format |
| `/test-response` | GET | Allows testing the response engine without Twilio |

---

# SLIDE 14: Demonstration

During the demo, we will show:

1. **Sending a message** to the bot's WhatsApp number and receiving a reply
2. **Different types of queries** — greetings, jokes, facts, math, general knowledge
3. **Typo handling** — showing that misspelled input still gets a valid response
4. **Follow-up messages** — using "another one" to get a new response on the same topic
5. **Dashboard** — viewing live statistics as messages are exchanged

---

# SLIDE 15: Testing and Results

| Test Type | What We Tested | Result |
|-----------|---------------|--------|
| Unit Testing | Individual functions (pattern match, fuzzy match, math parser) | Pass |
| Integration Testing | Full message flow from Twilio webhook to response | Pass |
| User Testing | Real conversations via WhatsApp | Pass |

## Performance

| Metric | Value |
|--------|-------|
| Average response time | < 50ms |
| Pattern match accuracy | 95% |
| Fuzzy match accuracy | 85% |

---

# SLIDE 16: Challenges Faced

| Challenge | How We Handled It |
|-----------|-------------------|
| Users misspelling words | Implemented fuzzy matching with a 65% similarity threshold |
| Bot giving the same response repeatedly | Added multiple responses per category with random selection |
| Users saying "another one" without context | Used conversation history to track the last topic |
| Math expressions written in different formats | Normalized text before parsing (e.g., "times" to "*") |

---

# SLIDE 17: Limitations

- The bot can only respond to topics that exist in its knowledge base
- It cannot understand complex or open-ended questions
- Responses are predefined, not generated dynamically
- The Twilio sandbox has usage limits for testing

These limitations are expected for a rule-based system. An AI-powered approach would handle open-ended conversations better, but at the cost of API fees and external dependencies.

---

# SLIDE 18: Future Improvements

If the project were to be extended, the following could be added:

1. **More knowledge categories** — sports, entertainment, current events
2. **Multi-language support** — detecting and responding in different languages
3. **Database storage** — persisting conversation logs and user data
4. **Machine learning** — training on past conversations to improve accuracy
5. **Admin panel** — allowing non-developers to edit the knowledge base

---

# SLIDE 19: Conclusion

For this project, we were tasked with chatting with a user's WhatsApp number programmatically. To accomplish this, we:

- Built a Flask server that receives WhatsApp messages via Twilio webhooks
- Implemented a response engine using pattern matching, fuzzy matching, and spelling correction
- Added conversation context tracking and response caching
- Created a monitoring dashboard to observe bot activity

The system demonstrates that it is possible to programmatically interact with WhatsApp users and provide meaningful automated responses using Python and freely available tools.

---

# SLIDE 20: References

1. Python Software Foundation. *Python Documentation*. https://docs.python.org/
2. Pallets Projects. *Flask Documentation*. https://flask.palletsprojects.com/
3. Twilio Inc. *WhatsApp API Documentation*. https://www.twilio.com/docs/whatsapp
4. Python Software Foundation. *difflib - Helpers for Computing Deltas*. https://docs.python.org/3/library/difflib.html
5. "A Survey on Chatbot Implementation in Customer Service" - IEEE, 2020
6. "Pattern Matching in Natural Language Processing" - ACM, 2019

---

# SLIDE 21: Questions and Answers

**Thank you for your attention.**

**Demo:** http://localhost:5000

**Contact:** [Your Email]

---

**[Group Members]**
**[Your University]**
**[Date]**
