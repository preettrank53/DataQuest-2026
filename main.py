import os
import pathway as pw
from pathway.xpacks.llm import embedders, llms, parsers, splitters
from pathway.xpacks.llm.document_store import DocumentStore
from pathway.xpacks.llm.question_answering import RAGQuestionAnswerer
from pathway.xpacks.llm.servers import PathwayWebserver
from dotenv import load_dotenv
from news_connector import fetch_news_stream

# Load environment variables from .env file
load_dotenv()

# Get Gemini API key from environment
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key or "your" in gemini_api_key.lower():
    raise ValueError(
        "Please set your GEMINI_API_KEY in the .env file. "
        "Get your API key from https://aistudio.google.com/app/apikey"
    )

# Set up the data source using NewsAPI connector in streaming mode
data_source = pw.io.python.read(
    fetch_news_stream(),
    schema=pw.schema_builder({
        "text": pw.column_definition(dtype=str),
        "url": pw.column_definition(dtype=str),
        "date": pw.column_definition(dtype=str),
        "source": pw.column_definition(dtype=str),
        "category": pw.column_definition(dtype=str),
    }),
    mode="streaming",
)

# Initialize the DocumentStore with Gemini embedder and token-based text splitter
doc_store = DocumentStore(
    docs=data_source,
    parser=parsers.ParseUnstructured(),
    splitter=splitters.TokenCountSplitter(max_tokens=400),
    embedder=embedders.GeminiEmbedder(
        api_key=gemini_api_key,
        model="models/text-embedding-004",  # Latest Gemini embedding model
    ),
    retriever_factory=lambda: pw.stdlib.indexing.BruteForceKnn(
        embedder=embedders.GeminiEmbedder(
            api_key=gemini_api_key,
            model="models/text-embedding-004",
        ),
        dimensions=768,  # Gemini text-embedding-004 default dimension
        metric="cosine",
    ),
)

# Set up the Gemini LLM for question answering
llm = llms.GeminiChat(
    api_key=gemini_api_key,
    model="gemini-1.5-flash",  # Fast and efficient model
    temperature=0.7,
)

# Define custom system prompt for Real-Time News Analyst
system_prompt = """You are a Real-Time News Analyst powered by live news streams from NewsAPI.

Your role and responsibilities:
- Answer questions ONLY using the provided context from recent news articles
- If the context is empty or insufficient, respond: "I have no recent news on this topic."
- Always mention the publication date of news when available
- Cite news sources when referencing information
- Be concise, factual, and objective
- Do not speculate or add information beyond what's provided in the context
- Focus on the most recent and relevant information

Context format:
- Each article contains: title, description, source name, publication date, and category
- Articles are from technology and business news categories
- Information is updated every 60 seconds

Guidelines:
- When answering, reference the source (e.g., "According to TechCrunch...")
- Mention dates to provide temporal context (e.g., "As of January 18, 2026...")
- If multiple sources discuss the same topic, synthesize the information
- Maintain transparency about what you know and don't know
"""

# Create RAG Question Answerer with custom system prompt
question_answerer = RAGQuestionAnswerer(
    llm=llm,
    indexer=doc_store,
    system_prompt=system_prompt,
    search_topk=5,  # Retrieve top 5 most relevant articles
)

# Create the application with the question answerer
app = question_answerer.build_app()

# Launch the PathwayWebserver
server = PathwayWebserver(
    host="0.0.0.0",
    port=8000,
)

print("🚀 Real-Time RAG Server with Live News Stream!")
print("📡 Data Source: NewsAPI.org (Technology & Business)")
print("🌐 API Endpoint: http://localhost:8000")
print("🤖 AI Model: Gemini 1.5 Flash + text-embedding-004")
print("📝 Custom System Prompt: Real-Time News Analyst")
print("\n💡 Test the Chat Endpoint:")
print('   curl -X POST http://localhost:8000/v1/chat \\')
print('     -H "Content-Type: application/json" \\')
print('     -d \'{"prompt": "What is the latest technology news?"}\'')
print("\n📋 Features:")
print("   ✅ Context-only answers")
print("   ✅ Source attribution")
print("   ✅ Publication dates included")
print("   ✅ Transparent responses")
print("\n✨ Live news articles are fetched every 60 seconds!")
print("\n⏳ Starting server and news connector...\n")

# Run the server with the RAG application
server.run(app)



