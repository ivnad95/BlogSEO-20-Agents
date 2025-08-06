from .base_agent import BaseAgent

class InternalLinkingAgent(BaseAgent):
    """PROFESSIONAL internal linking strategist using Gemini AI."""
    
    def run(self, state: dict) -> dict:
        topic = state.get('topic', '')
        all_outputs = state.get('all_outputs', {})
        
        if not self.llm:
            return {'error': 'Gemini API key not configured'}
        
        system_prompt = """You are an SEO expert specializing in internal linking strategies."""
        
        user_prompt = f"""Create internal linking strategy for '{topic}'.
        
        Provide strategy in JSON:
        {{
            "pillar_pages": ["main topic pages to link to"],
            "supporting_pages": ["related content to link"],
            "anchor_text_variations": ["text1", "text2"],
            "link_placement": ["where to add links"],
            "link_flow": "how links should flow"
        }}"""
        
        response = self.execute_prompt(system_prompt, user_prompt)
        return self.parse_json_response(response)
