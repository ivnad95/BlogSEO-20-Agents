from .base_agent import BaseAgent
from utilities.validators import check_grammar, calculate_similarity
from utilities.api_clients import DuckDuckGoSearchClient
import json

class QAValidationAgent(BaseAgent):
    # This agent performs multiple complex analysis, extraction, and rewriting tasks.
    model_name: str = "gemini-1.5-pro-latest"

    """
    PROFESSIONAL QA agent that performs grammar correction, fact-checking, and
    originality analysis. This agent covers the roles of A12, A14, and A19.
    """

    def run(self, state: dict) -> dict:
        """
        Performs a multi-step QA process on the draft.

        Args:
            state: Shared state dictionary.

        Returns:
            The updated state with the QA report and corrected text.
        """
        if not self.llm:
            return {'error': 'Gemini API key not configured'}

        draft = state.get('draft', {})
        current_text = draft.get('full_text')
        competitor_content = state.get('competitor_content', [])

        if not current_text:
            return {'error': 'Draft text is required for QA.'}

        # --- A12: Grammar & Syntax Correction ---
        grammar_mistakes = check_grammar(current_text)
        corrected_text = self._correct_grammar(current_text, grammar_mistakes)
        state['draft']['full_text'] = corrected_text # Update the main draft with corrections
        
        # --- A19: Originality Check ---
        originality_report = []
        if competitor_content:
            for competitor in competitor_content:
                if 'content_summary' in competitor and competitor['content_summary']:
                    similarity_score = calculate_similarity(corrected_text, competitor['content_summary'])
                    originality_report.append({
                        "competitor_url": competitor.get('url'),
                        "similarity_score": f"{similarity_score:.2%}"
                    })

        # --- A14: Fact-Checking ---
        fact_check_report = self._perform_fact_check(corrected_text)

        # --- Final QA Report ---
        state['qa_report'] = {
            "grammar_validation": {
                "mistake_count": len(grammar_mistakes),
                "mistakes_found": [m['message'] for m in grammar_mistakes[:5]] # Show first 5 messages
            },
            "originality_validation": originality_report,
            "fact_checking_validation": fact_check_report
        }
        
        return state

    def _correct_grammar(self, text: str, mistakes: list) -> str:
        """Uses an LLM to intelligently apply grammar corrections."""
        if not mistakes:
            return text

        system_prompt = "You are an expert editor. Your task is to correct grammar mistakes in a text based on a provided list of errors. Apply the corrections intelligently and naturally. Only fix the specified errors."
        user_prompt = f"""
        Please correct the following text based on the grammar mistakes listed below.

        **Grammar Mistakes Found by LanguageTool:**
        {json.dumps(mistakes[:10], indent=2)}

        **Original Text:**
        ---
        {text}
        ---

        Return ONLY the full, corrected text.
        """
        return self.execute_prompt(system_prompt, user_prompt)

    def _perform_fact_check(self, text: str) -> dict:
        """Identifies claims and uses web search to verify them."""
        # 1. Extract claims with an LLM
        claim_extraction_prompt = f"""
        From the following text, extract up to 5 main factual claims that should be fact-checked. A factual claim is a statement that can be verified with evidence. Do not extract opinions or general statements.

        **Text:**
        ---
        {text}
        ---
        
        Return the claims as a JSON list of strings: {{"claims": ["claim 1", "claim 2", ...]}}
        """
        claims_response = self.execute_prompt("You are a data extraction expert.", claim_extraction_prompt)
        claims = self.parse_json_response(claims_response).get('claims', [])

        if not claims:
            return {"status": "No specific claims were identified to check."}

        # 2. Verify each claim with web search
        try:
            search_client = DuckDuckGoSearchClient()
        except Exception as e:
            return {"status": f"Could not initialize search client: {e}"}

        verification_results = []
        for claim in claims:
            try:
                search_results = search_client.search(claim, max_results=3)
                snippets = [f"{res.get('title', '')}: {res.get('body', '')}" for res in search_results]
                verification_results.append({"claim": claim, "evidence": snippets})
            except Exception as e:
                verification_results.append({"claim": claim, "evidence": f"Search failed: {e}"})
        
        # 3. Final analysis with LLM
        analysis_prompt = f"""
        You are a fact-checker. Based on the provided claims and the supporting evidence from web search snippets, assess the likely accuracy of each claim.

        **Claims and Evidence:**
        ---
        {json.dumps(verification_results, indent=2)}
        ---

        Provide a final report in JSON format with a list of objects, where each object has "claim", "supporting_evidence_summary", and a "verification_status" of "Verified", "Contradicted", or "Inconclusive".
        """
        final_report = self.execute_prompt("You are a meticulous fact-checker.", analysis_prompt)
        return self.parse_json_response(final_report)
