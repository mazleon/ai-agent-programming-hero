"""
RAG Retriever implementation for Google ADK integration.
Provides retrieval tools compatible with ADK's tool system.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from google.adk.tools.retrieval import BaseRetrievalTool
from .vector_store import PolicyVectorStore, load_documents_from_directory

logger = logging.getLogger(__name__)

_DOCUMENT_TYPE_TO_FILENAME = {
    "warranty_policy": "warranty_policy.md",
    "replacement_policy": "replacement_policy.md",
    "customer_support": "customer_support_faq.md",
}


def _fallback_text_search(query: str, document_types: Optional[List[str]] = None, max_results: int = 3) -> List[Dict[str, Any]]:
    """Basic keyword search directly against markdown documents as a safety net."""
    if document_types is None:
        document_types = list(_DOCUMENT_TYPE_TO_FILENAME.keys())

    data_dir = Path(__file__).parent.parent / "data"
    tokens = [token.lower() for token in query.split() if token]

    if not tokens:
        return []

    fallback_results: List[Dict[str, Any]] = []

    for document_type in document_types:
        filename = _DOCUMENT_TYPE_TO_FILENAME.get(document_type)
        if not filename:
            continue

        file_path = data_dir / filename
        if not file_path.exists():
            logger.warning("Fallback search skipped missing document: %s", file_path)
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
        except OSError as exc:
            logger.error("Failed to read policy document %s: %s", file_path, exc)
            continue

        lines = content.splitlines()
        snippets: List[str] = []

        for index, line in enumerate(lines):
            lowered = line.lower()
            if any(token in lowered for token in tokens):
                start = max(0, index - 2)
                end = min(len(lines), index + 3)
                snippet = "\n".join(lines[start:end]).strip()
                if snippet and snippet not in snippets:
                    snippets.append(snippet)

        for snippet in snippets[:max_results]:
            fallback_results.append(
                {
                    "content": snippet,
                    "metadata": {
                        "source": filename.replace(".md", ""),
                        "document_type": document_type,
                        "fallback": True,
                    },
                    "document_type": document_type,
                    "relevance_score": 0.4,  # nominal score for fallback
                }
            )

    return fallback_results[:max_results]


class PolicyRetrievalTool(BaseRetrievalTool):
    """
    ADK-compatible retrieval tool for phone shop policies.
    Integrates ChromaDB vector store with Google ADK framework.
    """
    
    def __init__(
        self,
        name: str = "policy_retrieval",
        description: str = "Retrieves relevant information from phone shop policies including warranty, replacement, and customer support documents",
        data_directory: Optional[str] = None,
        persist_directory: str = "chroma_db",
        collection_name: str = "phone_shop_policies",
        **kwargs
    ):
        """
        Initialize the policy retrieval tool.
        
        Args:
            name: Tool name
            description: Tool description
            data_directory: Directory containing policy documents
            persist_directory: ChromaDB persistence directory
            collection_name: ChromaDB collection name
        """
        super().__init__(name=name, description=description, **kwargs)
        
        self.data_directory = data_directory
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Initialize vector store
        self._initialize_vector_store()
    
    def _initialize_vector_store(self) -> None:
        """Initialize and populate the vector store."""
        try:
            # Create vector store
            self.vector_store = PolicyVectorStore(
                persist_directory=self.persist_directory,
                collection_name=self.collection_name
            )
            
            # Check if we need to load documents
            stats = self.vector_store.get_collection_stats()
            total_docs = stats.get("total_documents", 0)

            if total_docs == 0:
                logger.info("Vector store is empty, attempting to load policy documents...")
                self._load_documents()

                # Recompute stats after loading
                stats = self.vector_store.get_collection_stats()
                total_docs = stats.get("total_documents", 0)

            logger.info(
                "Vector store initialization complete. Documents available: %s",
                total_docs,
            )
                
        except Exception as e:
            logger.error(f"Error initializing vector store: {str(e)}")
            raise
    
    def _load_documents(self) -> None:
        """Load documents from data directory into vector store."""
        if not self.data_directory:
            # Try to find data directory relative to this file
            current_dir = Path(__file__).parent
            potential_data_dir = current_dir.parent / "data"
            
            if potential_data_dir.exists():
                self.data_directory = str(potential_data_dir)
            else:
                logger.warning("No data directory specified and default not found")
                return
        
        try:
            load_documents_from_directory(self.vector_store, self.data_directory)
            logger.info(f"Successfully loaded documents from {self.data_directory}")
        except Exception as e:
            logger.error(f"Error loading documents: {str(e)}")
            raise
    
    async def run_async(self, *, args: Dict[str, Any], tool_context) -> Dict[str, Any]:
        """
        Execute the retrieval tool asynchronously.
        
        Args:
            args: Tool arguments containing the query
            tool_context: ADK tool context
            
        Returns:
            Dictionary containing retrieved information
        """
        try:
            # Extract query from arguments
            query = args.get("query", "")
            if not query:
                return {
                    "error": "No query provided",
                    "results": []
                }
            
            # Optional parameters
            max_results = args.get("max_results", 5)
            document_type = args.get("document_type")  # Filter by document type
            
            # Prepare metadata filter
            metadata_filter = None
            if document_type:
                metadata_filter = {"document_type": document_type}
            
            # Perform search
            search_results = self.vector_store.search(
                query=query,
                n_results=max_results,
                filter_metadata=metadata_filter
            )
            
            # Format results for ADK
            formatted_results = []
            for result in search_results:
                formatted_result = {
                    "content": result["document"],
                    "source": result["metadata"].get("source", "unknown"),
                    "document_type": result["metadata"].get("document_type", "general"),
                    "relevance_score": result["relevance_score"],
                    "metadata": result["metadata"]
                }
                formatted_results.append(formatted_result)
            
            # Create response
            response = {
                "query": query,
                "results": formatted_results,
                "total_results": len(formatted_results),
                "status": "success"
            }
            
            logger.info(f"Retrieved {len(formatted_results)} results for query: '{query[:50]}...'")
            return response
            
        except Exception as e:
            logger.error(f"Error in policy retrieval: {str(e)}")
            return {
                "error": str(e),
                "query": args.get("query", ""),
                "results": [],
                "status": "error"
            }


def search_warranty_info(query: str, max_results: int = 3) -> Dict[str, Any]:
    """
    Standalone function to search warranty information.
    Can be used as a regular ADK tool function.
    
    Args:
        query: Search query about warranty
        max_results: Maximum number of results to return
        
    Returns:
        Dictionary with warranty information
    """
    try:
        # Initialize retriever if not already done
        if not hasattr(search_warranty_info, '_retriever'):
            try:
                search_warranty_info._retriever = PolicyRetrievalTool()
                logger.info("PolicyRetrievalTool initialized successfully")
            except Exception as init_error:
                logger.error(f"Failed to initialize PolicyRetrievalTool: {str(init_error)}")
                return {
                    "warranty_info": [f"RAG system initialization failed: {str(init_error)}"],
                    "sources": [],
                    "found": False
                }
        
        # Search with warranty filter
        results = search_warranty_info._retriever.vector_store.search(
            query=query,
            n_results=max_results,
            filter_metadata={"document_type": "warranty_policy"}
        )
        
        # Format for simple function return
        if not results:
            logger.warning(f"No warranty results found for query: {query}. Falling back to keyword search.")
            results = _fallback_text_search(query, ["warranty_policy"], max_results)

        if results:
            return {
                "warranty_info": [r["document"] if "document" in r else r["content"] for r in results],
                "sources": [r.get("metadata", {}).get("source", "warranty_policy") for r in results],
                "found": True
            }

        return {
            "warranty_info": ["No warranty information found for your query."],
            "sources": [],
            "found": False
        }
            
    except Exception as e:
        logger.error(f"Error searching warranty info: {str(e)}")
        return {
            "warranty_info": [f"Error retrieving warranty information: {str(e)}"],
            "sources": [],
            "found": False
        }


def search_replacement_info(query: str, max_results: int = 3) -> Dict[str, Any]:
    """
    Standalone function to search replacement policy information.
    Can be used as a regular ADK tool function.
    
    Args:
        query: Search query about replacement policy
        max_results: Maximum number of results to return
        
    Returns:
        Dictionary with replacement policy information
    """
    try:
        # Initialize retriever if not already done
        if not hasattr(search_replacement_info, '_retriever'):
            search_replacement_info._retriever = PolicyRetrievalTool()
        
        # Search with replacement filter
        results = search_replacement_info._retriever.vector_store.search(
            query=query,
            n_results=max_results,
            filter_metadata={"document_type": "replacement_policy"}
        )
        
        # Format for simple function return
        if not results:
            logger.warning(f"No replacement results found for query: {query}. Falling back to keyword search.")
            results = _fallback_text_search(query, ["replacement_policy"], max_results)

        if results:
            return {
                "replacement_info": [r.get("document") or r.get("content") for r in results],
                "sources": [r.get("metadata", {}).get("source", "replacement_policy") for r in results],
                "found": True
            }

        return {
            "replacement_info": ["No replacement policy information found for your query."],
            "sources": [],
            "found": False
        }
            
    except Exception as e:
        logger.error(f"Error searching replacement info: {str(e)}")
        return {
            "replacement_info": [f"Error retrieving replacement information: {str(e)}"],
            "sources": [],
            "found": False
        }


def search_customer_support_info(query: str, max_results: int = 3) -> Dict[str, Any]:
    """
    Standalone function to search customer support information.
    Can be used as a regular ADK tool function.
    
    Args:
        query: Search query about customer support
        max_results: Maximum number of results to return
        
    Returns:
        Dictionary with customer support information
    """
    try:
        # Initialize retriever if not already done
        if not hasattr(search_customer_support_info, '_retriever'):
            try:
                search_customer_support_info._retriever = PolicyRetrievalTool()
                logger.info("PolicyRetrievalTool initialized successfully for customer support")
            except Exception as init_error:
                logger.error(f"Failed to initialize PolicyRetrievalTool: {str(init_error)}")
                return {
                    "support_info": [f"RAG system initialization failed: {str(init_error)}"],
                    "sources": [],
                    "found": False
                }
        
        # Search with customer support filter
        results = search_customer_support_info._retriever.vector_store.search(
            query=query,
            n_results=max_results,
            filter_metadata={"document_type": "customer_support"}
        )
        
        # If no results with filter, try without filter
        if not results:
            logger.info(f"No vector results found for customer support query: {query}. Trying fallback search.")
            results = _fallback_text_search(query, ["customer_support"], max_results)
        
        if results:
            return {
                "support_info": [r.get("document") or r.get("content") for r in results],
                "sources": [r.get("metadata", {}).get("source", "customer_support_faq") for r in results],
                "found": True
            }

        return {
            "support_info": ["No customer support information found for your query."],
            "sources": [],
            "found": False
        }
            
    except Exception as e:
        logger.error(f"Error searching customer support info: {str(e)}")
        return {
            "support_info": [f"Error retrieving customer support information: {str(e)}"],
            "sources": [],
            "found": False
        }


def search_general_policy_info(query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    General function to search all policy information.
    Can be used as a regular ADK tool function.
    
    Args:
        query: Search query
        max_results: Maximum number of results to return
        
    Returns:
        Dictionary with policy information from all sources
    """
    try:
        # Initialize retriever if not already done
        if not hasattr(search_general_policy_info, '_retriever'):
            search_general_policy_info._retriever = PolicyRetrievalTool()
        
        # Search without filters (all documents)
        results = search_general_policy_info._retriever.vector_store.search(
            query=query,
            n_results=max_results
        )
        
        if not results:
            logger.info(f"No vector results for general policy query: {query}. Using fallback search.")
            results = _fallback_text_search(query, max_results=max_results)

        if results:
            formatted_results = []
            for r in results:
                formatted_results.append({
                    "content": r.get("document") or r.get("content"),
                    "source": r.get("metadata", {}).get("source", "policy_document"),
                    "type": r.get("metadata", {}).get("document_type", "general"),
                    "relevance": round(r.get("relevance_score", 0.4), 3)
                })
            
            return {
                "policy_info": formatted_results,
                "total_found": len(formatted_results),
                "found": True
            }

        return {
            "policy_info": [],
            "total_found": 0,
            "found": False,
            "message": "No relevant policy information found for your query."
        }
            
    except Exception as e:
        logger.error(f"Error searching general policy info: {str(e)}")
        return {
            "policy_info": [],
            "total_found": 0,
            "found": False,
            "error": f"Error retrieving policy information: {str(e)}"
        }


# Example usage and testing
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Test the retrieval functions
    test_queries = [
        ("warranty period", search_warranty_info),
        ("return policy", search_replacement_info),
        ("contact support", search_customer_support_info),
        ("phone protection", search_general_policy_info)
    ]
    
    for query, func in test_queries:
        print(f"\nTesting {func.__name__} with query: '{query}'")
        result = func(query)
        print(f"Found: {result.get('found', False)}")
        
        if 'warranty_info' in result:
            for info in result['warranty_info'][:1]:  # Show first result
                print(f"Info: {info[:100]}...")
        elif 'replacement_info' in result:
            for info in result['replacement_info'][:1]:
                print(f"Info: {info[:100]}...")
        elif 'support_info' in result:
            for info in result['support_info'][:1]:
                print(f"Info: {info[:100]}...")
        elif 'policy_info' in result:
            for info in result['policy_info'][:1]:
                print(f"Info: {info['content'][:100]}...")
