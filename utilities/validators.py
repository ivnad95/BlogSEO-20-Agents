from typing import Dict, List
import languagetool_python
from simhash import Simhash


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


# Caching the tool to avoid re-initializing it on every call
_grammar_tool = None

def get_grammar_tool():
    """Initializes and returns a LanguageTool instance."""
    global _grammar_tool
    if _grammar_tool is None:
        # This might need to download the language model on first run
        _grammar_tool = languagetool_python.LanguageTool('en-US')
    return _grammar_tool

def check_grammar(text: str) -> List[Dict]:
    """
    Checks the grammar of a given text using LanguageTool.

    Args:
        text (str): The text to check.

    Returns:
        List[Dict]: A list of dictionaries, each representing a grammar mistake.
    """
    tool = get_grammar_tool()
    matches = tool.check(text)

    # Convert Match objects to dictionaries for easier serialization/use
    mistakes = [
        {
            "ruleId": match.ruleId,
            "message": match.message,
            "replacements": match.replacements,
            "offset": match.offset,
            "length": match.errorLength,
            "context": match.context,
        }
        for match in matches
    ]
    return mistakes

def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculates the similarity between two texts using Simhash.

    Args:
        text1 (str): The first text.
        text2 (str): The second text.

    Returns:
        float: A similarity score between 0.0 (completely different) and
               1.0 (identical).
    """
    hash1 = Simhash(text1)
    hash2 = Simhash(text2)

    # Simhash distance is the number of bits that are different.
    # The hash is 64 bits long.
    distance = hash1.distance(hash2)

    # Normalize the distance to a similarity score
    similarity = (64 - distance) / 64
    return similarity
