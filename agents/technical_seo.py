import json
from agents.base_agent import BaseAgent

class TechnicalSEOAgent(BaseAgent):
    """
    An agent specialized in enhancing the technical SEO aspects of a blog post.
    This agent checks for mobile-friendliness, page speed optimizations, and other
    technical factors that are crucial for search engine ranking.
    """

    def run(self, state: dict) -> dict:
        """
        Executes the technical SEO analysis.

        Args:
            state (dict): The current state of the blog post generation process.
                          It must contain 'draft_content'.

        Returns:
            dict: The updated state with technical SEO recommendations.
        """
        if 'draft_content' not in state:
            return {**state, "error": "Draft content not found for Technical SEO Agent."}

        system_prompt = """
        You are a Technical SEO Specialist AI. Your task is to analyze the provided blog content
        and suggest technical SEO improvements. Focus on actionable advice that can be
        implemented by a developer or a content manager.

        Analyze the following aspects:
        1.  **Mobile-Friendliness**: Is the content structured in a way that's easy to read on mobile?
            (e.g., short paragraphs, bullet points, clear headings).
        2.  **Page Speed**: What elements in the content could slow down page load?
            (e.g., large images, complex tables). Suggest optimizations.
        3.  **Structured Data (Schema Markup)**: What schema.org types would be relevant for this content?
            (e.g., Article, FAQPage, HowTo). Provide a sample JSON-LD snippet.
        4.  **URL Structure**: Suggest a clean, SEO-friendly URL slug for this post.
        5.  **Accessibility (a11y)**: Provide three recommendations to make the content more accessible
            to people with disabilities (e.g., descriptive links, ARIA labels for complex elements).

        Present your analysis in a structured JSON format.
        """

        user_prompt = f"""
        Here is the blog post draft:
        ---
        {state['draft_content']}
        ---
        Please provide your technical SEO analysis based on the instructions.
        """

        response = self.execute_prompt(system_prompt, user_prompt)
        technical_seo_analysis = self.parse_json_response(response)

        return {**state, "technical_seo_analysis": technical_seo_analysis}
