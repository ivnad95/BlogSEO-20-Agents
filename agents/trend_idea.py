from pytrends.request import TrendReq
import requests
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime, timedelta
from .base_agent import BaseAgent
import json

class TrendIdeaAgent(BaseAgent):
    """PROFESSIONAL trend analysis agent using Gemini AI + real data sources."""
    # This agent performs a mix of data gathering and analysis, a flash model is suitable.
    model_name: str = "gemini-1.5-flash-latest"
    
    def run(self, state: dict) -> dict:
        """Analyze trends and generate content ideas using FREE APIs.
        
        Args:
            state: Shared state dictionary containing:
                - topic: The blog topic
                - previous_output: Output from previous agent
                - all_outputs: All agent outputs so far
            
        Returns:
            Dictionary with REAL trend analysis results
        """
        topic = state.get('topic', '')
        results = {}
        
        # 1. Google Trends Analysis (FREE)
        try:
            pytrends = TrendReq(hl='en-US', tz=360)
            keywords = topic.split()[:5]  # Take first 5 words as keywords
            pytrends.build_payload(keywords, timeframe='today 3-m')
            
            # Get interest over time
            interest_data = pytrends.interest_over_time()
            if not interest_data.empty:
                # Convert to regular dict with string keys for JSON serialization
                trends_dict = {}
                for col in interest_data.columns:
                    if col != 'isPartial':
                        trends_dict[str(col)] = interest_data[col].tolist()
                results['search_trends'] = trends_dict
            
            # Get related queries
            related = pytrends.related_queries()
            # Convert DataFrames to simple lists for JSON serialization
            related_clean = {}
            for keyword, data in related.items():
                related_clean[keyword] = {
                    'top': data['top'].to_dict('records') if data['top'] is not None and not data['top'].empty else [],
                    'rising': data['rising'].to_dict('records') if data['rising'] is not None and not data['rising'].empty else []
                }
            results['related_queries'] = related_clean
            
            # Get trending searches
            trending = pytrends.trending_searches(pn='united_states')
            results['trending_now'] = trending.values.tolist()[:10]
        except Exception as e:
            results['trends_error'] = str(e)
        
        # 2. Reddit Trending Topics (FREE - no API key needed)
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            reddit_url = f"https://www.reddit.com/search.json?q={topic}&sort=hot&limit=10"
            response = requests.get(reddit_url, headers=headers)
            if response.status_code == 200:
                reddit_data = response.json()
                posts = reddit_data.get('data', {}).get('children', [])
                results['reddit_discussions'] = [
                    {
                        'title': post['data']['title'],
                        'score': post['data']['score'],
                        'comments': post['data']['num_comments']
                    } for post in posts[:5]
                ]
        except Exception as e:
            results['reddit_error'] = str(e)
        
        # 3. Google News RSS (FREE)
        try:
            news_url = f"https://news.google.com/rss/search?q={topic}&hl=en-US&gl=US&ceid=US:en"
            feed = feedparser.parse(news_url)
            results['recent_news'] = [
                {
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.published
                } for entry in feed.entries[:5]
            ]
        except Exception as e:
            results['news_error'] = str(e)
        
        # FUTURE WORK - SPRINT 2:
        # ========================
        # 1. PyTrends Integration:
        #    - Connect to Google Trends API using pytrends library
        #    - Fetch trending searches for specified regions/categories
        #    - Analyze search volume patterns and seasonal trends
        #    - Example: trends.get_historical_interest(keywords, timeframe='today 3-m')
        
        # 2. Social Media Trend Analysis:
        #    - Twitter/X API integration for trending hashtags
        #    - Reddit API for trending topics in relevant subreddits
        #    - LinkedIn pulse topics analysis
        #    - TikTok trending sounds/challenges correlation
        
        # 3. News Aggregation:
        #    - BeautifulSoup scraping for Google News trends
        #    - NewsAPI integration for breaking news topics
        #    - RSS feed parsing for industry-specific news sources
        
        # 4. LLM-Powered Trend Synthesis:
        #    - Prompt: "Analyze these trending topics {trends} and identify 
        #      content opportunities for {niche}. Consider search intent, 
        #      competition level, and content gaps."
        #    - Use Gemini/GPT-4 for trend correlation and opportunity scoring
        
        # 5. Competitor Content Gap Analysis:
        #    - Ahrefs/SEMrush API for competitor content analysis
        #    - Identify topics competitors haven't covered
        #    - Find underperforming competitor content to improve upon
        
        # 6. Predictive Trend Modeling:
        #    - Time series analysis for trend prediction
        #    - Machine learning model for trend lifecycle stage detection
        #    - Identify emerging vs declining trends
        
        # 4. Wikipedia trending articles (FREE)
        try:
            wiki_url = "https://en.wikipedia.org/api/rest_v1/feed/featured/2024/01/01"
            response = requests.get(wiki_url)
            if response.status_code == 200:
                wiki_data = response.json()
                results['wikipedia_trending'] = wiki_data.get('mostread', {}).get('articles', [])[:5]
        except Exception:
            pass
        
        # 5. Use Gemini AI to analyze and synthesize all trend data
        if not self.llm:
            return {"error": "Gemini API key not configured"}

        system_prompt = (
            "You are an expert trend analyst and content strategist specializing in identifying "
            "viral topics and content opportunities. Your role is to analyze real-time trend data "
            "and provide actionable insights for content creation."
        )

        user_prompt = (
            f"Analyze the following trend data for the topic '{topic}' and provide strategic insights:\n\n"
            f"TRENDING NOW: {results.get('trending_now', [][:5])}\n"
            f"RELATED QUERIES: {json.dumps(results.get('related_queries', {}), indent=2)[:1000]}\n"
            f"RECENT NEWS: {[n['title'] for n in results.get('recent_news', [])]}\n"
            f"REDDIT DISCUSSIONS: {[r['title'] for r in results.get('reddit_discussions', [])]}\n\n"
            "Provide a comprehensive analysis in JSON format with:\n"
            "1. content_opportunities: List of 5 specific content ideas based on trends\n"
            "2. trending_angles: 5 unique angles to approach this topic\n"
            "3. viral_potential: Score 1-10 with explanation\n"
            "4. best_timing: When to publish for maximum impact\n"
            "5. target_keywords: 10 high-value keywords to target\n"
            "6. content_gaps: What competitors are missing\n"
            "7. recommended_format: Best content format (listicle, guide, etc.)"
        )

        gemini_response = self.execute_prompt(system_prompt, user_prompt)
        if "error" in gemini_response.lower():
            return {"error": f"TrendIdeaAgent failed: {gemini_response}"}

        ai_analysis = self.parse_json_response(gemini_response)
        if isinstance(ai_analysis, dict) and ai_analysis.get("error"):
            return {"error": f"TrendIdeaAgent failed: {ai_analysis['error']}"}

        results["ai_trend_analysis"] = ai_analysis
        return results
