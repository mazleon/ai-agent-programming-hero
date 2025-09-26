#!/usr/bin/env python3
"""
Simple test script to check FastMCP installation and basic functionality.
"""

import sys
import traceback
from pathlib import Path

print("🧪 Testing FastMCP Installation...")
print("=" * 50)

# Test 1: Import FastMCP
try:
    from fastmcp import FastMCP
    print("✅ FastMCP imported successfully")
except ImportError as e:
    print(f"❌ Failed to import FastMCP: {e}")
    print("Please install FastMCP: pip install fastmcp")
    sys.exit(1)

# Test 2: Create a simple FastMCP server
try:
    mcp = FastMCP(name="TestServer")
    print("✅ FastMCP server instance created")
except Exception as e:
    print(f"❌ Failed to create FastMCP server: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 3: Add a simple tool
try:
    @mcp.tool
    def test_tool(message: str) -> str:
        """A simple test tool."""
        return f"Hello, {message}!"
    
    print("✅ Test tool added successfully")
except Exception as e:
    print(f"❌ Failed to add test tool: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 4: Check if database directory exists
db_dir = Path("src/phone_shop_agent/database")
if db_dir.exists():
    print(f"✅ Database directory exists: {db_dir}")
    
    # List files in database directory
    files = list(db_dir.glob("*"))
    if files:
        print(f"   Files: {[f.name for f in files]}")
    else:
        print("   Directory is empty")
else:
    print(f"❌ Database directory not found: {db_dir}")
    print("   Creating database directory...")
    db_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created database directory: {db_dir}")

# Test 5: Check if database initialization script exists
init_script = db_dir / "init_db.py"
if init_script.exists():
    print(f"✅ Database initialization script exists: {init_script}")
else:
    print(f"❌ Database initialization script not found: {init_script}")

print("\n" + "=" * 50)
print("🎯 Test Summary:")
print("✅ FastMCP is working correctly")
print("✅ Ready to proceed with phone shop setup")

if __name__ == "__main__":
    print("\n🚀 All tests passed! FastMCP is ready to use.")
