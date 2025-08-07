from .base_agent import BaseAgent
import json

class InternalLinkingAgent(BaseAgent):
    """
    Analyzes the draft and strategically inserts placeholder internal links.
    Part of agent A17.
    """
    # This is a complex text analysis and rewriting task.
    model_name: str = "gemini-1.5-pro-latest"

    def run(self, state: dict) -> dict:
        """
        Identifies opportunities for internal links and inserts them into the text.

        Args:
            state: Shared state dictionary, must contain 'draft' with 'full_text'.

        Returns:
            The updated state with internal links added to the draft.
        """
        if not self.llm:
            return {'error': 'Gemini API key not configured'}

        draft = state.get('draft', {})
        current_text = draft.get('full_text')
        topic = state.get('topic', '')

        if not current_text:
            return {'error': 'Draft text is required for internal linking.'}

        system_prompt = """You are an SEO expert specializing in creating powerful internal linking structures. Your task is to read a blog post and strategically add internal links to it. The links should be relevant and enhance the reader's journey."""
        
        user_prompt = f"""
        Please revise the following blog post on the topic of "{topic}". Your task is to identify 3-5 key phrases or concepts in the text that would be perfect opportunities to link to other hypothetical articles on the same blog.

        **Instructions:**
        1.  Read the entire text to understand the context.
        2.  Identify phrases where a reader might want to learn more about a related sub-topic.
        3.  Rewrite the text to include a markdown link for each identified opportunity.
        4.  The link URL should be a placeholder that suggests a blog post slug. For example, if you identify the phrase "basic SEO principles", you could change it to "[basic SEO principles](/blog/seo-principles-for-beginners)".
        5.  Do not link to the main topic of the article itself. Link to related, more specific topics.
        6.  Ensure the links are added naturally and do not disrupt the reading flow.

        **Draft to Revise:**
        ---
        {current_text}
        ---

        Return ONLY the full, revised text with the markdown internal links added. Do not add any commentary.
        """
        
        text_with_internal_links = self.execute_prompt(system_prompt, user_prompt)
        
        # Update the draft in the state
        state['draft']['full_text'] = text_with_internal_links
        
        return state
