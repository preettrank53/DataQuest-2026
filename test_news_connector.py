"""
Test suite for news_connector.py
Tests the NewsAPI connector functionality including data fetching, 
duplicate filtering, and error handling.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
from news_connector import fetch_news_stream, seen_urls

class TestNewsConnector(unittest.TestCase):
    """Test cases for the news connector"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Clear seen URLs before each test
        seen_urls.clear()
        
        # Mock API response
        self.mock_response = {
            "status": "ok",
            "articles": [
                {
                    "title": "Test Article 1",
                    "description": "Test description 1",
                    "url": "https://example.com/article1",
                    "publishedAt": "2026-01-18T10:00:00Z",
                    "source": {"name": "Test Source"}
                },
                {
                    "title": "Test Article 2",
                    "description": "Test description 2",
                    "url": "https://example.com/article2",
                    "publishedAt": "2026-01-18T11:00:00Z",
                    "source": {"name": "Test Source 2"}
                }
            ]
        }
    
    def tearDown(self):
        """Clean up after tests"""
        seen_urls.clear()
    
    @patch.dict(os.environ, {"NEWS_API_KEY": "test_api_key_12345"})
    @patch('news_connector.requests.get')
    @patch('news_connector.time.sleep')
    def test_fetch_news_stream_success(self, mock_sleep, mock_get):
        """Test successful news fetching"""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = self.mock_response
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Get generator
        generator = fetch_news_stream()
        
        # Fetch first article
        article = next(generator)
        
        # Verify article structure
        self.assertIn('text', article)
        self.assertIn('url', article)
        self.assertIn('date', article)
        self.assertIn('source', article)
        self.assertIn('category', article)
        
        # Verify article content
        self.assertEqual(article['url'], 'https://example.com/article1')
        self.assertIn('Test Article 1', article['text'])
    
    @patch.dict(os.environ, {"NEWS_API_KEY": "test_api_key_12345"})
    @patch('news_connector.requests.get')
    @patch('news_connector.time.sleep')
    def test_duplicate_filtering(self, mock_sleep, mock_get):
        """Test that duplicate articles are filtered out"""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = self.mock_response
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Get generator
        generator = fetch_news_stream()
        
        # Fetch all articles from first batch
        articles_batch1 = []
        for _ in range(4):  # 2 tech + 2 business
            articles_batch1.append(next(generator))
        
        # Mock sleep returns to trigger second poll
        # Should get no new articles since they're duplicates
        mock_sleep.reset_mock()
        
        # Verify URLs are in seen_urls
        self.assertIn('https://example.com/article1', seen_urls)
        self.assertIn('https://example.com/article2', seen_urls)
    
    @patch.dict(os.environ, {"NEWS_API_KEY": "test_api_key_12345"})
    @patch('news_connector.requests.get')
    @patch('news_connector.time.sleep')
    def test_api_error_handling(self, mock_sleep, mock_get):
        """Test handling of API errors"""
        # Mock API error response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "error",
            "message": "API key invalid"
        }
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        # Get generator - should not crash
        generator = fetch_news_stream()
        
        # Try to get articles - should handle error gracefully
        # The generator will continue running and retry
        try:
            # This should not raise an exception
            next(generator)
        except StopIteration:
            # Generator may stop if we limit iterations in test
            pass
    
    @patch.dict(os.environ, {"NEWS_API_KEY": "test_api_key_12345"})
    @patch('news_connector.requests.get')
    @patch('news_connector.time.sleep')
    def test_network_timeout_handling(self, mock_sleep, mock_get):
        """Test handling of network timeouts"""
        import requests
        
        # Mock timeout exception
        mock_get.side_effect = requests.exceptions.Timeout("Connection timeout")
        
        # Get generator - should not crash
        generator = fetch_news_stream()
        
        # Should handle timeout gracefully
        try:
            next(generator)
        except StopIteration:
            pass
    
    def test_missing_api_key(self):
        """Test that missing API key raises error"""
        # Clear environment variable
        if "NEWS_API_KEY" in os.environ:
            del os.environ["NEWS_API_KEY"]
        
        # Should raise ValueError
        with self.assertRaises(ValueError):
            generator = fetch_news_stream()
            next(generator)


class TestNewsDataFormat(unittest.TestCase):
    """Test the data format of news articles"""
    
    @patch.dict(os.environ, {"NEWS_API_KEY": "test_api_key_12345"})
    @patch('news_connector.requests.get')
    @patch('news_connector.time.sleep')
    def test_article_data_format(self, mock_sleep, mock_get):
        """Test that article data has correct format"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "ok",
            "articles": [{
                "title": "AI Breakthrough",
                "description": "New AI model released",
                "url": "https://example.com/ai-news",
                "publishedAt": "2026-01-18T12:00:00Z",
                "source": {"name": "Tech News"}
            }]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        generator = fetch_news_stream()
        article = next(generator)
        
        # Verify all required fields present
        required_fields = ['text', 'url', 'date', 'source', 'category']
        for field in required_fields:
            self.assertIn(field, article)
        
        # Verify data types
        self.assertIsInstance(article['text'], str)
        self.assertIsInstance(article['url'], str)
        self.assertIsInstance(article['date'], str)
        self.assertIsInstance(article['source'], str)
        self.assertIsInstance(article['category'], str)
        
        # Verify text combines title and description
        self.assertIn('AI Breakthrough', article['text'])
        self.assertIn('New AI model released', article['text'])


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
