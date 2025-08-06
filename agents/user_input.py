from .base_agent import BaseAgent

class UserInputAgent(BaseAgent):
    """
    Initializes the content brief with the user's topic and default parameters.
    This is the first agent in the workflow.
    """

    def run(self, state: dict) -> dict:
        """
        Takes the initial state with a 'topic' and creates the initial content brief.

        Args:
            state: The initial state, must contain a 'topic' key.

        Returns:
            A dictionary representing the initial content brief.
        """
        topic = state.get('topic', '')
        if not topic:
            return {"error": "Topic is required to start the process."}

        # This agent sets up the initial parameters for the entire workflow.
        # These can be overridden by the user in a more advanced UI.
        initial_brief = {
            "topic": topic,
            "target_word_count": 2000,
            "tone": "professional",
            "target_audience": f"a general audience interested in {topic}",
            "content_type": "informational blog post",
            "seo_focus": True,
            "include_images": True,
            "call_to_action": "Subscribe for more great content!",
            "brand_voice": "informative and engaging"
        }

        # The state will be built upon this initial brief.
        return initial_brief
