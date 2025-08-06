from .base_agent import BaseAgent

class AltTextAgent(BaseAgent):
    """PROFESSIONAL alt text generator using Gemini AI."""
    
    def run(self, state: dict) -> dict:
        all_outputs = state.get('all_outputs', {})
        images = all_outputs.get('ImageOptimizationAgent', {})
        
        if not self.llm:
            return {'error': 'Gemini API key not configured'}
        
        system_prompt = """You are an expert at writing SEO-optimized, accessible alt text."""
        
        user_prompt = f"""Generate alt text for these images: {images}
        
        Provide alt texts in JSON:
        {{
            "alt_texts": [
                {{"image": "hero_image", "alt": "descriptive SEO alt text", "title": "image title"}}
            ],
            "seo_guidelines": ["guideline1", "guideline2"]
        }}"""
        
        response = self.execute_prompt(system_prompt, user_prompt)
        return self.parse_json_response(response)
