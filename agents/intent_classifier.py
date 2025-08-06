from .base_agent import BaseAgent
import json

class IntentClassifierAgent(BaseAgent):
    # This is a straightforward classification task, a flash model is efficient.
    model_name: str = "gemini-1.5-flash-latest"

    """
    Analyzes the topic and trending angles to classify the primary search intent.
    This corresponds to agent A3 in the workflow.
    """

    def run(self, state: dict) -> dict:
        """
        Analyzes the topic and trending angles to classify search intent.

        Args:
            state (dict): The current state of the content brief.
                          Must contain 'topic' and the output from the trend agent.

        Returns:
            dict: The updated state with 'search_intent'.
        """
        topic = state.get('topic')
        # The output from the previous agent (trend_idea) is merged into the state
        ai_trend_analysis = state.get('ai_trend_analysis')

        if not topic or not ai_trend_analysis:
            return {"error": "Topic and AI trend analysis are required for intent classification."}

        trending_angles = ai_trend_analysis.get('trending_angles', [])

        system_prompt = """
        You are an expert SEO analyst. Your task is to classify the primary search intent for a given topic.
        Analyze the main topic and the trending angles provided.

        Classify the intent into ONE of these categories and provide a brief justification:
        - "Informational": The user wants to know something (e.g., "what is photosynthesis").
        - "Commercial Investigation": The user is comparing products/services (e.g., "best running shoes").
        - "Transactional": The user wants to buy something now (e.g., "buy nike air force 1").
        - "Navigational": The user wants to go to a specific site (e.g., "youtube").
        - "How-To/Instructional": The user wants to learn a specific task (e.g., "how to tie a tie").

        Respond in a JSON format with two keys: "intent" and "justification".
        """

        user_prompt = f"""
        Topic: "{topic}"
        Trending Angles: {json.dumps(trending_angles, indent=2)}

        Primary Search Intent Analysis:
        """

        if not self.llm:
            return {'error': 'Gemini API key not configured'}

        response = self.execute_prompt(system_prompt, user_prompt)
        parsed_response = self.parse_json_response(response)

        # Update the state with the new information
        state['search_intent'] = parsed_response.get('intent', 'unknown')
        state['search_intent_justification'] = parsed_response.get('justification', '')

        return state
