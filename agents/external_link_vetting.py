from .base_agent import BaseAgent

class ExternalLinkVettingAgent(BaseAgent):
    """PROFESSIONAL external link curator using Gemini AI."""
    
    def run(self, state: dict) -> dict:
        topic = state.get('topic', '')
        
        if not self.llm:
            return {'error': 'Gemini API key not configured'}
        
        system_prompt = """You are an expert at finding and vetting authoritative external sources."""
        
        user_prompt = f"""Find authoritative external links for '{topic}'.
        
        Provide recommendations in JSON:
        {{
            "authoritative_sources": [
                {{"url": "example.com", "domain_authority": "high", "relevance": "why relevant"}}
            ],
            "research_papers": ["paper1", "paper2"],
            "industry_resources": ["resource1"],
            "news_sources": ["source1"]
        }}"""
        
        response = self.execute_prompt(system_prompt, user_prompt)
        return self.parse_json_response(response)
