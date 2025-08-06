from .base_agent import BaseAgent
import json

class ImageOptimizationAgent(BaseAgent):
    """
    PROFESSIONAL Image Prompt Engineer. Analyzes the final text to create detailed,
    effective prompts for an AI image generation model. This corresponds to agent A15.
    """
    # This agent needs to understand content deeply to create good prompts.
    model_name: str = "gemini-1.5-pro-latest"

    def run(self, state: dict) -> dict:
        """
        Analyzes the article text and generates a list of detailed image prompts.

        Args:
            state: Shared state dictionary, must contain 'draft' with 'full_text'.

        Returns:
            The updated state with a list of image prompts.
        """
        if not self.llm:
            return {'error': 'Gemini API key not configured'}

        draft = state.get('draft', {})
        full_text = draft.get('full_text')

        if not full_text:
            return {'error': 'Final draft text is required to generate image prompts.'}
        
        system_prompt = """You are a creative director and expert prompt engineer for AI image generation models. Your task is to read a blog post and create a set of detailed, vivid, and effective prompts to generate images that will enhance the article. The prompts must be specific and follow best practices for text-to-image generation."""
        
        user_prompt = f"""
        Read the following blog post. Identify 3-4 key opportunities for images (e.g., a hero image for the title, an image for a key concept, a diagram). For each opportunity, create a detailed prompt for an AI image generator like DALL-E 3 or Imagen.

        **Prompting Best Practices:**
        - Be specific about the subject, setting, style, and composition.
        - Use descriptive adjectives.
        - Specify the desired art style (e.g., 'photorealistic', 'digital art', 'vector illustration', 'flat icon').
        - Specify lighting and color palette if important.
        - Example: "A photorealistic image of a majestic lion sleeping peacefully under an acacia tree on the Serengeti plains, with the warm, golden light of sunset casting long shadows. The style should be like a National Geographic photograph."

        **Blog Post Text:**
        ---
        {full_text[:8000]}
        ---

        Return your output as a JSON object with a single key, "image_prompts", which is a list of strings. Each string is a complete, detailed prompt.
        Example JSON:
        {{
            "image_prompts": [
                "Prompt for Hero Image...",
                "Prompt for Image 2...",
                "Prompt for Image 3..."
            ]
        }}
        """
        
        response = self.execute_prompt(system_prompt, user_prompt)
        parsed_response = self.parse_json_response(response)

        state['image_prompts'] = parsed_response.get('image_prompts', [])

        return state
