from .base_agent import BaseAgent

class HumanizationAgent(BaseAgent):
    # Rewriting and refining text benefits from a more capable model.
    model_name: str = "gemini-1.5-pro-latest"

    """
    PROFESSIONAL content humanizer using Gemini AI. It refines a draft to make it
    more engaging, relatable, and less robotic. This corresponds to agent A9.
    """

    def run(self, state: dict) -> dict:
        """
        Takes the draft text and rewrites it to be more human and engaging.

        Args:
            state: Shared state dictionary, must contain a 'draft' dictionary with a 'full_text' key.

        Returns:
            The updated state with the humanized text.
        """
        if not self.llm:
            return {'error': 'Gemini API key not configured'}

        draft = state.get('draft', {})
        original_text = draft.get('full_text')

        if not original_text:
            return {'error': 'Draft text from DraftWriterAgent is required for humanization.'}

        system_prompt = """You are an expert editor specializing in making AI-generated text sound like it was written by a human. Your goal is to increase engagement and relatability without changing the core meaning or information."""
        
        user_prompt = f"""
        Please rewrite the following blog post draft to make it sound more human. Apply the following techniques:
        - Break down long, complex sentences into shorter, more digestible ones.
        - Use a more conversational and slightly informal tone where appropriate.
        - Incorporate rhetorical questions to engage the reader.
        - Use contractions (e.g., "it's" instead of "it is", "you're" instead of "you are").
        - Add smoother transitions between paragraphs.
        - Ensure the core information, facts, and keywords remain intact.

        Here is the draft to rewrite:
        ---
        {original_text}
        ---

        Return ONLY the full, rewritten, humanized text. Do not add any commentary before or after the text.
        """
        
        humanized_text = self.execute_prompt(system_prompt, user_prompt)
        
        # Update the draft in the state
        state['draft']['full_text'] = humanized_text
        # Optional: keep a history of the pre-humanized text
        state['draft']['original_text'] = original_text
        
        return state
