import os
import re
import json
import logging
from django.conf import settings
from dotenv import load_dotenv

# Try to import Gemini, but don't fail if not available
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  google-generativeai not installed. Run: pip install google-generativeai")

logger = logging.getLogger(__name__)

class FakeNewsDetector:
    def __init__(self):
        # Load environment variables directly as backup
        load_dotenv()
        
        # Try multiple ways to get the API key
        self.gemini_api_key = (
            getattr(settings, 'GEMINI_API_KEY', None) or 
            os.getenv('GEMINI_API_KEY')
        )
        
        self.model = None
        
        print(f"🔑 API Key check - From settings: {getattr(settings, 'GEMINI_API_KEY', None)}")
        print(f"🔑 API Key check - From env: {os.getenv('GEMINI_API_KEY')}")
        print(f"🔑 Final API Key: {self.gemini_api_key}")
        
        if self.gemini_api_key and GEMINI_AVAILABLE:
            try:
                genai.configure(api_key=self.gemini_api_key)
                
                # Discover available models dynamically
                print("🔄 Discovering available models...")
                available_models = []
                try:
                    models = genai.list_models()
                    for model in models:
                        if 'generateContent' in model.supported_generation_methods:
                            available_models.append(model.name)
                            print(f"📋 Found model: {model.name}")
                except Exception as e:
                    print(f"❌ Could not list models: {e}")
                    available_models = []
                
                # Try available models or fallback to common ones
                model_names = available_models if available_models else [
                    'gemini-1.5-flash',
                    'gemini-1.5-flash-001',
                    'gemini-1.0-pro',
                    'gemini-1.0-pro-001',
                    'models/gemini-pro',
                    'models/gemini-1.0-pro'
                ]
                
                successful_model = None
                for model_name in model_names:
                    try:
                        self.model = genai.GenerativeModel(model_name)
                        # Test the model with a simple request
                        test_response = self.model.generate_content("Say hello in JSON: {'message': 'hello'}")
                        successful_model = model_name
                        print(f"✅ Successfully loaded and tested model: {model_name}")
                        break
                    except Exception as e:
                        print(f"❌ Failed to load {model_name}: {e}")
                        continue
                
                if not successful_model:
                    print("❌ All model attempts failed - using mock analysis")
                    self.model = None
                    
            except Exception as e:
                print(f"❌ Gemini configuration failed: {e}")
                self.model = None
        else:
            if not self.gemini_api_key:
                print("❌ No Gemini API key found")
            if not GEMINI_AVAILABLE:
                print("❌ google-generativeai package not installed")
            self.model = None
    
    def extract_keywords(self, text):
        """Extract important keywords for web search"""
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [word for word in words if word not in common_words and len(word) > 3]
        return list(set(keywords))[:5]
    
    def search_web(self, query):
        """Search the web for fact-checking information"""
        try:
            return [
                {
                    'title': f"Fact check: {query}",
                    'snippet': "Web search would provide real fact-checking sources when implemented.",
                    'url': 'https://example.com/fact-check'
                }
            ]
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return []
    
    def analyze_with_gemini(self, news_text, search_results=None):
        """Analyze news content using Gemini API"""
        if not self.model:
            print("🔍 Using mock analysis (no model available)")
            return self.mock_analysis(news_text)
        
        try:
            # Simple, clear prompt
            prompt = f"""
            Analyze if this news is likely fake or real: "{news_text}"
            
            Respond with valid JSON only:
            {{
                "is_fake": true/false,
                "confidence_score": 0.0-1.0,
                "reasons": ["list", "of", "reasons"],
                "fact_check_notes": "brief analysis",
                "recommendations": ["list", "of", "suggestions"]
            }}
            """
            
            print(f"🔍 Sending request to Gemini...")
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            print(f"🔍 Raw response: {response_text}")
            
            # Clean the response
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            # Parse JSON
            analysis_result = json.loads(response_text)
            print("✅ Gemini analysis successful!")
            return analysis_result
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            # If JSON parsing fails, try to extract basic info
            return self.extract_basic_analysis(response_text, news_text)
        except Exception as e:
            print(f"❌ Gemini analysis error: {e}")
            return self.mock_analysis(news_text)
    
    def extract_basic_analysis(self, response_text, news_text):
        """Extract basic analysis from non-JSON response"""
        text_lower = response_text.lower()
        is_fake = any(word in text_lower for word in ['fake', 'false', 'misinformation', 'untrue'])
        
        return {
            "is_fake": is_fake,
            "confidence_score": 0.6,
            "reasons": ["AI analysis completed but response format was unexpected"],
            "fact_check_notes": response_text[:200] + "..." if len(response_text) > 200 else response_text,
            "recommendations": ["Verify with official sources", "Check multiple outlets"]
        }
    
    def mock_analysis(self, news_text):
        """Fallback analysis when Gemini is not available"""
        text_lower = news_text.lower()
        
        fake_indicators = ['breaking', 'shocking', 'urgent', 'secret', 'miracle', 'cure', 'died', 'dead', 'fake']
        is_fake = any(indicator in text_lower for indicator in fake_indicators)
        
        return {
            "is_fake": is_fake,
            "confidence_score": 0.7 if is_fake else 0.6,
            "reasons": ["Using rule-based analysis"],
            "fact_check_notes": "AI analysis not available. Using basic pattern detection.",
            "recommendations": ["Verify with official sources", "Check reliable news outlets"]
        }
    
    def check_news(self, news_text, include_web_search=True):
        """Main method to check news authenticity"""
        keywords = self.extract_keywords(news_text)
        search_results = []
        
        if include_web_search and keywords:
            search_query = " ".join(keywords) + " fact check"
            search_results = self.search_web(search_query)
        
        analysis_result = self.analyze_with_gemini(news_text, search_results)
        
        return {
            'analysis': analysis_result,
            'keywords': keywords,
            'sources_checked': search_results,
            'news_preview': news_text[:200] + '...' if len(news_text) > 200 else news_text
        }