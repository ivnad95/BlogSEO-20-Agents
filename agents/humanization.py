from .base_agent import BaseAgent

class HumanizationAgent(BaseAgent):
    """PROFESSIONAL content humanizer using Gemini AI."""
    
    def run(self, state: dict) -> dict:
        all_outputs = state.get('all_outputs', {})
        draft = all_outputs.get('DraftWriterAgent', {}).get('draft', {})
        
        if not self.llm:
            return {'error': 'Gemini API key not configured'}
        
        system_prompt = """You are an expert writer who makes content engaging, relatable, and human."""
        
        user_prompt = f"""Humanize this content to make it more engaging.
        Content: {str(draft)[:1000]}
        
        Provide humanization in JSON:
        {{
            "personal_stories": ["story example"],
            "emotional_hooks": ["hook1", "hook2"],
            "conversational_elements": ["element1"],
            "engagement_techniques": ["technique1"]
        }}"""
        
        response = self.execute_prompt(system_prompt, user_prompt)
        return self.parse_json_response(response)
