from .base_agent import BaseAgent
import json
from datetime import datetime

class SchemaEnhancementAgent(BaseAgent):
    """
    Analyzes the final article to generate relevant Article and FAQPage
    JSON-LD schema for technical SEO. This corresponds to agent A18.
    """
    # This is a structured data generation task, flash model is sufficient.
    model_name: str = "gemini-1.5-flash-latest"

    def run(self, state: dict) -> dict:
        """
        Generates schema.org markup for the article.

        Args:
            state: Shared state dictionary, must contain 'draft' and 'topic'.

        Returns:
            The updated state with a 'schemas' dictionary.
        """
        if not self.llm:
            return {'error': 'Gemini API key not configured'}

        draft = state.get('draft', {})
        topic = state.get('topic', 'Untitled Article')
        full_text = draft.get('full_text')

        if not full_text:
            return {'error': 'Draft text is required for schema generation.'}

        # 1. Generate Article Schema
        article_schema = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": topic,
            "datePublished": datetime.utcnow().isoformat() + "Z",
            "author": {
                "@type": "Person",
                "name": "AI Content Team" # Placeholder author
            },
            "publisher": {
                "@type": "Organization",
                "name": "AI Blog",
                "logo": {
                    "@type": "ImageObject",
                    "url": "https://example.com/logo.png" # Placeholder logo
                }
            }
        }

        # 2. Generate FAQ Schema by extracting Q&As from the text
        system_prompt = "You are an expert in extracting structured data from text. Your task is to identify question-and-answer pairs within a given article."
        user_prompt = f"""
        Read the following article text. Identify up to 5 distinct questions and their corresponding answers.

        **Article Text:**
        ---
        {full_text}
        ---

        Return the findings as a JSON object with a single key, "faq_pairs", which is a list of objects. Each object should have two keys: "question" and "answer".
        Example:
        {{
            "faq_pairs": [
                {{
                    "question": "What is the main purpose of photosynthesis?",
                    "answer": "The main purpose of photosynthesis is to convert light energy into chemical energy..."
                }}
            ]
        }}
        If no clear Q&A pairs are found, return an empty list.
        """
        
        response = self.execute_prompt(system_prompt, user_prompt)
        faq_pairs = self.parse_json_response(response).get('faq_pairs', [])

        faq_schema = None
        if faq_pairs and isinstance(faq_pairs, list):
            faq_schema = {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": pair['question'],
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": pair['answer']
                        }
                    } for pair in faq_pairs if 'question' in pair and 'answer' in pair
                ]
            }

        state['schemas'] = {
            "article_schema": article_schema,
            "faq_schema": faq_schema
        }

        return state
