from .base_agent import BaseAgent

class ReadabilityAgent(BaseAgent):
    # Rewriting for clarity and simplicity is a nuanced task.
    model_name: str = "gemini-1.5-pro-latest"

    """
    PROFESSIONAL readability optimizer using Gemini AI. It refines a draft to make it
    clearer, simpler, and easier to read. This corresponds to agent A10.
    """

    def run(self, state: dict) -> dict:
        """
        Takes the draft text and rewrites it for improved readability.

        Args:
            state: Shared state dictionary, must contain a 'draft' dictionary with a 'full_text' key.

        Returns:
            The updated state with the more readable text.
        """
        if not self.llm:
            return {'error': 'Gemini API key not configured'}

        draft = state.get('draft', {})
        # This text will be the output from the HumanizationAgent
        current_text = draft.get('full_text')

        if not current_text:
            return {'error': 'Draft text is required for readability analysis.'}

        system_prompt = """You are an expert editor who specializes in improving the readability of text. Your goal is to make content accessible to a broader audience (aiming for a 7th-8th grade reading level) without losing the core message or sounding patronizing."""
        
        user_prompt = f"""
        Please rewrite the following blog post draft to improve its readability. Apply the following techniques:
        - Simplify complex vocabulary and jargon. Replace difficult words with more common ones.
        - Break up long, convoluted sentences.
        - Use active voice instead of passive voice where possible.
        - Add bullet points or numbered lists to break up dense paragraphs if it makes sense.
        - Ensure the meaning, facts, and keywords of the original text are preserved.

        Here is the draft to rewrite:
        ---
        {current_text}
        ---

        Return ONLY the full, rewritten, more readable text. Do not add any commentary before or after the text.
        """
        
        readable_text = self.execute_prompt(system_prompt, user_prompt)
        
        # Update the draft in the state
        state['draft']['full_text'] = readable_text
        
        return state
