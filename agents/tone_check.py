from .base_agent import BaseAgent

class ToneCheckAgent(BaseAgent):
    """PROFESSIONAL tone analyzer using Gemini AI."""
    
    def run(self, state: dict) -> dict:
        all_outputs = state.get('all_outputs', {})
        draft = all_outputs.get('DraftWriterAgent', {}).get('draft', {})
        target_tone = all_outputs.get('UserInputAgent', {}).get('tone', 'professional')
        
        if not self.llm:
            return {'error': 'Gemini API key not configured'}
        
        system_prompt = """You are an expert at analyzing and adjusting content tone."""
        
        user_prompt = f"""Analyze if content matches target tone: {target_tone}
        Content: {str(draft)[:1000]}
        
        Provide analysis in JSON:
        {{
            "current_tone": "detected tone",
            "tone_match_score": "8/10",
            "adjustments_needed": ["adjustment1"],
            "tone_examples": {{"original": "adjusted"}}
        }}"""
        
        response = self.execute_prompt(system_prompt, user_prompt)
        return self.parse_json_response(response)
