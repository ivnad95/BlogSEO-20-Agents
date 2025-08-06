from .base_agent import BaseAgent

class ImageOptimizationAgent(BaseAgent):
    """PROFESSIONAL image optimization strategist using Gemini AI."""
    
    def run(self, state: dict) -> dict:
        topic = state.get('topic', '')
        all_outputs = state.get('all_outputs', {})
        
        if not self.llm:
            return {'error': 'Gemini API key not configured'}
        
        system_prompt = """You are an expert in visual content strategy and image SEO."""
        
        user_prompt = f"""Create image strategy for '{topic}'.
        
        Provide strategy in JSON:
        {{
            "hero_image": {{"description": "what it should show", "keywords": ["img keyword"]}},
            "supporting_images": [
                {{"type": "infographic", "content": "what to include", "alt_text": "SEO alt text"}}
            ],
            "image_seo": {{"file_naming": "convention", "compression": "recommendations"}},
            "visual_hierarchy": "how to structure images"
        }}"""
        
        response = self.execute_prompt(system_prompt, user_prompt)
        return self.parse_json_response(response)
