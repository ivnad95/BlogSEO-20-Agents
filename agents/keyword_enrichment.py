from .base_agent import BaseAgent

class KeywordEnrichmentAgent(BaseAgent):
    """PROFESSIONAL keyword enrichment using Gemini AI."""
    
    def run(self, state: dict) -> dict:
        all_outputs = state.get('all_outputs', {})
        draft = all_outputs.get('DraftWriterAgent', {}).get('draft', {})
        keywords = all_outputs.get('KeywordMiningAgent', {}).get('primary_keywords', [])
        
        if not self.llm:
            return {'error': 'Gemini API key not configured'}
        
        system_prompt = """You are an SEO expert who optimizes content for keyword density and relevance."""
        
        user_prompt = f"""Enhance this content with natural keyword integration.
        Keywords to add: {keywords[:15]}
        Current content structure: {str(draft)[:500]}
        
        Provide suggestions in JSON:
        {{
            "keyword_placements": {{"keyword": "where and how to add it"}},
            "density_optimization": "recommendations",
            "semantic_variations": ["variation1", "variation2"]
        }}"""
        
        response = self.execute_prompt(system_prompt, user_prompt)
        return self.parse_json_response(response)
