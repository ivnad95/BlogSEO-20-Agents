"""Lightweight text analysis utilities with graceful fallbacks.

The original project relies on heavy third-party libraries such as
BERTopic, KeyBERT and YAKE. Those libraries pull in large language models
and external services which are not available in the execution
environment used for the tests.  The helpers below provide minimal
implementations so that modules depending on them can be imported without
raising exceptions.  When the optional dependencies are installed the
full functionality is available, otherwise the functions simply return
empty results.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

# Optional dependencies -----------------------------------------------------
try:  # pragma: no cover - simple import wrapper
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover
    pd = None  # type: ignore

try:  # pragma: no cover
    from keybert import KeyBERT  # type: ignore
except Exception:  # pragma: no cover
    KeyBERT = None  # type: ignore

try:  # pragma: no cover
    from bertopic import BERTopic  # type: ignore
except Exception:  # pragma: no cover
    BERTopic = None  # type: ignore

try:  # pragma: no cover
    import yake  # type: ignore
except Exception:  # pragma: no cover
    yake = None  # type: ignore

# Lazy model initialisation -------------------------------------------------
kw_model = KeyBERT(model="all-MiniLM-L6-v2") if KeyBERT else None

topic_model = BERTopic(embedding_model="all-MiniLM-L6-v2", verbose=False) if BERTopic else None

yake_extractor = yake.KeywordExtractor(n=1, dedupLim=0.9, features=None) if yake else None


def extract_keywords_yake(text: str, max_keywords: int = 20) -> List[Tuple[str, float]]:
    """Return keywords using YAKE if available.

    When the YAKE dependency is missing an empty list is returned.  This
    is sufficient for tests which only require the function to exist.
    """

    if not yake_extractor:  # pragma: no cover - fallback branch
        return []
    keywords = yake_extractor.extract_keywords(text)
    return keywords[:max_keywords]


def extract_keywords_keybert(text: str, top_n: int = 10) -> List[Tuple[str, float]]:
    """Return keywords using KeyBERT if available.

    Without the KeyBERT library installed an empty list is returned.
    """

    if not kw_model:  # pragma: no cover - fallback branch
        return []
    keywords = kw_model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 2),
        stop_words="english",
        top_n=top_n,
    )
    return keywords


def model_topics_bertopic(
    documents: List[str],
    min_topic_size: int = 3,
    nr_topics: Any = "auto",
) -> Tuple[Any, Dict[Any, List[Tuple[str, float]]]]:
    """Run BERTopic if the library is available.

    A tuple of empty structures is returned when BERTopic or pandas are
    missing so that calls to the function remain safe in minimal
    environments.
    """

    if not topic_model or pd is None:  # pragma: no cover - fallback branch
        return (pd.DataFrame() if pd is not None else []), {}

    topics, _ = topic_model.fit_transform(documents)
    topic_info = topic_model.get_topic_info()
    topic_keywords = topic_model.get_topics()
    return topic_info, topic_keywords
