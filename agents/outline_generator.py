from .base_agent import BaseAgent
import json

class OutlineGeneratorAgent(BaseAgent):
    # This agent synthesizes a large amount of strategic input into a detailed structure.
    model_name: str = "gemini-1.5-pro-latest"

    """
    PROFESSIONAL outline generator that synthesizes all prior research
    (trends, intent, competitor gaps, keywords) into a strategic, SEO-optimized
    content blueprint using Gemini AI. This corresponds to agent A7.
    """

    def run(self, state: dict) -> dict:
        """
        Creates a detailed, strategic outline based on the comprehensive state.

        Args:
            state: The shared state dictionary, containing outputs from all previous agents.

        Returns:
            A dictionary containing the detailed content outline.
        """
        if not self.llm:
            return {'error': 'Gemini API key not configured'}

        # Gather all the intelligence from previous agents
        topic = state.get('topic', 'the specified topic')
        search_intent = state.get('search_intent', 'not specified')
        # Assuming the output of the competitor scan is in the state
        content_gaps = state.get('content_gaps', [])
        unique_angles = state.get('unique_angles', [])
        # Assuming the output of the keyword miner is in the state
        keyword_strategy = state.get('keyword_strategy', {})
        primary_keywords = keyword_strategy.get('primary_keywords', [])
        question_keywords = keyword_strategy.get('question_keywords', [])
        keyword_clusters = keyword_strategy.get('keyword_clusters', {})

        system_prompt = """You are an expert content strategist and SEO architect. Your job is to create a comprehensive, highly-detailed, and strategically-sound blog post outline. You must synthesize all available data—search intent, competitor weaknesses, and keyword strategy—to build a blueprint for an article that will rank #1."""

        user_prompt = f"""
        I need a world-class blog post outline for the topic: "{topic}".
        You must use all the following strategic inputs to construct the outline:

        --- STRATEGIC INPUTS ---
        1.  **Primary Search Intent:** {search_intent} (The outline's structure must satisfy this intent.)
        2.  **Identified Content Gaps from Competitors:** {json.dumps(content_gaps)} (The outline MUST address these gaps.)
        3.  **Unique Angles for Differentiation:** {json.dumps(unique_angles)} (The outline should incorporate these angles.)
        4.  **Core Keyword Clusters to Structure Around:** {json.dumps(keyword_clusters)} (The main sections of the outline should be based on these clusters.)
        5.  **Key Questions to Answer:** {json.dumps(question_keywords)} (Ensure the outline explicitly answers these questions, perhaps in an FAQ section.)
        6.  **Primary Keywords to Include:** {json.dumps(primary_keywords)} (These should be naturally integrated into headings and subpoints.)
        --- END STRATEGIC INPUTS ---

        Now, generate the outline in a detailed JSON format. The JSON object should have a single root key "outline".
        The "outline" key should contain a list of section objects. Each section object must have:
        - "title": A compelling, SEO-friendly heading for the section (e.g., "H2: Understanding the Basics of X").
        - "subsections": A list of detailed sub-points, instructions, or topics to cover within that section. These should be descriptive.
        - "keywords_to_include": A list of specific keywords from the input lists that should be prioritized in this section.

        Example of a single section object:
        {{
            "title": "H2: What is Photosynthesis and Why Is It Important?",
            "subsections": [
                "Define photosynthesis in simple terms.",
                "Explain the chemical equation of photosynthesis.",
                "Discuss the role of chlorophyll and sunlight.",
                "Cover the importance of photosynthesis for life on Earth."
            ],
            "keywords_to_include": ["what is photosynthesis", "photosynthesis for kids"]
        }}

        Create a full outline with an introduction, at least 3-5 main body sections based on the keyword clusters, and a conclusion. Include an FAQ section if it makes sense for the question keywords.
        """

        response = self.execute_prompt(system_prompt, user_prompt)
        parsed_response = self.parse_json_response(response)

        # Add the outline to the main state
        state['outline'] = parsed_response.get('outline', {})
        return state
