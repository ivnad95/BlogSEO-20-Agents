"""Validation helpers with optional third‑party dependencies.

The original implementation required external packages such as
`languagetool_python` and `simhash`.  These libraries are not available in
the execution environment used for the tests which caused import errors
when the validator utilities were imported.  The simplified version below
provides the same public functions but degrades gracefully when those
optional dependencies are missing.
"""

from __future__ import annotations

from typing import Dict, List

# Optional imports ---------------------------------------------------------
try:  # pragma: no cover - dependency may not be installed
    import languagetool_python  # type: ignore
except Exception:  # pragma: no cover
    languagetool_python = None  # type: ignore

try:  # pragma: no cover
    from simhash import Simhash  # type: ignore
except Exception:  # pragma: no cover
    Simhash = None  # type: ignore


# Agent output validation ---------------------------------------------------
def validate_agent_output(agent_name: str, output: Dict) -> bool:
    """Validate that an agent's output dictionary contains expected keys."""

    required_fields = {
        "DraftWriterAgent": ["draft", "word_count"],
        "KeywordMiningAgent": ["primary_keywords", "long_tail_keywords"],
        "OnPageSEOAgent": ["title_tag", "meta_description"],
        "FinalAssemblyAgent": ["title", "content"],
    }

    if agent_name in required_fields:
        for field in required_fields[agent_name]:
            if field not in output:
                return False
    return True


# Grammar checking ---------------------------------------------------------
_grammar_tool = None

def get_grammar_tool():
    """Return a LanguageTool instance when available."""

    global _grammar_tool
    if languagetool_python is None:  # pragma: no cover - fallback branch
        return None
    if _grammar_tool is None:
        _grammar_tool = languagetool_python.LanguageTool("en-US")
    return _grammar_tool


def check_grammar(text: str) -> List[Dict]:
    """Check grammar of *text* using LanguageTool when possible."""

    tool = get_grammar_tool()
    if tool is None:  # pragma: no cover - fallback branch
        return []
    matches = tool.check(text)
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


# Similarity ----------------------------------------------------------------
def calculate_similarity(text1: str, text2: str) -> float:
    """Return a similarity score between two texts using Simhash.

    If the `simhash` package is not installed a neutral score of ``0.0`` is
    returned instead of raising an exception.
    """

    if Simhash is None:  # pragma: no cover - fallback branch
        return 0.0
    hash1 = Simhash(text1)
    hash2 = Simhash(text2)
    distance = hash1.distance(hash2)
    return (64 - distance) / 64
