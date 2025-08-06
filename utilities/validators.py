def validate_agent_output(agent_name: str, output: Dict) -> bool:
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
