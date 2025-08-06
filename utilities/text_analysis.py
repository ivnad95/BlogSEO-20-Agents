"""
Text Analysis Utilities
=======================
This module provides functions for advanced text analysis, including keyword extraction
and topic modeling. These tools help in understanding the semantic content of text.
"""

from typing import List, Dict, Tuple, Any
import pandas as pd
from keybert import KeyBERT
from bertopic import BERTopic
import yake

# Initialize models once to be reused. This is a form of caching.
# For KeyBERT, we can use a standard, lightweight model.
kw_model = KeyBERT(model='all-MiniLM-L6-v2')

# BERTopic requires a bit more setup. We'll use a standard configuration.
# We can pass the same sentence transformer model for consistency.
topic_model = BERTopic(embedding_model='all-MiniLM-L6-v2', verbose=False)

# YAKE extractor doesn't need a heavy model, just configuration.
yake_extractor = yake.KeywordExtractor(n=1, dedupLim=0.9, features=None)


def extract_keywords_yake(text: str, max_keywords: int = 20) -> List[Tuple[str, float]]:
    """
    Extracts keywords from text using the YAKE (Yet Another Keyword Extractor) algorithm.
    YAKE is lightweight and works well without a transformer model.

    Args:
        text (str): The input text.
        max_keywords (int): The maximum number of keywords to return.

    Returns:
        List[Tuple[str, float]]: A list of (keyword, score) tuples. Lower scores are better.
    """
    keywords = yake_extractor.extract_keywords(text)
    return keywords[:max_keywords]


def extract_keywords_keybert(text: str, top_n: int = 10) -> List[Tuple[str, float]]:
    """
    Extracts keywords and keyphrases from text using KeyBERT, which leverages BERT embeddings.

    Args:
        text (str): The input text.
        top_n (int): The number of top keywords to extract.

    Returns:
        List[Tuple[str, float]]: A list of (keyword, similarity_score) tuples.
    """
    keywords = kw_model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 2),  # Consider single words and two-word phrases
        stop_words='english',
        top_n=top_n
    )
    return keywords


def model_topics_bertopic(
    documents: List[str],
    min_topic_size: int = 3,
    nr_topics: Any = "auto"
) -> Tuple[pd.DataFrame, Dict[Any, List[Tuple[str, float]]]]:
    """
    Performs topic modeling on a list of documents using BERTopic.

    Args:
        documents (List[str]): A list of text documents to model.
        min_topic_size (int): The minimum size of a topic.
        nr_topics (any): The number of topics to find. "auto" for automatic reduction.

    Returns:
        Tuple[pd.DataFrame, Dict[Any, List[Tuple[str, float]]]]:
        A tuple containing:
        - A DataFrame with topic information for each document.
        - A dictionary where keys are topic IDs and values are lists of (word, score) tuples.
    """
    # BERTopic can take some time, especially for many documents.
    topics, _ = topic_model.fit_transform(documents)

    # Get the topic info DataFrame
    topic_info = topic_model.get_topic_info()

    # Get the keywords for each topic
    topic_keywords = topic_model.get_topics()

    return topic_info, topic_keywords
