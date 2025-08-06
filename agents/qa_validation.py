from .base_agent import BaseAgent

class QAValidationAgent(BaseAgent):
    """PROFESSIONAL quality assurance validator using Gemini AI."""
    
    def run(self, state: dict) -> dict:
        all_outputs = state.get('all_outputs', {})
        
        if not self.llm:
            return {'error': 'Gemini API key not configured'}
        
        system_prompt = """You are a quality assurance expert for content."""
        
        user_prompt = f"""Perform quality check on the blog post.
        
        Provide QA report in JSON:
        {{
            "quality_score": "9/10",
            "factual_accuracy": "verified",
            "grammar_issues": ["issue1"],
            "seo_compliance": "pass",
            "improvements": ["suggestion1"],
            "ready_to_publish": true
        }}"""
        
        response = self.execute_prompt(system_prompt, user_prompt)
        return self.parse_json_response(response)
