import os
import time
import requests
from datetime import datetime
from typing import Dict, Generator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWS_API_URL = "https://newsapi.org/v2/top-headlines"
POLL_INTERVAL = 60  # seconds
CATEGORIES = ["technology", "business"]

# Track seen articles to avoid duplicates
seen_urls = set()


def fetch_news_stream() -> Generator[Dict[str, str], None, None]:
    """
    Generator function that fetches live news articles from NewsAPI.org.
    
    Yields:
        Dict containing article data with keys: text, url, date, source
    """
    print("🔴 NewsAPI Connector started")
    print(f"📡 Fetching {', '.join(CATEGORIES)} news every {POLL_INTERVAL} seconds")
    
    if not NEWS_API_KEY or "your" in NEWS_API_KEY.lower():
        raise ValueError(
            "NEWS_API_KEY not configured. Please set it in the .env file. "
            "Get your key from https://newsapi.org/register"
        )
    
    while True:
        try:
            # Fetch news for each category
            for category in CATEGORIES:
                print(f"\n🔍 Fetching {category} news...")
                
                params = {
                    "apiKey": NEWS_API_KEY,
                    "category": category,
                    "language": "en",
                    "pageSize": 20,  # Fetch top 20 articles
                    "sortBy": "publishedAt"
                }
                
                try:
                    response = requests.get(NEWS_API_URL, params=params, timeout=10)
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    if data.get("status") != "ok":
                        print(f"⚠️  API returned non-OK status: {data.get('message', 'Unknown error')}")
                        continue
                    
                    articles = data.get("articles", [])
                    new_articles_count = 0
                    
                    for article in articles:
                        url = article.get("url", "")
                        
                        # Skip if we've already seen this article
                        if url in seen_urls or not url:
                            continue
                        
                        # Mark as seen
                        seen_urls.add(url)
                        new_articles_count += 1
                        
                        # Extract article data
                        title = article.get("title", "")
                        description = article.get("description", "")
                        published_at = article.get("publishedAt", "")
                        source_name = article.get("source", {}).get("name", "Unknown")
                        
                        # Combine title and description for better context
                        text = f"{title}. {description}" if description else title
                        
                        # Format the data
                        article_data = {
                            "text": text,
                            "url": url,
                            "date": published_at,
                            "source": source_name,
                            "category": category
                        }
                        
                        print(f"✅ New {category} article: {title[:60]}...")
                        
                        # Yield the article
                        yield article_data
                    
                    if new_articles_count == 0:
                        print(f"ℹ️  No new {category} articles (all previously seen)")
                    else:
                        print(f"📰 Found {new_articles_count} new {category} articles")
                
                except requests.exceptions.Timeout:
                    print(f"⏱️  Timeout fetching {category} news - will retry in {POLL_INTERVAL}s")
                    continue
                
                except requests.exceptions.RequestException as e:
                    print(f"🔌 Network error fetching {category} news: {str(e)[:100]}")
                    print(f"   Will retry in {POLL_INTERVAL}s")
                    continue
                
                except ValueError as e:
                    print(f"⚠️  JSON parsing error for {category}: {str(e)[:100]}")
                    continue
            
            # Wait before next poll
            print(f"\n💤 Waiting {POLL_INTERVAL} seconds before next poll...")
            time.sleep(POLL_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n🛑 News connector stopped by user")
            break
        
        except Exception as e:
            print(f"❌ Unexpected error in news connector: {str(e)[:200]}")
            print(f"   Continuing after {POLL_INTERVAL}s pause...")
            time.sleep(POLL_INTERVAL)


# Standalone test
if __name__ == "__main__":
    print("=" * 60)
    print("NewsAPI Connector - Standalone Test")
    print("=" * 60)
    
    article_count = 0
    max_articles = 10  # For testing, only fetch first 10 articles
    
    try:
        for article in fetch_news_stream():
            article_count += 1
            print(f"\n--- Article {article_count} ---")
            print(f"Source: {article['source']}")
            print(f"Category: {article['category']}")
            print(f"Date: {article['date']}")
            print(f"URL: {article['url']}")
            print(f"Text: {article['text'][:150]}...")
            
            if article_count >= max_articles:
                print(f"\n✅ Test complete! Fetched {article_count} articles.")
                break
    
    except KeyboardInterrupt:
        print("\n\n✅ Test stopped by user")
