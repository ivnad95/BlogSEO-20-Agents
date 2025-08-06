from .base_agent import BaseAgent
from utilities.text_analysis import extract_keywords_yake, extract_keywords_keybert, model_topics_bertopic
import json

class KeywordMiningAgent(BaseAgent):
    # This agent performs heavy analysis and synthesis, requiring a more powerful model.
    model_name: str = "gemini-1.5-pro-latest"

    """
    PROFESSIONAL keyword and topic analysis agent. It uses text analysis models on
    competitor content and synthesizes the findings with Gemini AI for advanced SEO insights.
    This agent covers the roles of both Keyword Extraction (A5) and Topical Authority Modeler (A6).
    """

    def run(self, state: dict) -> dict:
        """
        Mines keywords and models topics from competitor text, then uses an LLM for strategic analysis.

        Args:
            state: Shared state dictionary. Must contain the output from CompetitorScanAgent,
                   expected under a key like 'competitor_analysis'.

        Returns:
            A dictionary with a comprehensive keyword and topic analysis.
        """
        # This agent relies on the output of the competitor scan.
        # The orchestrator should place the output of the competitor scan into the state.
        # We'll look for a key like 'competitor_content' within the state.
        competitor_content = state.get('competitor_content', [])
        
        if not competitor_content:
             # Fallback for testing or if the key name is different
            if state.get('competitor_analysis', {}).get('competitor_content'):
                competitor_content = state['competitor_analysis']['competitor_content']
            else:
                return {"error": "Competitor content from a previous step is required for keyword mining."}

        # 1. Consolidate text and run local text analysis
        full_text_corpus = " ".join([item.get('content_summary', '') for item in competitor_content])
        document_list = [item.get('content_summary', '') for item in competitor_content if item.get('content_summary')]

        if not full_text_corpus.strip():
            return {"error": "Competitor content is empty or invalid."}

        # Extract keywords using multiple methods for diversity
        keywords_yake = extract_keywords_yake(full_text_corpus, max_keywords=30)
        keywords_keybert = extract_keywords_keybert(full_text_corpus, top_n=20)
        
        # Model topics from the documents
        try:
            # Check if there are enough documents for BERTopic
            if len(document_list) > 1:
                topic_info, topic_keywords_raw = model_topics_bertopic(document_list)
                # Convert BERTopic output to a more JSON-friendly format
                topic_clusters = {f"Topic {topic_id}": [word for word, score in words] for topic_id, words in topic_keywords_raw.items() if topic_id != -1}
            else:
                topic_clusters = {"info": "Not enough documents to perform topic modeling."}
        except Exception as e:
            topic_clusters = {"error": f"Failed to model topics: {e}"}

        # 2. Synthesize with LLM
        if not self.llm:
            return {'error': 'Gemini API key not configured'}

        system_prompt = """You are a world-class SEO strategist and data analyst. Your job is to take raw data from text analysis tools and transform it into a strategic keyword and topical authority plan. You must distinguish between what the tools found and the strategy you are creating."""

        user_prompt = f"""
        I have analyzed the content of top competitors for a topic. Here is the raw data I extracted:

        --- RAW DATA ---
        Keywords extracted by YAKE (a statistical extractor): {json.dumps(keywords_yake, indent=2)}
        Keywords extracted by KeyBERT (a transformer-based extractor): {json.dumps(keywords_keybert, indent=2)}
        Topic clusters identified by BERTopic: {json.dumps(topic_clusters, indent=2)}
        --- END RAW DATA ---

        Based on this data, create a comprehensive SEO strategy in JSON format. The strategy should include:
        
        - "primary_keywords": Identify the top 5-7 most important primary keywords from the raw data.
        - "long_tail_keywords": Generate 10-15 specific, long-tail variations inspired by the raw keywords and topics.
        - "semantic_keywords": List 10 LSI/semantic keywords that are conceptually related to the topic clusters.
        - "question_keywords": Formulate 10 question-based keywords that the content should answer, based on the identified topics.
        - "keyword_clusters": Refine the raw topic clusters into a logical structure. Group related keywords under 3-5 clear, human-readable cluster names (e.g., "Understanding the Basics", "Advanced Techniques", "Product Comparisons").
        - "topical_authority_plan": Provide a brief 2-3 sentence plan on how to build topical authority, referencing the identified clusters. Explain which topics seem most important based on the data.
        - "search_intent_mapping": For the primary keywords, map each one to a likely search intent (e.g., "Informational", "Commercial").
        """

        response = self.execute_prompt(system_prompt, user_prompt)
        keyword_analysis = self.parse_json_response(response)

        # Combine raw data with LLM analysis for a full report
        state.update({
            "keyword_strategy": keyword_analysis,
            "raw_keyword_data": {
                "yake_keywords": keywords_yake,
                "keybert_keywords": keywords_keybert,
                "bertopic_clusters": topic_clusters
            }
        })
        return state
