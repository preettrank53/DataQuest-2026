"""
Integration tests for the Live News RAG pipeline
Tests end-to-end functionality including server, API, and news ingestion
"""

import unittest
import time
import os
from unittest.mock import patch, MagicMock


class TestRAGIntegration(unittest.TestCase):
    """Integration tests for the RAG pipeline"""
    
    def test_environment_variables(self):
        """Test that required environment variables are set"""
        from dotenv import load_dotenv
        load_dotenv()
        
        gemini_key = os.getenv("GEMINI_API_KEY")
        news_key = os.getenv("NEWS_API_KEY")
        
        # Verify keys are present (but don't check actual values for security)
        self.assertIsNotNone(gemini_key, "GEMINI_API_KEY not found in .env")
        self.assertIsNotNone(news_key, "NEWS_API_KEY not found in .env")
        self.assertNotEqual(gemini_key, "", "GEMINI_API_KEY is empty")
        self.assertNotEqual(news_key, "", "NEWS_API_KEY is empty")
    
    def test_imports(self):
        """Test that all required modules can be imported"""
        try:
            import pathway as pw
            import requests
            from dotenv import load_dotenv
            import google.generativeai
            from pathway.xpacks.llm import embedders, llms, parsers, splitters
            from news_connector import fetch_news_stream
        except ImportError as e:
            self.fail(f"Failed to import required module: {e}")
    
    def test_news_connector_callable(self):
        """Test that news connector is callable and returns a generator"""
        from news_connector import fetch_news_stream
        
        # Check it's callable
        self.assertTrue(callable(fetch_news_stream))
        
        # Check it returns a generator (with mocked API key)
        with patch.dict(os.environ, {"NEWS_API_KEY": "test_key"}):
            result = fetch_news_stream()
            import types
            self.assertIsInstance(result, types.GeneratorType)
    
    @patch('news_connector.requests.get')
    def test_news_connector_yields_data(self, mock_get):
        """Test that news connector yields properly formatted data"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "ok",
            "articles": [{
                "title": "Test",
                "description": "Test article",
                "url": "https://test.com",
                "publishedAt": "2026-01-18T12:00:00Z",
                "source": {"name": "Test"}
            }]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        from news_connector import fetch_news_stream
        
        with patch.dict(os.environ, {"NEWS_API_KEY": "test_key"}):
            generator = fetch_news_stream()
            article = next(generator)
            
            # Verify structure matches expected schema
            expected_keys = {'text', 'url', 'date', 'source', 'category'}
            self.assertEqual(set(article.keys()), expected_keys)
    
    def test_requirements_installed(self):
        """Test that all required packages are installed"""
        required_packages = [
            'pathway',
            'requests',
            'python-dotenv',
            'google-generativeai'
        ]
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                self.fail(f"Required package '{package}' is not installed")


class TestPathwayComponents(unittest.TestCase):
    """Test Pathway framework components"""
    
    def test_pathway_schema_builder(self):
        """Test that schema builder works correctly"""
        import pathway as pw
        
        schema = pw.schema_builder({
            "text": pw.column_definition(dtype=str),
            "url": pw.column_definition(dtype=str),
        })
        
        self.assertIsNotNone(schema)
    
    def test_gemini_embedder_import(self):
        """Test that Gemini embedder can be imported"""
        try:
            from pathway.xpacks.llm import embedders
            self.assertTrue(hasattr(embedders, 'GeminiEmbedder'))
        except ImportError as e:
            self.fail(f"Failed to import GeminiEmbedder: {e}")
    
    def test_gemini_chat_import(self):
        """Test that Gemini chat can be imported"""
        try:
            from pathway.xpacks.llm import llms
            self.assertTrue(hasattr(llms, 'GeminiChat'))
        except ImportError as e:
            self.fail(f"Failed to import GeminiChat: {e}")


class TestProjectStructure(unittest.TestCase):
    """Test project file structure"""
    
    def test_required_files_exist(self):
        """Test that all required project files exist"""
        project_root = os.path.dirname(os.path.abspath(__file__))
        
        required_files = [
            'main.py',
            'news_connector.py',
            '.env',
            'requirements.txt',
            '.gitignore'
        ]
        
        for filename in required_files:
            filepath = os.path.join(project_root, filename)
            self.assertTrue(
                os.path.exists(filepath),
                f"Required file '{filename}' does not exist"
            )
    
    def test_gitignore_contains_env(self):
        """Test that .gitignore properly excludes .env file"""
        project_root = os.path.dirname(os.path.abspath(__file__))
        gitignore_path = os.path.join(project_root, '.gitignore')
        
        with open(gitignore_path, 'r') as f:
            gitignore_content = f.read()
        
        # Check that .env is in gitignore
        self.assertIn('.env', gitignore_content, 
                     ".env file must be in .gitignore to protect API keys")
        
        # Check that venv is in gitignore
        self.assertIn('venv', gitignore_content,
                     "venv directory should be in .gitignore")


if __name__ == '__main__':
    print("=" * 60)
    print("Running Integration Tests for Live News RAG Pipeline")
    print("=" * 60)
    unittest.main(verbosity=2)
