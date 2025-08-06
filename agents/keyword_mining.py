from .base_agent import BaseAgent
import requests
from collections import Counter
import json

class KeywordMiningAgent(BaseAgent):
    """PROFESSIONAL keyword research agent using Gemini AI for advanced SEO."""
    
    def run(self, state: dict) -> dict:
        """Mine and analyze keywords using Gemini AI and free tools.
        
        Args:
            state: Shared state dictionary
            
        Returns:
            Comprehensive keyword analysis
        """
        topic = state.get('topic', '')
        all_outputs = state.get('all_outputs', {})
        trends_data = all_outputs.get('TrendIdeaAgent', {})
        
        # Get related queries from trends
        related_queries = trends_data.get('related_queries', {})
        
        # Extract keywords from various sources
        keywords = []
        
        # 1. Google Suggest API (FREE)
        try:
            suggest_url = f"http://suggestqueries.google.com/complete/search?output=firefox&q={topic}"
            response = requests.get(suggest_url)
            if response.status_code == 200:
                suggestions = response.json()[1]
                keywords.extend(suggestions)
        except:
            pass
        
        # FUTURE WORK - SPRINT 2:
        # ========================
        # 1. PyTrends Keyword Research:
        #    - pytrends.build_payload(keywords) for search volume data
        #    - Get related queries and rising queries
        #    - Analyze keyword seasonality and geographic distribution
        #    - Compare keyword trends over time
        
        # 2. Google Keyword Planner API:
        #    - Fetch keyword ideas with search volumes
        #    - Get CPC and competition data
        #    - Identify long-tail keyword opportunities
        #    - Keyword grouping and clustering
        
        # 3. LLM-Based Keyword Expansion:
        #    - Prompt: "Given the seed keyword '{keyword}', generate 30 related 
        #      long-tail keywords categorized by search intent (informational, 
        #      navigational, transactional, commercial)."
        #    - Use semantic similarity for keyword relevance scoring
        
        # 4. SERP Analysis:
        #    - BeautifulSoup scraping of Google SERP features
        #    - Extract People Also Ask (PAA) questions
        #    - Identify featured snippet opportunities
        #    - Analyze SERP intent signals
        
        # 5. Competitor Keyword Mining:
        #    - Scrape competitor meta tags and content
        #    - Extract frequently used terms and phrases
        #    - Identify keyword gaps and opportunities
        
        # 6. NLP-Based Keyword Extraction:
        #    - Use spaCy/NLTK for entity recognition
        #    - TF-IDF analysis for important terms
        #    - RAKE algorithm for multi-word keyword extraction
        #    - TextRank for keyword importance scoring
        
        # 7. Search Intent Classification:
        #    - ML model to classify keyword intent
        #    - Match keywords to content types
        #    - Prioritize keywords by business value
        
        # 8. Keyword Difficulty Scoring:
        #    - Analyze top 10 SERP results
        #    - Calculate domain authority requirements
        #    - Estimate content depth needed
        
        # 2. Use Gemini AI for advanced keyword research
        if not self.llm:
            return {'error': 'Gemini API key not configured'}
        
        system_prompt = """You are an expert SEO keyword researcher with deep knowledge of search intent, keyword difficulty, and content optimization.
        You understand user search behavior, long-tail keywords, and semantic SEO."""
        
        user_prompt = f"""Perform comprehensive keyword research for the topic: '{topic}'
        
        RELATED QUERIES FOUND: {list(related_queries.keys())[:10]}
        GOOGLE SUGGESTIONS: {keywords[:10]}
        
        Provide detailed keyword analysis in JSON format:
        {{
            "primary_keywords": ["List 10 main keywords with highest value"],
            "long_tail_keywords": ["List 15 specific long-tail variations"],
            "semantic_keywords": ["List 10 LSI/semantic keywords"],
            "question_keywords": ["List 10 question-based keywords"],
            "commercial_keywords": ["List 5 buyer-intent keywords"],
            "informational_keywords": ["List 10 research-intent keywords"],
            "keyword_clusters": {{
                "cluster_name": ["related keywords in cluster"]
            }},
            "difficulty_analysis": {{
                "easy_wins": ["Low competition keywords"],
                "medium_competition": ["Moderate difficulty keywords"],
                "high_competition": ["Difficult but valuable keywords"]
            }},
            "search_intent_mapping": {{
                "keyword": "intent_type (informational/commercial/navigational/transactional)"
            }},
            "content_suggestions": ["5 content ideas based on keywords"],
            "featured_snippet_opportunities": ["Keywords likely to win snippets"],
            "voice_search_keywords": ["Natural language variations"]
        }}
        """
        
        response = self.execute_prompt(system_prompt, user_prompt)
        keyword_analysis = self.parse_json_response(response)
        
        # Combine all results
        result = {
            'google_suggestions': keywords,
            'related_queries': list(related_queries.keys())[:20],
            **keyword_analysis
        }
        
        # Calculate total unique keywords found
        all_keywords = set()
        for key, value in result.items():
            if isinstance(value, list):
                all_keywords.update(value)
        
        result['total_keywords_found'] = len(all_keywords)
        result['keyword_density_recommendations'] = {
            'primary': '2-3%',
            'secondary': '1-2%',
            'semantic': '0.5-1%'
        }
        
        return result
