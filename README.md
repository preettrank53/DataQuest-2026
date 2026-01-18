# 🚀 Live News RAG with Gemini AI

**DataQuest 2026 Hackathon Project**

A real-time Retrieval-Augmented Generation (RAG) system powered by Google Gemini AI that fetches live technology and business news from NewsAPI.org and provides intelligent answers to user queries.

## ✨ Features

- 🤖 **Gemini AI Integration** - Uses Gemini 1.5 Flash for fast, intelligent responses
- 📡 **Live News Stream** - Fetches real-time tech & business news from NewsAPI
- 🔍 **Semantic Search** - Advanced vector embeddings with Gemini text-embedding-004
- ⚡ **Real-time Updates** - Polls NewsAPI every 60 seconds for fresh content
- 🛡️ **Robust Error Handling** - Graceful degradation on network failures
- 🎯 **Duplicate Filtering** - Smart URL-based deduplication
- 🌐 **REST API** - Simple HTTP endpoint for queries

## 🏗️ Architecture

```
NewsAPI.org → Custom Connector → Pathway Streaming → DocumentStore → 
Gemini Embeddings → Vector Index → Gemini LLM → REST API → User
```

## 📋 Prerequisites

- Python 3.10 or higher
- [Gemini API Key](https://aistudio.google.com/app/apikey)
- [NewsAPI Key](https://newsapi.org/register)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/DataQuest-2026.git
cd DataQuest-2026
```

### 2. Create Virtual Environment

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# OR
source venv/bin/activate     # Linux/Mac
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Keys

Create a `.env` file in the project root:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
NEWS_API_KEY=your_news_api_key_here
```

> **⚠️ IMPORTANT**: Never commit your `.env` file to Git. It's already in `.gitignore`.

## 🚀 Usage

### Start the Server

```bash
python main.py
```

Expected output:
```
🚀 Real-Time RAG Server with Live News Stream!
📡 Data Source: NewsAPI.org (Technology & Business)
🌐 API Endpoint: http://localhost:8000
🤖 AI Model: Gemini 1.5 Flash + text-embedding-004

🔴 NewsAPI Connector started
📡 Fetching technology, business news every 60 seconds
```

### Query the API

Open a new terminal and run:

```bash
curl -X POST http://localhost:8000/v1/pw_ai_answer \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is the latest technology news?"}'
```

### Example Queries

```bash
# Latest tech news
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What are the top technology stories today?"}'

# Business news
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Tell me about recent business developments"}'

# Specific topics
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is happening with AI and machine learning?"}'

# Test context handling
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What news is there about SpaceX?"}'
```

### NEW: Phase 3 Features (Generation Layer)

**Custom System Prompt**: Real-Time News Analyst
- ✅ Context-only responses (no hallucination)
- ✅ Source attribution in answers
- ✅ Publication dates mentioned
- ✅ Graceful handling of missing information
- ✅ Transparent about knowledge boundaries

## 🧪 Testing

### Run Integration Tests

```bash
python test_integration.py
```

### Run Unit Tests

```bash
python test_news_connector.py
```

### Test News Connector Standalone

```bash
python news_connector.py
```

This will fetch 10 sample articles and display their details.

## 📁 Project Structure

```
DataQuest-2026/
├── main.py                  # Main RAG application
├── news_connector.py        # Custom NewsAPI connector
├── test_integration.py      # Integration tests
├── test_news_connector.py   # Unit tests
├── requirements.txt         # Python dependencies
├── .env                     # API keys (DO NOT COMMIT)
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## ⚙️ Configuration

### Polling Interval

Edit `news_connector.py`:

```python
POLL_INTERVAL = 60  # Change to 300 for 5 minutes, etc.
```

### News Categories

Edit `news_connector.py`:

```python
CATEGORIES = ["technology", "business"]  # Add "science", "health", etc.
```

### Rate Limit Warning

**NewsAPI Free Tier**: 100 requests/day

Current setup with 60-second polling will exceed this. Consider:
- Set `POLL_INTERVAL = 900` (15 minutes) → 96 requests/day ✅
- Upgrade to Developer tier (1,000 requests/day)

## 🐛 Troubleshooting

### "No module named 'pathway'"

```bash
pip install -r requirements.txt
```

### "API key not configured"

Check your `.env` file has both API keys set correctly.

### Server fails to start

1. Check both API keys are valid
2. Ensure port 8000 is not in use
3. Check internet connection

### No news articles fetched

1. Verify NEWS_API_KEY is correct
2. Check NewsAPI quota at https://newsapi.org/account
3. Review console logs for error messages

## 🚢 Deployment

### Deploy to Cloud

This project can be deployed to:
- Google Cloud Run
- Heroku
- AWS Lambda (with modifications)
- Azure Container Instances

### Environment Variables

Set these in your cloud platform:
- `GEMINI_API_KEY`
- `NEWS_API_KEY`

## 🤝 Contributing

This is a hackathon project for DataQuest 2026. Contributions welcome!

## 📄 License

MIT License - feel free to use and modify

## 🙏 Acknowledgments

- [Pathway Framework](https://pathway.com/) - Real-time data processing
- [Google Gemini](https://ai.google.dev/) - AI embeddings and LLM
- [NewsAPI](https://newsapi.org/) - Live news data
- DataQuest 2026 Hackathon

## 📞 Support

For issues or questions, please open an issue on GitHub.

---

**Built with ❤️ for DataQuest 2026 Hackathon**