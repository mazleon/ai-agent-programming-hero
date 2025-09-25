#!/usr/bin/env python3
"""
Setup script for RAG (Retrieval-Augmented Generation) system.
Initializes the vector database and loads policy documents.
"""

import os
import sys
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from phone_shop_agent.rag import PolicyVectorStore, load_documents_from_directory
except ImportError as e:
    print(f"Error importing RAG modules: {e}")
    print("Make sure you've installed the required dependencies:")
    print("pip install -r requirements.txt")
    sys.exit(1)

def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """Main setup function."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("🚀 Setting up RAG system for Phone Shop Agent...")
    print("=" * 50)
    
    try:
        # Initialize vector store
        print("📊 Initializing ChromaDB vector store...")
        vector_store = PolicyVectorStore(
            persist_directory="chroma_db",
            collection_name="phone_shop_policies"
        )
        
        # Check if documents are already loaded
        stats = vector_store.get_collection_stats()
        current_docs = stats.get("total_documents", 0)
        
        if current_docs > 0:
            print(f"✅ Vector store already contains {current_docs} documents")
            response = input("Do you want to reload documents? (y/N): ").lower().strip()
            
            if response == 'y':
                print("🗑️  Deleting existing collection...")
                vector_store.delete_collection()
                vector_store = PolicyVectorStore(
                    persist_directory="chroma_db",
                    collection_name="phone_shop_policies"
                )
            else:
                print("✅ Using existing vector store")
                return
        
        # Load documents
        data_dir = Path("src/phone_shop_agent/data")
        if not data_dir.exists():
            print(f"❌ Data directory not found: {data_dir}")
            print("Make sure you're running this script from the project root directory")
            return
        
        print(f"📚 Loading documents from {data_dir}...")
        load_documents_from_directory(vector_store, str(data_dir))
        
        # Verify setup
        final_stats = vector_store.get_collection_stats()
        total_docs = final_stats.get("total_documents", 0)
        
        print("\n" + "=" * 50)
        print("✅ RAG Setup Complete!")
        print(f"📊 Total documents indexed: {total_docs}")
        print(f"💾 Vector store location: {final_stats.get('persist_directory', 'chroma_db')}")
        print(f"🏷️  Collection name: {final_stats.get('collection_name', 'phone_shop_policies')}")
        
        # Test search
        print("\n🔍 Testing search functionality...")
        test_queries = [
            "warranty period",
            "return policy", 
            "customer support"
        ]
        
        for query in test_queries:
            results = vector_store.search(query, n_results=1)
            if results:
                print(f"  ✅ '{query}' -> Found {len(results)} result(s)")
            else:
                print(f"  ❌ '{query}' -> No results found")
        
        print("\n🎉 RAG system is ready!")
        print("You can now run the phone shop agent with:")
        print("  cd src")
        print("  adk run phone_shop_agent")
        
    except Exception as e:
        logger.error(f"Setup failed: {str(e)}")
        print(f"\n❌ Setup failed: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("2. Check that you're in the project root directory")
        print("3. Verify that policy documents exist in src/phone_shop_agent/data/")
        sys.exit(1)

if __name__ == "__main__":
    main()
