from .base_agent import BaseAgent

class TechnicalSEOAgent(BaseAgent):
    """PROFESSIONAL technical SEO advisor using Gemini AI."""
    
    def run(self, state: dict) -> dict:
        all_outputs = state.get('all_outputs', {})
        
        if not self.llm:
            return {'error': 'Gemini API key not configured'}
        
        system_prompt = """You are a technical SEO expert."""
        
        user_prompt = f"""Provide technical SEO recommendations.
        
        Return in JSON:
        {{
            "page_speed": ["optimization1", "optimization2"],
            "mobile_optimization": ["mobile fix1"],
            "crawlability": ["improvement1"],
            "indexability": ["recommendation1"],
            "structured_data": ["schema type to add"]
        }}"""
        
        response = self.execute_prompt(system_prompt, user_prompt)
        return self.parse_json_response(response)
