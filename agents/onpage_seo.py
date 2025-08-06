from .base_agent import BaseAgent
import json
import re

class OnPageSEOAgent(BaseAgent):
    """
    Analyzes the final draft to generate critical on-page SEO elements like
    title tags, meta descriptions, and URL slugs.
    """
    model_name: str = "gemini-1.5-pro-latest"

    def run(self, state: dict) -> dict:
        """
        Generates on-page SEO elements based on the final article content.
        """
        if not self.llm:
            return {'error': 'Gemini API key not configured'}

        draft = state.get('draft', {})
        full_text = draft.get('full_text')
        topic = state.get('topic', '')
        keyword_strategy = state.get('keyword_strategy', {})
        primary_keywords = keyword_strategy.get('primary_keywords', [])

        if not full_text:
            return {'error': 'Draft text is required for on-page SEO optimization.'}
        
        system_prompt = "You are an on-page SEO expert with a talent for writing compelling, clickable titles and descriptions. Your primary goal is to optimize content for search engine visibility and user click-through rate."
        
        user_prompt = f"""
        Analyze the following blog post and generate the optimal on-page SEO elements.

        **Primary Keywords to focus on:** {json.dumps(primary_keywords)}
        **Blog Post Content:**
        ---
        {full_text[:8000]}
        ---

        Based on the content, generate the following elements in a JSON object:
        
        - "title_tag": A perfectly optimized title tag. It must be under 60 characters and include the most important primary keyword naturally.
        - "meta_description": A compelling meta description. It must be under 155 characters, entice users to click, and contain a primary keyword.
        - "url_slug": A short, SEO-friendly URL slug using lowercase letters and hyphens.
        - "h1_suggestion": A powerful H1 heading for the article. This should be very similar or identical to the title tag.
        """
        
        response = self.execute_prompt(system_prompt, user_prompt)
        seo_elements = self.parse_json_response(response)

        # Clean up the slug just in case the LLM adds invalid characters
        if 'url_slug' in seo_elements and isinstance(seo_elements['url_slug'], str):
            seo_elements['url_slug'] = self._slugify(seo_elements['url_slug'])

        state['on_page_seo'] = seo_elements
        return state

    def _slugify(self, text: str) -> str:
        """Converts text to a URL-friendly slug."""
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s-]', '', text)
        text = re.sub(r'[\s-]+', '-', text).strip('-')
        return text if text else "unnamed-article"
