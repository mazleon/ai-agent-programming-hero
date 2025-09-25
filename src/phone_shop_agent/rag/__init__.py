"""
RAG (Retrieval-Augmented Generation) module for phone shop agent.
Provides vector storage and retrieval capabilities for policy documents.
"""

from .vector_store import PolicyVectorStore, load_documents_from_directory
from .retriever import (
    PolicyRetrievalTool,
    search_warranty_info,
    search_replacement_info,
    search_customer_support_info,
    search_general_policy_info
)

__all__ = [
    "PolicyVectorStore",
    "load_documents_from_directory",
    "PolicyRetrievalTool",
    "search_warranty_info",
    "search_replacement_info",
    "search_customer_support_info",
    "search_general_policy_info"
]
