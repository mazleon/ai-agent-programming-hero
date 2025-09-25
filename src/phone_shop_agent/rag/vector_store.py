"""
Vector Store implementation for RAG pipeline using ChromaDB.
Handles document embedding, storage, and retrieval for phone shop policies.
"""

import os
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import hashlib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class PolicyVectorStore:
    """Vector store for phone shop policy documents using ChromaDB."""
    
    def __init__(self, persist_directory: str = "chroma_db", collection_name: str = "phone_shop_policies"):
        """
        Initialize the vector store.
        
        Args:
            persist_directory: Directory to persist ChromaDB data
            collection_name: Name of the ChromaDB collection
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Create persist directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
        
        logger.info(f"Initialized vector store with collection: {collection_name}")
    
    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks for better retrieval.
        
        Args:
            text: Text to chunk
            chunk_size: Maximum characters per chunk
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings within the last 100 characters
                sentence_end = text.rfind('.', start, end)
                if sentence_end > start + chunk_size - 100:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            
        return chunks
    
    def _generate_doc_id(self, content: str, source: str) -> str:
        """Generate unique document ID based on content and source."""
        content_hash = hashlib.md5(f"{source}:{content}".encode()).hexdigest()
        return f"{source}_{content_hash[:8]}"
    
    def add_document(self, content: str, source: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a document to the vector store.
        
        Args:
            content: Document content
            source: Source identifier (e.g., filename)
            metadata: Additional metadata for the document
        """
        try:
            # Chunk the document
            chunks = self._chunk_text(content)
            
            documents = []
            metadatas = []
            ids = []
            
            for i, chunk in enumerate(chunks):
                doc_id = self._generate_doc_id(chunk, f"{source}_chunk_{i}")
                
                # Prepare metadata
                chunk_metadata = {
                    "source": source,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "content_type": "policy_document"
                }
                
                if metadata:
                    chunk_metadata.update(metadata)
                
                documents.append(chunk)
                metadatas.append(chunk_metadata)
                ids.append(doc_id)
            
            # Add to collection
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added document '{source}' with {len(chunks)} chunks to vector store")
            
        except Exception as e:
            logger.error(f"Error adding document '{source}': {str(e)}")
            raise
    
    def search(self, query: str, n_results: int = 5, filter_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for relevant documents.
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of search results with documents, metadata, and distances
        """
        try:
            # Prepare query parameters
            query_params = {
                "query_texts": [query],
                "n_results": n_results,
                "include": ["documents", "metadatas", "distances"]
            }
            
            # Add metadata filter if provided
            if filter_metadata:
                query_params["where"] = filter_metadata
            
            # Perform search
            results = self.collection.query(**query_params)
            
            # Format results
            formatted_results = []
            for i in range(len(results["documents"][0])):
                result = {
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                    "relevance_score": 1 - results["distances"][0][i]  # Convert distance to relevance
                }
                formatted_results.append(result)
            
            logger.info(f"Found {len(formatted_results)} results for query: '{query[:50]}...'")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": self.collection_name,
                "persist_directory": self.persist_directory
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {}
    
    def delete_collection(self) -> None:
        """Delete the entire collection."""
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error deleting collection: {str(e)}")
            raise


def load_documents_from_directory(vector_store: PolicyVectorStore, directory_path: str) -> None:
    """
    Load all markdown documents from a directory into the vector store.
    
    Args:
        vector_store: PolicyVectorStore instance
        directory_path: Path to directory containing documents
    """
    directory = Path(directory_path)
    
    if not directory.exists():
        logger.error(f"Directory does not exist: {directory_path}")
        return
    
    # Find all markdown files
    md_files = list(directory.glob("*.md"))
    
    if not md_files:
        logger.warning(f"No markdown files found in: {directory_path}")
        return
    
    for md_file in md_files:
        try:
            # Read file content
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract metadata from filename and content
            metadata = {
                "filename": md_file.name,
                "file_path": str(md_file),
                "document_type": _infer_document_type(md_file.name)
            }
            
            # Add to vector store
            vector_store.add_document(
                content=content,
                source=md_file.stem,  # filename without extension
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error loading file {md_file}: {str(e)}")


def _infer_document_type(filename: str) -> str:
    """Infer document type from filename."""
    filename_lower = filename.lower()
    
    if "warranty" in filename_lower:
        return "warranty_policy"
    elif "replacement" in filename_lower:
        return "replacement_policy"
    elif "faq" in filename_lower:
        return "customer_support"
    else:
        return "general_policy"


# Example usage and testing
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize vector store
    vector_store = PolicyVectorStore()
    
    # Load documents from data directory
    data_dir = Path(__file__).parent.parent / "data"
    load_documents_from_directory(vector_store, str(data_dir))
    
    # Test search
    test_queries = [
        "What is the warranty period for new phones?",
        "How do I return a phone?",
        "What's covered under warranty?",
        "Can I get a replacement if my phone is defective?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        results = vector_store.search(query, n_results=3)
        
        for i, result in enumerate(results, 1):
            print(f"  {i}. Source: {result['metadata']['source']}")
            print(f"     Relevance: {result['relevance_score']:.3f}")
            print(f"     Content: {result['document'][:100]}...")
    
    # Print collection stats
    stats = vector_store.get_collection_stats()
    print(f"\nCollection Stats: {stats}")
