from .base_agent import BaseAgent
import json

class FinalAssemblyAgent(BaseAgent):
    """PROFESSIONAL content assembler using Gemini AI to integrate ALL agent outputs."""
    
    def run(self, state: dict) -> dict:
        all_outputs = state.get('all_outputs', {})
        
        # Extract key components from all agents
        draft = all_outputs.get('DraftWriterAgent', {}).get('draft', {})
        keywords = all_outputs.get('KeywordMiningAgent', {})
        seo_data = all_outputs.get('OnPageSEOAgent', {})
        technical_seo = all_outputs.get('TechnicalSEOAgent', {})
        schema = all_outputs.get('SchemaEnhancementAgent', {})
        images = all_outputs.get('ImageOptimizationAgent', {})
        readability = all_outputs.get('ReadabilityAgent', {})
        qa_validation = all_outputs.get('QAValidationAgent', {})
        
        # If we don't have Gemini API, return merged data
        if not self.llm:
            result = {
                'final_content': draft,
                'seo_metadata': seo_data,
                'technical_requirements': technical_seo,
                'schema_markup': schema,
                'images': images,
                'validation': qa_validation
            }
            return result
        
        # Use Gemini to intelligently merge all components
        system_prompt = """You are an expert content editor who assembles final, publication-ready blog posts.
        You integrate content, SEO optimization, technical requirements, and quality checks."""
        
        user_prompt = f"""Assemble the final blog post integrating ALL these components:
        
        DRAFT CONTENT: {json.dumps(draft, indent=2)[:2000]}
        SEO OPTIMIZATION: {json.dumps(seo_data, indent=2)[:500]}
        KEYWORDS TO VERIFY: {keywords.get('primary_keywords', [])[:10]}
        READABILITY IMPROVEMENTS: {json.dumps(readability, indent=2)[:500]}
        QA VALIDATION: {json.dumps(qa_validation, indent=2)[:500]}
        
        Create the FINAL blog post with:
        {{
            "title": "Final optimized title with primary keyword",
            "meta_description": "Compelling 155-char meta description",
            "url_slug": "seo-friendly-url",
            "content": "Complete HTML-formatted blog content with all sections",
            "word_count": number,
            "reading_time": "X minutes",
            "seo_score": "score/100",
            "tags": ["relevant", "tags"],
            "category": "main category",
            "internal_links": ["suggested internal links"],
            "external_links": ["authoritative external links"],
            "images_required": ["list of images needed"],
            "schema_markup": {{"structured data"}},
            "publish_ready": true/false,
            "optimization_notes": "any final notes"
        }}
        
        Ensure the content flows naturally, includes all keywords naturally, and is ready for publication."""
        
        response = self.execute_prompt(system_prompt, user_prompt)
        final_output = self.parse_json_response(response)
        
        # Merge with existing draft if needed
        if 'draft' in draft:
            final_output['original_draft'] = draft
        
        # Add validation status
        final_output['validation_status'] = qa_validation.get('ready_to_publish', False)
        
        return final_output
