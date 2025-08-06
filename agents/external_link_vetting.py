from .base_agent import BaseAgent
from utilities.api_clients import DuckDuckGoSearchClient
import json

class ExternalLinkVettingAgent(BaseAgent):
    """
    Identifies claims in the text, finds authoritative external sources,
    and inserts them as links. Part of agent A17.
    """
    model_name: str = "gemini-1.5-pro-latest"

    def run(self, state: dict) -> dict:
        """
        Analyzes the draft, finds external sources, and adds them as links.
        """
        if not self.llm:
            return {'error': 'Gemini API key not configured'}

        draft = state.get('draft', {})
        current_text = draft.get('full_text')

        if not current_text:
            return {'error': 'Draft text is required for external linking.'}

        # Step 1: Identify claims that need citations
        opportunities = self._find_linking_opportunities(current_text)
        if not opportunities:
            return state # No opportunities found, so no changes needed

        # Step 2: Find authoritative URLs for each opportunity
        links_to_add = self._find_authoritative_links(opportunities)
        if not links_to_add:
            return state # No links found

        # Step 3: Rewrite the text to include the links
        text_with_external_links = self._insert_links(current_text, links_to_add)
        
        state['draft']['full_text'] = text_with_external_links
        return state

    def _find_linking_opportunities(self, text: str) -> list:
        """Use an LLM to find sentences that would benefit from a citation."""
        system_prompt = "You are a research assistant. Your task is to identify specific factual claims in a text that would be stronger if they were supported by a citation to an authoritative external source."
        user_prompt = f"""
        Read the following text. Identify up to 5 specific, factual claims that a reader might want to verify. Do not select opinions or general statements.

        **Text to Analyze:**
        ---
        {text}
        ---

        Return the claims as a JSON object with a single key "claims_to_cite", which is a list of strings.
        Example: {{"claims_to_cite": ["The sky appears blue due to Rayleigh scattering.", "The Earth's circumference is approximately 40,075 kilometers."]}}
        """
        response = self.execute_prompt(system_prompt, user_prompt)
        return self.parse_json_response(response).get('claims_to_cite', [])

    def _find_authoritative_links(self, claims: list) -> list:
        """Use a search tool to find a good source for each claim."""
        try:
            search_client = DuckDuckGoSearchClient()
        except Exception as e:
            print(f"Could not initialize search client: {e}")
            return []

        links = []
        for claim in claims:
            try:
                # Prioritize high-authority domains
                query = f'"{claim}" site:.edu OR site:.gov OR site:.org OR site:wikipedia.org'
                search_results = search_client.search(query, max_results=1)
                if search_results:
                    links.append({"claim": claim, "url": search_results[0]['href']})
            except Exception as e:
                print(f"Search failed for claim '{claim}': {e}")
        return links

    def _insert_links(self, text: str, links: list) -> str:
        """Use an LLM to rewrite the text and add the links naturally."""
        system_prompt = "You are an expert editor. Your task is to revise a text to include citations as markdown links. The links should be added smoothly and naturally without disrupting the flow."
        user_prompt = f"""
        Please revise the following text to include the provided citations. Find the sentence related to each claim and add the corresponding URL as a markdown link.

        **Citations to Add:**
        {json.dumps(links, indent=2)}

        **Original Text:**
        ---
        {text}
        ---

        Return ONLY the full, revised text with the markdown external links added. Do not add any commentary.
        """
        return self.execute_prompt(system_prompt, user_prompt)
