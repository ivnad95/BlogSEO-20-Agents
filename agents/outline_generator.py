from .base_agent import BaseAgent

class OutlineGeneratorAgent(BaseAgent):
    """PROFESSIONAL outline generator using Gemini AI."""
    
    def run(self, state: dict) -> dict:
        topic = state.get('topic', '')
        all_outputs = state.get('all_outputs', {})
        keywords = all_outputs.get('KeywordMiningAgent', {}).get('primary_keywords', [])
        
        if not self.llm:
            return {'error': 'Gemini API key not configured'}
        
        system_prompt = """You are an expert content strategist who creates comprehensive, SEO-optimized blog outlines."""
        
        user_prompt = f"""Create a detailed blog outline for '{topic}'.
        Keywords to include: {keywords[:10]}
        
        Provide JSON format:
        {{
            "sections": [
                {{"heading": "Section Title", "subpoints": ["point1", "point2"], "keywords": ["keyword1"]}}
            ],
            "estimated_word_count": 2000
        }}"""
        
        response = self.execute_prompt(system_prompt, user_prompt)
        return self.parse_json_response(response)
