#!/usr/bin/env python3
"""
Test script for RAG system functionality.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test if we can import the RAG modules."""
    print("Testing imports...")
    try:
        from phone_shop_agent.rag.vector_store import PolicyVectorStore
        print("✅ PolicyVectorStore imported successfully")
        
        from phone_shop_agent.rag.retriever import search_customer_support_info
        print("✅ search_customer_support_info imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_vector_store():
    """Test vector store initialization and document loading."""
    print("\nTesting vector store...")
    try:
        from phone_shop_agent.rag.vector_store import PolicyVectorStore, load_documents_from_directory
        
        # Initialize vector store
        vector_store = PolicyVectorStore(
            persist_directory="test_chroma_db",
            collection_name="test_policies"
        )
        print("✅ Vector store initialized")
        
        # Load documents
        data_dir = Path("src/phone_shop_agent/data")
        if data_dir.exists():
            load_documents_from_directory(vector_store, str(data_dir))
            print("✅ Documents loaded")
            
            # Get stats
            stats = vector_store.get_collection_stats()
            print(f"📊 Total documents: {stats.get('total_documents', 0)}")
            
            # Test search
            results = vector_store.search("store hours", n_results=3)
            print(f"🔍 Search test: Found {len(results)} results for 'store hours'")
            
            if results:
                print(f"   First result: {results[0]['document'][:100]}...")
                print(f"   Source: {results[0]['metadata']['source']}")
                print(f"   Document type: {results[0]['metadata'].get('document_type', 'unknown')}")
            
            return True
        else:
            print(f"❌ Data directory not found: {data_dir}")
            return False
            
    except Exception as e:
        print(f"❌ Vector store test failed: {e}")
        return False

def test_retriever_functions():
    """Test the retriever functions."""
    print("\nTesting retriever functions...")
    try:
        from phone_shop_agent.rag.retriever import search_customer_support_info
        
        # Test customer support search
        result = search_customer_support_info("store hours", max_results=2)
        print(f"🔍 Customer support search result:")
        print(f"   Found: {result.get('found', False)}")
        print(f"   Results count: {len(result.get('support_info', []))}")
        
        if result.get('found', False):
            for i, info in enumerate(result['support_info'][:1]):
                print(f"   Result {i+1}: {info[:100]}...")
        
        return result.get('found', False)
        
    except Exception as e:
        print(f"❌ Retriever function test failed: {e}")
        return False

def test_tool_integration():
    """Test the tool integration."""
    print("\nTesting tool integration...")
    try:
        from phone_shop_agent.tools.tool import get_customer_support_information
        
        result = get_customer_support_information("What are your store hours?")
        print(f"🛠️  Tool result:")
        print(f"   Length: {len(result)} characters")
        print(f"   Preview: {result[:200]}...")
        
        # Check if it's not an error message
        success = "I couldn't find" not in result and "Error" not in result
        print(f"   Success: {success}")
        
        return success
        
    except Exception as e:
        print(f"❌ Tool integration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 RAG System Test Suite")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("Vector Store Test", test_vector_store),
        ("Retriever Functions Test", test_retriever_functions),
        ("Tool Integration Test", test_tool_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔬 Running {test_name}...")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("📋 Test Results Summary:")
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} - {test_name}")
        if success:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! RAG system is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
