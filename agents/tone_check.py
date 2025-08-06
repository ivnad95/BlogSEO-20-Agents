from .base_agent import BaseAgent

class ToneCheckAgent(BaseAgent):
    # Enforcing a consistent tone across a long document requires a capable model.
    model_name: str = "gemini-1.5-pro-latest"

    """
    PROFESSIONAL tone and style optimizer using Gemini AI. It rewrites a draft
    to ensure it matches the desired tone. This corresponds to agent A11.
    """

    def run(self, state: dict) -> dict:
        """
        Takes the draft text and rewrites it to match the specified tone.

        Args:
            state: Shared state dictionary, must contain 'draft' with 'full_text' and a 'tone'.

        Returns:
            The updated state with the tone-adjusted text.
        """
        if not self.llm:
            return {'error': 'Gemini API key not configured'}

        draft = state.get('draft', {})
        current_text = draft.get('full_text')
        # Get tone from the brief, which should have been set by UserInputAgent
        target_tone = state.get('tone', 'professional')

        if not current_text:
            return {'error': 'Draft text is required for tone adjustment.'}

        system_prompt = f"""You are an expert editor with a mastery of writing styles. Your task is to rewrite a given text to perfectly match a specific target tone, while preserving all the factual information and keywords."""
        
        user_prompt = f"""
        Please rewrite the following blog post draft to have a consistent '{target_tone}' tone.

        - If the tone is 'professional', use formal language, structured arguments, and an authoritative voice.
        - If the tone is 'conversational', use simpler language, contractions, and a friendly, approachable voice.
        - If the tone is 'witty', inject clever humor and wordplay where appropriate without undermining the core message.
        - Adapt your rewriting strategy to the requested tone.

        Here is the draft to rewrite:
        ---
        {current_text}
        ---

        Return ONLY the full, rewritten text in the '{target_tone}' tone. Do not add any commentary.
        """
        
        adjusted_text = self.execute_prompt(system_prompt, user_prompt)
        
        # Update the draft in the state
        state['draft']['full_text'] = adjusted_text
        
        return state
