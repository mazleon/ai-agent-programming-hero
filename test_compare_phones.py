#!/usr/bin/env python3
"""
Test script to debug the compare_phones function issue.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_compare_phones():
    """Test the compare_phones function directly."""
    print("🧪 Testing compare_phones function...")
    
    try:
        from phone_shop_agent.tools.mcp_tools import compare_phones
        print(f"✅ Function imported successfully: {compare_phones}")
        print(f"   Function type: {type(compare_phones)}")
        print(f"   Function callable: {callable(compare_phones)}")
        print(f"   Function name: {compare_phones.__name__}")
        print(f"   Function module: {compare_phones.__module__}")
        
        # Test calling the function
        print("\n📱 Testing function call...")
        result = compare_phones("iPhone 15", "Samsung Galaxy S23")
        print("✅ Function called successfully")
        print(f"   Result preview: {result[:200]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_sync_function():
    """Test the underlying sync function."""
    print("\n🔧 Testing underlying sync function...")
    
    try:
        from phone_shop_agent.mcp.fastmcp_client import compare_phones_sync
        print(f"✅ Sync function imported: {compare_phones_sync}")
        print(f"   Function type: {type(compare_phones_sync)}")
        print(f"   Function callable: {callable(compare_phones_sync)}")
        
        # Test calling the sync function directly
        print("\n📱 Testing sync function call...")
        result = compare_phones_sync("iPhone 15", "Samsung Galaxy S23")
        print("✅ Sync function called successfully")
        print(f"   Result preview: {result[:100]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_agent_tools():
    """Test the agent and its tools."""
    print("\n🤖 Testing agent tools...")
    
    try:
        from phone_shop_agent import root_agent
        print(f"✅ Agent imported successfully: {root_agent}")
        print(f"   Agent tools count: {len(root_agent.tools)}")
        
        # Find the compare_phones tool
        compare_tool = None
        for tool in root_agent.tools:
            if hasattr(tool, '__name__') and tool.__name__ == 'compare_phones':
                compare_tool = tool
                break
            elif hasattr(tool, 'name') and tool.name == 'compare_phones':
                compare_tool = tool
                break
        
        if compare_tool:
            print(f"✅ Found compare_phones tool: {compare_tool}")
            print(f"   Tool type: {type(compare_tool)}")
            print(f"   Tool callable: {callable(compare_tool)}")
            
            # Try to call it if it's a function
            if callable(compare_tool) and hasattr(compare_tool, '__name__'):
                print("\n📱 Testing tool call...")
                result = compare_tool("iPhone 15", "Samsung Galaxy S23")
                print("✅ Tool called successfully")
                print(f"   Result preview: {result[:200]}...")
        else:
            print("❌ compare_phones tool not found in agent tools")
            print("   Available tools:")
            for i, tool in enumerate(root_agent.tools):
                tool_name = getattr(tool, '__name__', getattr(tool, 'name', f'tool_{i}'))
                print(f"     {i+1}. {tool_name} ({type(tool)})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_compare_phones()
    test_sync_function()
    test_agent_tools()
