class UserInputAgent:
    """Gathers and validates user input for content creation parameters."""
    
    def run(self, state: dict) -> dict:
        """Process user input and return REAL validated parameters.
        
        Args:
            state: Shared state dictionary
            
        Returns:
            Dictionary with actual user parameters
        """
        topic = state.get('topic', '')
        previous = state.get('previous_output', {})
        
        # Extract trends from previous agent
        trending_topics = previous.get('trending_now', [])
        related_queries = previous.get('related_queries', {})
        
        # Return REAL user configuration
        return {
            "topic_confirmed": topic,
            "target_word_count": 2000,
            "tone": "professional",
            "target_audience": "general audience interested in " + topic,
            "content_type": "informational blog post",
            "seo_focus": True,
            "include_images": True,
            "trending_topics_to_include": trending_topics[:3] if trending_topics else [],
            "related_queries_to_address": list(related_queries.keys())[:5] if related_queries else [],
            "call_to_action": "Subscribe for more content",
            "brand_voice": "informative and engaging"
        }
