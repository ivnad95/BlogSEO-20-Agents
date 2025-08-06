from .base_agent import BaseAgent

class SchemaEnhancementAgent(BaseAgent):
    """PROFESSIONAL schema markup generator using Gemini AI."""
    
    def run(self, state: dict) -> dict:
        topic = state.get('topic', '')
        all_outputs = state.get('all_outputs', {})
        
        if not self.llm:
            return {'error': 'Gemini API key not configured'}
        
        system_prompt = """You are an expert in structured data and schema markup."""
        
        user_prompt = f"""Generate schema markup for '{topic}'.
        
        Provide schemas in JSON:
        {{
            "article_schema": {{"@type": "Article", "@context": "https://schema.org"}},
            "faq_schema": {{"@type": "FAQPage", "mainEntity": []}},
            "breadcrumb_schema": {{"@type": "BreadcrumbList"}},
            "recommended_schemas": ["schema1", "schema2"]
        }}"""
        
        response = self.execute_prompt(system_prompt, user_prompt)
        return self.parse_json_response(response)
