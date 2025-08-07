import json
from agents.base_agent import BaseAgent

class StyleConsistencyAgent(BaseAgent):
    """
    An agent that specializes in ensuring a consistent writing style and tone
    throughout a blog post. It checks for a uniform voice, formatting, and
    overall coherence.
    """

    def run(self, state: dict) -> dict:
        """
        Executes the style consistency check.

        Args:
            state (dict): The current state of the blog post generation process.
                          It must contain 'draft_content'.

        Returns:
            dict: The updated state with style consistency analysis.
        """
        if 'draft_content' not in state:
            return {**state, "error": "Draft content not found for Style Consistency Agent."}

        system_prompt = """
        You are an expert editor AI with a keen eye for style and consistency.
        Your task is to analyze the provided blog post draft and identify any
        inconsistencies in style, tone, or formatting.

        Please check for the following:
        1.  **Tone of Voice**: Does the tone remain consistent throughout the article?
            (e.g., formal vs. informal, humorous vs. serious).
        2.  **Formatting**: Are headings, lists, and other formatted elements used consistently?
        3.  **Terminology**: Is terminology used consistently? (e.g., "AI agent" vs. "AI bot").
        4.  **Point of View**: Is the point of view consistent? (e.g., first person vs. third person).
        5.  **Overall Flow**: Does the article flow logically from one section to the next?

        Provide your feedback in a structured JSON format. For each point,
        briefly describe the issue and suggest a correction.
        """

        user_prompt = f"""
        Here is the blog post draft to analyze:
        ---
        {state['draft_content']}
        ---
        Please provide your style consistency analysis based on the instructions.
        """

        response = self.execute_prompt(system_prompt, user_prompt)
        style_consistency_analysis = self.parse_json_response(response)

        return {**state, "style_consistency_analysis": style_consistency_analysis}
