from .base_agent import BaseAgent

class ReadabilityAgent(BaseAgent):
    """PROFESSIONAL readability optimizer using Gemini AI."""
    
    def run(self, state: dict) -> dict:
        all_outputs = state.get('all_outputs', {})
        draft = all_outputs.get('DraftWriterAgent', {}).get('draft', {})
        
        if not self.llm:
            return {'error': 'Gemini API key not configured'}
        
        system_prompt = """You are an expert editor who optimizes content for readability and engagement."""
        
        user_prompt = f"""Analyze and improve readability of this content.
        Content: {str(draft)[:1000]}
        
        Provide improvements in JSON:
        {{
            "readability_score": "8/10",
            "improvements": ["suggestion1", "suggestion2"],
            "sentence_rewrites": {{"original": "improved"}},
            "paragraph_structure": "recommendations"
        }}"""
        
        response = self.execute_prompt(system_prompt, user_prompt)
        return self.parse_json_response(response)
