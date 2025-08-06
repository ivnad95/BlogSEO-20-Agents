from .base_agent import BaseAgent
from utilities.api_clients import DuckDuckGoSearchClient, WebScraperClient
import json

class CompetitorScanAgent(BaseAgent):
    # This agent analyzes scraped text, a flash model provides a good balance of cost and capability.
    model_name: str = "gemini-1.5-flash-latest"

    """
    PROFESSIONAL competitor analysis agent that uses real-time search and scraping
    to analyze competitor content, powered by Gemini AI.
    """

    def run(self, state: dict) -> dict:
        """
        Scans competitors by searching online, scraping their content, and using an LLM to analyze it.

        Args:
            state: Shared state dictionary containing 'topic'.

        Returns:
            A dictionary containing detailed competitor analysis.
        """
        topic = state.get('topic', '')
        if not topic:
            return {"error": "Topic is required for competitor analysis."}

        if not self.llm:
            return {'error': 'Gemini API key not configured'}

        # 1. Initialize utility clients
        try:
            search_client = DuckDuckGoSearchClient()
            scraper_client = WebScraperClient()
        except Exception as e:
            return {"error": f"Failed to initialize utility clients: {e}"}

        # 2. Search for competitors
        search_query = f"top 5 articles and blogs about '{topic}'"
        try:
            search_results = search_client.search(search_query, max_results=5)
        except Exception as e:
            return {"error": f"Failed to perform web search: {e}"}

        if not search_results:
            return {"error": "Could not find any competitors via web search."}

        # 3. Scrape competitor content
        competitor_content = []
        for result in search_results:
            url = result.get('href')
            if url:
                try:
                    content = scraper_client.scrape(url)
                    # Truncate content to keep the prompt manageable
                    if len(content) > 4000:
                        content = content[:4000] + "..."
                    competitor_content.append({
                        "title": result.get('title', 'N/A'),
                        "url": url,
                        "content_summary": content
                    })
                except Exception as e:
                    # Log or handle scraping error for a single URL
                    print(f"Could not scrape {url}: {e}")
        
        if not competitor_content:
            return {"error": "Failed to scrape any competitor content."}

        # 4. Synthesize with LLM
        system_prompt = """You are an expert SEO and content strategist. Your task is to perform a deep competitive analysis based on the provided text scraped from top-ranking articles for a given topic. Focus on identifying actionable insights."""

        user_prompt = f"""
        Topic: '{topic}'

        I have scraped the content from top search results. Here is the data:
        ---
        {json.dumps(competitor_content, indent=2)}
        ---

        Based ONLY on the provided text, perform a comprehensive analysis. Output your findings in a structured JSON format with the following keys:
        
        - "top_competitors": A list of the competitor URLs that were analyzed.
        - "competitor_strengths": For each competitor, identify 1-2 key strengths evident from their content (e.g., "in-depth analysis," "good use of examples," "clear structure").
        - "content_gaps": Identify at least 3 specific sub-topics, questions, or angles that are missing from the provided content and could be covered in a new, more comprehensive article.
        - "opportunities": Suggest 3 actionable ways to create a superior piece of content. This could involve combining topics, adding a unique perspective, or improving the format.
        - "unique_angles": Brainstorm 2-3 unique or contrarian angles to differentiate a new article from these competitors.
        """

        response = self.execute_prompt(system_prompt, user_prompt)
        return self.parse_json_response(response)
