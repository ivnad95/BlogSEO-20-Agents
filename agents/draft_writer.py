from .base_agent import BaseAgent
import json

class DraftWriterAgent(BaseAgent):
    """PROFESSIONAL content writer using Gemini AI for high-quality blog generation."""
    
    def run(self, state: dict) -> dict:
        """Generate PROFESSIONAL blog content using Gemini AI."""
        topic = state.get('topic', '')
        all_outputs = state.get('all_outputs', {})
        
        # Extract context from previous agents
        trends_data = all_outputs.get('TrendIdeaAgent', {})
        user_data = all_outputs.get('UserInputAgent', {})
        keywords_data = all_outputs.get('KeywordMiningAgent', {})
        
        # Get data
        ai_trends = trends_data.get('ai_trend_analysis', {})
        target_keywords = keywords_data.get('primary_keywords', [])
        content_opportunities = ai_trends.get('content_opportunities', [])
        
        if not self.llm:
            return {'error': 'Gemini API key not configured'}
        
        result = {'sections': []}
        
        # Generate comprehensive blog post using Gemini
        system_prompt = """You are an expert SEO content writer who creates engaging, informative, and highly optimized blog posts.
        You write with authority, use data and examples, and create content that ranks well on Google.
        Your writing is clear, engaging, and provides real value to readers."""
        
        user_prompt = f"""Write a comprehensive, SEO-optimized blog post about '{topic}'.
        
        TARGET KEYWORDS TO INCLUDE NATURALLY: {target_keywords[:10]}
        CONTENT OPPORTUNITIES: {content_opportunities[:3]}
        TRENDING ANGLES: {ai_trends.get('trending_angles', [])[:3]}
        
        Create a detailed blog post with the following structure in JSON format:
        {{
            "title": "SEO-optimized title with main keyword",
            "meta_description": "155-character meta description",
            "introduction": "Engaging 200-word introduction with hook",
            "main_sections": [
                {{
                    "heading": "Section heading with keyword",
                    "content": "300-400 words of detailed content",
                    "key_points": ["point1", "point2"],
                    "examples": ["example1", "example2"]
                }}
            ],
            "conclusion": "150-word conclusion with CTA",
            "faq_section": [
                {{
                    "question": "Common question",
                    "answer": "Detailed answer"
                }}
            ],
            "internal_links_suggestions": ["topic1", "topic2"],
            "external_links_suggestions": ["authoritative source1", "source2"]
        }}
        
        Make it comprehensive, informative, and at least 2000 words total.
        Include statistics, examples, and actionable advice.
        """
        
        response = self.execute_prompt(system_prompt, user_prompt)
        draft_data = self.parse_json_response(response)
        
        # Calculate word count
        total_text = str(draft_data)
        result['word_count'] = len(total_text.split())
        result['draft'] = draft_data
        
        # Generate additional sections if needed
        if result['word_count'] < 1500:
            additional_prompt = f"""Expand on the topic '{topic}' with 3 more detailed sections.
            Focus on: practical tips, case studies, and common mistakes to avoid.
            Format as JSON with 'additional_sections' array."""
            
            additional_response = self.execute_prompt(system_prompt, additional_prompt)
            additional_data = self.parse_json_response(additional_response)
            result['additional_sections'] = additional_data.get('additional_sections', [])
        
        return result
