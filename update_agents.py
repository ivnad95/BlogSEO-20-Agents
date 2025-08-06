#!/usr/bin/env python3
"""
Update all agent files to use Gemini AI with professional prompts
"""

import os

# Template for each agent using Gemini AI
AGENT_TEMPLATES = {
    "outline_generator.py": '''from .base_agent import BaseAgent

class OutlineGeneratorAgent(BaseAgent):
    """PROFESSIONAL outline generator using Gemini AI."""
    
    def run(self, state: dict) -> dict:
        topic = state.get('topic', '')
        all_outputs = state.get('all_outputs', {})
        keywords = all_outputs.get('KeywordMiningAgent', {}).get('primary_keywords', [])
        
        if not self.llm:
            return {'error': 'Gemini API key not configured'}
        
        system_prompt = """You are an expert content strategist who creates comprehensive, SEO-optimized blog outlines."""
        
        user_prompt = f"""Create a detailed blog outline for '{topic}'.
        Keywords to include: {keywords[:10]}
        
        Provide JSON format:
        {{
            "sections": [
                {{"heading": "Section Title", "subpoints": ["point1", "point2"], "keywords": ["keyword1"]}}
            ],
            "estimated_word_count": 2000
        }}"""
        
        response = self.execute_prompt(system_prompt, user_prompt)
        return self.parse_json_response(response)
''',

    "competitor_scan.py": '''from .base_agent import BaseAgent

class CompetitorScanAgent(BaseAgent):
    """PROFESSIONAL competitor analysis using Gemini AI."""
    
    def run(self, state: dict) -> dict:
        topic = state.get('topic', '')
        
        if not self.llm:
            return {'error': 'Gemini API key not configured'}
        
        system_prompt = """You are an expert competitive analyst specializing in content gap analysis and SEO."""
        
        user_prompt = f"""Analyze competitor landscape for '{topic}'.
        
        Provide comprehensive analysis in JSON:
        {{
            "top_competitors": ["List 5 main competitors"],
            "content_gaps": ["Gap 1", "Gap 2"],
            "competitor_strengths": ["What they do well"],
            "opportunities": ["How to outrank them"],
            "unique_angles": ["Differentiation strategies"]
        }}"""
        
        response = self.execute_prompt(system_prompt, user_prompt)
        return self.parse_json_response(response)
''',

    "keyword_enrichment.py": '''from .base_agent import BaseAgent

class KeywordEnrichmentAgent(BaseAgent):
    """PROFESSIONAL keyword enrichment using Gemini AI."""
    
    def run(self, state: dict) -> dict:
        all_outputs = state.get('all_outputs', {})
        draft = all_outputs.get('DraftWriterAgent', {}).get('draft', {})
        keywords = all_outputs.get('KeywordMiningAgent', {}).get('primary_keywords', [])
        
        if not self.llm:
            return {'error': 'Gemini API key not configured'}
        
        system_prompt = """You are an SEO expert who optimizes content for keyword density and relevance."""
        
        user_prompt = f"""Enhance this content with natural keyword integration.
        Keywords to add: {keywords[:15]}
        Current content structure: {str(draft)[:500]}
        
        Provide suggestions in JSON:
        {{
            "keyword_placements": {{"keyword": "where and how to add it"}},
            "density_optimization": "recommendations",
            "semantic_variations": ["variation1", "variation2"]
        }}"""
        
        response = self.execute_prompt(system_prompt, user_prompt)
        return self.parse_json_response(response)
''',

    "readability.py": '''from .base_agent import BaseAgent

class ReadabilityAgent(BaseAgent):
    """PROFESSIONAL readability optimizer using Gemini AI."""
    
    def run(self, state: dict) -> dict:
        all_outputs = state.get('all_outputs', {})
        draft = all_outputs.get('DraftWriterAgent', {}).get('draft', {})
        
        if not self.llm:
            return {'error': 'Gemini API key not configured'}
        
        system_prompt = """You are an expert editor who optimizes content for readability and engagement."""
        
        user_prompt = f"""Analyze and improve readability of this content.
        Content: {str(draft)[:1000]}
        
        Provide improvements in JSON:
        {{
            "readability_score": "8/10",
            "improvements": ["suggestion1", "suggestion2"],
            "sentence_rewrites": {{"original": "improved"}},
            "paragraph_structure": "recommendations"
        }}"""
        
        response = self.execute_prompt(system_prompt, user_prompt)
        return self.parse_json_response(response)
''',

    "humanization.py": '''from .base_agent import BaseAgent

class HumanizationAgent(BaseAgent):
    """PROFESSIONAL content humanizer using Gemini AI."""
    
    def run(self, state: dict) -> dict:
        all_outputs = state.get('all_outputs', {})
        draft = all_outputs.get('DraftWriterAgent', {}).get('draft', {})
        
        if not self.llm:
            return {'error': 'Gemini API key not configured'}
        
        system_prompt = """You are an expert writer who makes content engaging, relatable, and human."""
        
        user_prompt = f"""Humanize this content to make it more engaging.
        Content: {str(draft)[:1000]}
        
        Provide humanization in JSON:
        {{
            "personal_stories": ["story example"],
            "emotional_hooks": ["hook1", "hook2"],
            "conversational_elements": ["element1"],
            "engagement_techniques": ["technique1"]
        }}"""
        
        response = self.execute_prompt(system_prompt, user_prompt)
        return self.parse_json_response(response)
''',

    "style_consistency.py": '''from .base_agent import BaseAgent

class StyleConsistencyAgent(BaseAgent):
    """PROFESSIONAL style consistency checker using Gemini AI."""
    
    def run(self, state: dict) -> dict:
        all_outputs = state.get('all_outputs', {})
        draft = all_outputs.get('DraftWriterAgent', {}).get('draft', {})
        
        if not self.llm:
            return {'error': 'Gemini API key not configured'}
        
        system_prompt = """You are an expert editor ensuring consistent voice and style."""
        
        user_prompt = f"""Analyze style consistency of this content.
        Content: {str(draft)[:1000]}
        
        Provide analysis in JSON:
        {{
            "style_score": "9/10",
            "inconsistencies": ["issue1", "issue2"],
            "tone_variations": ["where tone changes"],
            "recommendations": ["fix1", "fix2"]
        }}"""
        
        response = self.execute_prompt(system_prompt, user_prompt)
        return self.parse_json_response(response)
''',

    "tone_check.py": '''from .base_agent import BaseAgent

class ToneCheckAgent(BaseAgent):
    """PROFESSIONAL tone analyzer using Gemini AI."""
    
    def run(self, state: dict) -> dict:
        all_outputs = state.get('all_outputs', {})
        draft = all_outputs.get('DraftWriterAgent', {}).get('draft', {})
        target_tone = all_outputs.get('UserInputAgent', {}).get('tone', 'professional')
        
        if not self.llm:
            return {'error': 'Gemini API key not configured'}
        
        system_prompt = """You are an expert at analyzing and adjusting content tone."""
        
        user_prompt = f"""Analyze if content matches target tone: {target_tone}
        Content: {str(draft)[:1000]}
        
        Provide analysis in JSON:
        {{
            "current_tone": "detected tone",
            "tone_match_score": "8/10",
            "adjustments_needed": ["adjustment1"],
            "tone_examples": {{"original": "adjusted"}}
        }}"""
        
        response = self.execute_prompt(system_prompt, user_prompt)
        return self.parse_json_response(response)
''',

    "internal_linking.py": '''from .base_agent import BaseAgent

class InternalLinkingAgent(BaseAgent):
    """PROFESSIONAL internal linking strategist using Gemini AI."""
    
    def run(self, state: dict) -> dict:
        topic = state.get('topic', '')
        all_outputs = state.get('all_outputs', {})
        
        if not self.llm:
            return {'error': 'Gemini API key not configured'}
        
        system_prompt = """You are an SEO expert specializing in internal linking strategies."""
        
        user_prompt = f"""Create internal linking strategy for '{topic}'.
        
        Provide strategy in JSON:
        {{
            "pillar_pages": ["main topic pages to link to"],
            "supporting_pages": ["related content to link"],
            "anchor_text_variations": ["text1", "text2"],
            "link_placement": ["where to add links"],
            "link_flow": "how links should flow"
        }}"""
        
        response = self.execute_prompt(system_prompt, user_prompt)
        return self.parse_json_response(response)
''',

    "external_link_vetting.py": '''from .base_agent import BaseAgent

class ExternalLinkVettingAgent(BaseAgent):
    """PROFESSIONAL external link curator using Gemini AI."""
    
    def run(self, state: dict) -> dict:
        topic = state.get('topic', '')
        
        if not self.llm:
            return {'error': 'Gemini API key not configured'}
        
        system_prompt = """You are an expert at finding and vetting authoritative external sources."""
        
        user_prompt = f"""Find authoritative external links for '{topic}'.
        
        Provide recommendations in JSON:
        {{
            "authoritative_sources": [
                {{"url": "example.com", "domain_authority": "high", "relevance": "why relevant"}}
            ],
            "research_papers": ["paper1", "paper2"],
            "industry_resources": ["resource1"],
            "news_sources": ["source1"]
        }}"""
        
        response = self.execute_prompt(system_prompt, user_prompt)
        return self.parse_json_response(response)
''',

    "image_optimization.py": '''from .base_agent import BaseAgent

class ImageOptimizationAgent(BaseAgent):
    """PROFESSIONAL image optimization strategist using Gemini AI."""
    
    def run(self, state: dict) -> dict:
        topic = state.get('topic', '')
        all_outputs = state.get('all_outputs', {})
        
        if not self.llm:
            return {'error': 'Gemini API key not configured'}
        
        system_prompt = """You are an expert in visual content strategy and image SEO."""
        
        user_prompt = f"""Create image strategy for '{topic}'.
        
        Provide strategy in JSON:
        {{
            "hero_image": {{"description": "what it should show", "keywords": ["img keyword"]}},
            "supporting_images": [
                {{"type": "infographic", "content": "what to include", "alt_text": "SEO alt text"}}
            ],
            "image_seo": {{"file_naming": "convention", "compression": "recommendations"}},
            "visual_hierarchy": "how to structure images"
        }}"""
        
        response = self.execute_prompt(system_prompt, user_prompt)
        return self.parse_json_response(response)
''',

    "alt_text.py": '''from .base_agent import BaseAgent

class AltTextAgent(BaseAgent):
    """PROFESSIONAL alt text generator using Gemini AI."""
    
    def run(self, state: dict) -> dict:
        all_outputs = state.get('all_outputs', {})
        images = all_outputs.get('ImageOptimizationAgent', {})
        
        if not self.llm:
            return {'error': 'Gemini API key not configured'}
        
        system_prompt = """You are an expert at writing SEO-optimized, accessible alt text."""
        
        user_prompt = f"""Generate alt text for these images: {images}
        
        Provide alt texts in JSON:
        {{
            "alt_texts": [
                {{"image": "hero_image", "alt": "descriptive SEO alt text", "title": "image title"}}
            ],
            "seo_guidelines": ["guideline1", "guideline2"]
        }}"""
        
        response = self.execute_prompt(system_prompt, user_prompt)
        return self.parse_json_response(response)
''',

    "onpage_seo.py": '''from .base_agent import BaseAgent

class OnPageSEOAgent(BaseAgent):
    """PROFESSIONAL on-page SEO optimizer using Gemini AI."""
    
    def run(self, state: dict) -> dict:
        topic = state.get('topic', '')
        all_outputs = state.get('all_outputs', {})
        keywords = all_outputs.get('KeywordMiningAgent', {}).get('primary_keywords', [])
        
        if not self.llm:
            return {'error': 'Gemini API key not configured'}
        
        system_prompt = """You are an expert in on-page SEO optimization."""
        
        user_prompt = f"""Optimize on-page SEO for '{topic}'.
        Primary keywords: {keywords[:10]}
        
        Provide optimization in JSON:
        {{
            "title_tag": "SEO optimized title under 60 chars",
            "meta_description": "Compelling description under 155 chars",
            "h1_tag": "Main heading",
            "h2_tags": ["Subheading 1", "Subheading 2"],
            "url_slug": "seo-friendly-url",
            "canonical_url": "recommendation",
            "open_graph": {{"og:title": "social title", "og:description": "social desc"}}
        }}"""
        
        response = self.execute_prompt(system_prompt, user_prompt)
        return self.parse_json_response(response)
''',

    "technical_seo.py": '''from .base_agent import BaseAgent

class TechnicalSEOAgent(BaseAgent):
    """PROFESSIONAL technical SEO advisor using Gemini AI."""
    
    def run(self, state: dict) -> dict:
        all_outputs = state.get('all_outputs', {})
        
        if not self.llm:
            return {'error': 'Gemini API key not configured'}
        
        system_prompt = """You are a technical SEO expert."""
        
        user_prompt = f"""Provide technical SEO recommendations.
        
        Return in JSON:
        {{
            "page_speed": ["optimization1", "optimization2"],
            "mobile_optimization": ["mobile fix1"],
            "crawlability": ["improvement1"],
            "indexability": ["recommendation1"],
            "structured_data": ["schema type to add"]
        }}"""
        
        response = self.execute_prompt(system_prompt, user_prompt)
        return self.parse_json_response(response)
''',

    "schema_enhancement.py": '''from .base_agent import BaseAgent

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
''',

    "qa_validation.py": '''from .base_agent import BaseAgent

class QAValidationAgent(BaseAgent):
    """PROFESSIONAL quality assurance validator using Gemini AI."""
    
    def run(self, state: dict) -> dict:
        all_outputs = state.get('all_outputs', {})
        
        if not self.llm:
            return {'error': 'Gemini API key not configured'}
        
        system_prompt = """You are a quality assurance expert for content."""
        
        user_prompt = f"""Perform quality check on the blog post.
        
        Provide QA report in JSON:
        {{
            "quality_score": "9/10",
            "factual_accuracy": "verified",
            "grammar_issues": ["issue1"],
            "seo_compliance": "pass",
            "improvements": ["suggestion1"],
            "ready_to_publish": true
        }}"""
        
        response = self.execute_prompt(system_prompt, user_prompt)
        return self.parse_json_response(response)
''',

    "final_assembly.py": '''from .base_agent import BaseAgent

class FinalAssemblyAgent(BaseAgent):
    """PROFESSIONAL content assembler using Gemini AI."""
    
    def run(self, state: dict) -> dict:
        all_outputs = state.get('all_outputs', {})
        
        if not self.llm:
            return {'error': 'Gemini API key not configured'}
        
        system_prompt = """You are an expert content editor who assembles final blog posts."""
        
        user_prompt = f"""Assemble the final blog post from all components.
        Components: {list(all_outputs.keys())}
        
        Create final output in JSON:
        {{
            "title": "Final SEO title",
            "meta_description": "Final meta",
            "content": "Complete formatted blog content",
            "tags": ["tag1", "tag2"],
            "category": "category",
            "publish_ready": true
        }}"""
        
        response = self.execute_prompt(system_prompt, user_prompt)
        final = self.parse_json_response(response)
        
        # Merge with draft content
        draft = all_outputs.get('DraftWriterAgent', {}).get('draft', {})
        final.update(draft)
        
        return final
''',
}

def update_agents():
    """Update all agent files with Gemini AI implementations."""
    agents_dir = "agents"
    
    for filename, content in AGENT_TEMPLATES.items():
        filepath = os.path.join(agents_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"✅ Updated {filename}")
        else:
            print(f"⚠️ File not found: {filename}")

if __name__ == "__main__":
    update_agents()
    print("\n✅ All agents updated to use Gemini AI!")
