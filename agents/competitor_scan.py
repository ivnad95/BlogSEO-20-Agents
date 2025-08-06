from .base_agent import BaseAgent

class CompetitorScanAgent(BaseAgent):
    """PROFESSIONAL competitor analysis using Gemini AI."""
    
    def run(self, state: dict) -> dict:
        topic = state.get('topic', '')
        
        if not self.llm:
            return {'error': 'Gemini API key not configured'}
        
        system_prompt = """You are an expert competitive analyst specializing in content gap analysis and SEO."""
        
        user_prompt = f"""Analyze competitor landscape for '{topic}'.
        
        Provide comprehensive analysis in JSON:
        {{
            "top_competitors": ["List 5 main competitors"],
            "content_gaps": ["Gap 1", "Gap 2"],
            "competitor_strengths": ["What they do well"],
            "opportunities": ["How to outrank them"],
            "unique_angles": ["Differentiation strategies"]
        }}"""
        
        response = self.execute_prompt(system_prompt, user_prompt)
        return self.parse_json_response(response)
