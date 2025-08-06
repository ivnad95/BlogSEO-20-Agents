from .base_agent import BaseAgent

class StyleConsistencyAgent(BaseAgent):
    """PROFESSIONAL style consistency checker using Gemini AI."""
    
    def run(self, state: dict) -> dict:
        all_outputs = state.get('all_outputs', {})
        draft = all_outputs.get('DraftWriterAgent', {}).get('draft', {})
        
        if not self.llm:
            return {'error': 'Gemini API key not configured'}
        
        system_prompt = """You are an expert editor ensuring consistent voice and style."""
        
        user_prompt = f"""Analyze style consistency of this content.
        Content: {str(draft)[:1000]}
        
        Provide analysis in JSON:
        {{
            "style_score": "9/10",
            "inconsistencies": ["issue1", "issue2"],
            "tone_variations": ["where tone changes"],
            "recommendations": ["fix1", "fix2"]
        }}"""
        
        response = self.execute_prompt(system_prompt, user_prompt)
        return self.parse_json_response(response)
