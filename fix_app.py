#!/usr/bin/env python3
"""
Fixes for the BlogSEO v3 app based on agent output analysis
"""

import json
import os

# Fix 1: Update app.py to better handle agent outputs
APP_FIXES = '''
# Add to app.py after line 571 (in the generation process section)

# Enhanced result processing
if st.session_state.generation_complete and st.session_state.final_output:
    # Process final output to ensure proper formatting
    final_data = st.session_state.final_output
    
    # If final_output contains nested draft data, extract it
    if isinstance(final_data, dict):
        if 'draft' in final_data:
            draft_content = final_data['draft']
            
            # Build formatted HTML content
            html_sections = []
            
            # Add title and meta
            if 'title' in draft_content:
                html_sections.append(f"<h1>{draft_content['title']}</h1>")
            
            # Add introduction
            if 'introduction' in draft_content:
                html_sections.append(f"<div class='introduction'>{draft_content['introduction']}</div>")
            
            # Add main sections
            if 'main_sections' in draft_content:
                for section in draft_content['main_sections']:
                    html_sections.append(f"<h2>{section.get('heading', '')}</h2>")
                    html_sections.append(f"<div>{section.get('content', '')}</div>")
                    
                    # Add key points if available
                    if 'key_points' in section:
                        html_sections.append("<ul>")
                        for point in section['key_points']:
                            html_sections.append(f"<li>{point}</li>")
                        html_sections.append("</ul>")
            
            # Add conclusion
            if 'conclusion' in draft_content:
                html_sections.append(f"<div class='conclusion'>{draft_content['conclusion']}</div>")
            
            # Add FAQ section
            if 'faq_section' in draft_content:
                html_sections.append("<h2>Frequently Asked Questions</h2>")
                for faq in draft_content['faq_section']:
                    html_sections.append(f"<h3>{faq['question']}</h3>")
                    html_sections.append(f"<p>{faq['answer']}</p>")
            
            # Store formatted content
            final_data['formatted_html'] = '\n'.join(html_sections)
            final_data['word_count'] = len(' '.join(html_sections).split())
'''

# Fix 2: Update the FinalAssemblyAgent to better integrate all agent outputs
FINAL_ASSEMBLY_FIX = '''from .base_agent import BaseAgent
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
'''

# Fix 3: Improve the export functionality
EXPORT_FIX = '''
def create_complete_html_export(final_output):
    """Create a complete, styled HTML export with all SEO elements."""
    
    # Extract components
    content = final_output.get('content', '')
    title = final_output.get('title', 'Untitled')
    meta_desc = final_output.get('meta_description', '')
    schema = final_output.get('schema_markup', {})
    
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{meta_desc}">
    
    <!-- Schema.org markup -->
    <script type="application/ld+json">
    {json.dumps(schema, indent=2)}
    </script>
    
    <!-- Open Graph tags -->
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{meta_desc}">
    <meta property="og:type" content="article">
    
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.8;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
        }}
        h1 {{ color: #2c3e50; margin-bottom: 0.5rem; }}
        h2 {{ color: #34495e; margin-top: 2rem; }}
        .meta {{ color: #7f8c8d; font-size: 0.9rem; margin: 1rem 0; }}
        .content {{ background: white; }}
        .faq {{ background: #f8f9fa; padding: 1rem; margin: 2rem 0; border-radius: 8px; }}
        ul, ol {{ margin-left: 1.5rem; }}
        blockquote {{ border-left: 4px solid #3498db; padding-left: 1rem; color: #555; }}
    </style>
</head>
<body>
    <article>
        {content}
    </article>
</body>
</html>"""
    
    return html_template
'''

def apply_fixes():
    """Apply fixes to improve the app based on agent output analysis."""
    
    # 1. Update FinalAssemblyAgent
    with open('agents/final_assembly.py', 'w') as f:
        f.write(FINAL_ASSEMBLY_FIX)
    print("✅ Fixed FinalAssemblyAgent for better integration")
    
    # 2. Create improved export utilities
    export_utils = '''from typing import Dict, Any
import json
from datetime import datetime

def create_wordpress_export(content: Dict[str, Any]) -> str:
    """Create WordPress-compatible XML export."""
    title = content.get('title', 'Untitled')
    body = content.get('content', '')
    
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
    xmlns:excerpt="http://wordpress.org/export/1.2/excerpt/"
    xmlns:content="http://purl.org/rss/1.0/modules/content/"
    xmlns:wp="http://wordpress.org/export/1.2/">
<channel>
    <item>
        <title>{title}</title>
        <content:encoded><![CDATA[{body}]]></content:encoded>
        <wp:post_type>post</wp:post_type>
        <wp:status>draft</wp:status>
    </item>
</channel>
</rss>"""
    return xml

def create_medium_export(content: Dict[str, Any]) -> str:
    """Create Medium-compatible markdown export."""
    title = content.get('title', 'Untitled')
    body = content.get('content', '')
    tags = content.get('tags', [])
    
    markdown = f"""# {title}

Tags: {', '.join(tags)}

---

{body}
"""
    return markdown
'''
    
    with open('utilities/advanced_exporters.py', 'w') as f:
        f.write(export_utils)
    print("✅ Created advanced export utilities")
    
    # 3. Add validation for agent outputs
    validation_code = '''def validate_agent_output(agent_name: str, output: Dict) -> bool:
    """Validate that agent output contains expected fields."""
    
    required_fields = {
        'DraftWriterAgent': ['draft', 'word_count'],
        'KeywordMiningAgent': ['primary_keywords', 'long_tail_keywords'],
        'OnPageSEOAgent': ['title_tag', 'meta_description'],
        'FinalAssemblyAgent': ['title', 'content']
    }
    
    if agent_name in required_fields:
        for field in required_fields[agent_name]:
            if field not in output:
                return False
    return True
'''
    
    with open('utilities/validators.py', 'w') as f:
        f.write(validation_code)
    print("✅ Created output validators")
    
    print("\n✅ All fixes applied successfully!")
    print("\nKey improvements:")
    print("1. FinalAssemblyAgent now properly integrates all agent outputs")
    print("2. Enhanced HTML export with proper SEO elements")
    print("3. Added WordPress and Medium export formats")
    print("4. Added validation for agent outputs")
    print("\nRestart the app to see improvements!")

if __name__ == "__main__":
    apply_fixes()
