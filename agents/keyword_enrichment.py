from .base_agent import BaseAgent
import json

class KeywordEnrichmentAgent(BaseAgent):
    # This final rewrite requires a high degree of nuance to integrate keywords naturally.
    model_name: str = "gemini-1.5-pro-latest"

    """
    PROFESSIONAL SEO agent that intelligently integrates keywords into the final draft.
    This corresponds to agent A13.
    """

    def run(self, state: dict) -> dict:
        """
        Rewrites the final draft to naturally integrate the keyword strategy.

        Args:
            state: Shared state dictionary, must contain 'draft' and 'keyword_strategy'.

        Returns:
            The updated state with the keyword-enriched text.
        """
        if not self.llm:
            return {'error': 'Gemini API key not configured'}

        draft = state.get('draft', {})
        current_text = draft.get('full_text')
        keyword_strategy = state.get('keyword_strategy', {})

        if not current_text or not keyword_strategy:
            return {'error': 'Draft text and keyword strategy are required for enrichment.'}

        primary_keywords = keyword_strategy.get('primary_keywords', [])
        long_tail_keywords = keyword_strategy.get('long_tail_keywords', [])
        semantic_keywords = keyword_strategy.get('semantic_keywords', [])

        system_prompt = """You are an on-page SEO expert and a talented writer. Your task is to revise a given text to naturally incorporate a list of target keywords. The goal is to improve SEO relevance without making the text sound robotic or stuffed with keywords. The flow and readability of the text are paramount."""
        
        user_prompt = f"""
        Please revise the following blog post draft to naturally integrate the keywords from the provided keyword strategy.

        **Keyword Strategy:**
        - Primary Keywords: {json.dumps(primary_keywords)}
        - Long-Tail Keywords: {json.dumps(long_tail_keywords)}
        - Semantic Keywords: {json.dumps(semantic_keywords)}

        **Instructions:**
        1. Read the entire draft to understand its context and flow.
        2. Subtly weave in the keywords where they fit naturally. You may need to slightly rephrase sentences to accommodate them.
        3. Prioritize the primary keywords.
        4. Do NOT force keywords where they don't belong.
        5. The final text must be perfectly readable and sound natural.

        **Draft to Revise:**
        ---
        {current_text}
        ---

        Return ONLY the full, revised text with the keywords integrated. Do not add any commentary.
        """
        
        enriched_text = self.execute_prompt(system_prompt, user_prompt)
        
        # Update the draft in the state with the final polished text
        state['draft']['full_text'] = enriched_text
        
        return state
