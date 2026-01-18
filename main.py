import os
import pathway as pw
from pathway.xpacks.llm import embedders, llms, parsers, splitters
from pathway.xpacks.llm.document_store import DocumentStore
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

# Create the RAG application
app = doc_store.search_app(llm=llm)

# Launch the PathwayWebserver
server = PathwayWebserver(
    host="0.0.0.0",
    port=8000,
)

print("🚀 Real-Time RAG Server with Live News Stream!")
print("📡 Data Source: NewsAPI.org (Technology & Business)")
print("🌐 API Endpoint: http://localhost:8000")
print("🤖 AI Model: Gemini 1.5 Flash + text-embedding-004")
print("\n💡 Test the API with:")
print('   curl -X POST http://localhost:8000/v1/pw_ai_answer \\')
print('     -H "Content-Type: application/json" \\')
print('     -d \'{"prompt": "What is the latest technology news?"}\'')
print("\n✨ Live news articles are fetched every 60 seconds!")
print("\n⏳ Starting server and news connector...\n")

# Run the server with the RAG application
server.run(app)


