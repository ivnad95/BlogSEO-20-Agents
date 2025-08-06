from .base_agent import BaseAgent

class OnPageSEOAgent(BaseAgent):
    """PROFESSIONAL on-page SEO optimizer using Gemini AI."""
    
    def run(self, state: dict) -> dict:
        topic = state.get('topic', '')
        all_outputs = state.get('all_outputs', {})
        keywords = all_outputs.get('KeywordMiningAgent', {}).get('primary_keywords', [])
        
        if not self.llm:
            return {'error': 'Gemini API key not configured'}
        
        system_prompt = """You are an expert in on-page SEO optimization."""
        
        user_prompt = f"""Optimize on-page SEO for '{topic}'.
        Primary keywords: {keywords[:10]}
        
        Provide optimization in JSON:
        {{
            "title_tag": "SEO optimized title under 60 chars",
            "meta_description": "Compelling description under 155 chars",
            "h1_tag": "Main heading",
            "h2_tags": ["Subheading 1", "Subheading 2"],
            "url_slug": "seo-friendly-url",
            "canonical_url": "recommendation",
            "open_graph": {{"og:title": "social title", "og:description": "social desc"}}
        }}"""
        
        response = self.execute_prompt(system_prompt, user_prompt)
        return self.parse_json_response(response)
