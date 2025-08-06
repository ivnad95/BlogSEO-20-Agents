from .base_agent import BaseAgent
from utilities.api_clients import GeminiImageGenerationClient
import os
import time

class AltTextAgent(BaseAgent):
    """
    Generates images from prompts and creates descriptive, SEO-friendly alt text.
    This corresponds to agent A16.
    """
    # This agent uses a lite model for the straightforward task of writing alt text.
    model_name: str = "gemini-1.5-flash-latest"

    def run(self, state: dict) -> dict:
        """
        Takes image prompts, generates images, and writes alt text for them.

        Args:
            state: Shared state dictionary, must contain 'image_prompts'.

        Returns:
            The updated state with a list of generated image data.
        """
        if not self.llm:
            return {'error': 'Gemini text model not configured'}

        image_prompts = state.get('image_prompts', [])
        if not image_prompts:
            state['generated_images'] = []
            return state # No prompts to process

        try:
            image_client = GeminiImageGenerationClient()
        except Exception as e:
            return {'error': f"Failed to initialize image generation client: {e}"}

        # Create a directory for the images if it doesn't exist
        output_dir = "output/images"
        os.makedirs(output_dir, exist_ok=True)

        generated_images_data = []
        
        alt_text_system_prompt = "You are an expert in accessibility and SEO. Your task is to write a concise, descriptive alt text for an image based on its generation prompt. The alt text should describe the image for visually impaired users and include relevant keywords for search engines."

        for i, prompt in enumerate(image_prompts):
            # Generate a unique filename
            timestamp = int(time.time())
            filename = f"image_{timestamp}_{i+1}.png"
            output_path = os.path.join(output_dir, filename)

            # 1. Generate the image
            success = image_client.generate(prompt, output_path)

            if success:
                # 2. Generate alt text for the image
                alt_text_user_prompt = f"""
                An image was generated with the following prompt:
                ---
                {prompt}
                ---
                Please write the perfect alt text for this image. The alt text should be a single, descriptive sentence.
                """
                alt_text = self.execute_prompt(alt_text_system_prompt, alt_text_user_prompt)

                generated_images_data.append({
                    "prompt": prompt,
                    "image_path": output_path,
                    "alt_text": alt_text.strip()
                })
        
        state['generated_images'] = generated_images_data
        return state
