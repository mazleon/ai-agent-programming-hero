#!/usr/bin/env python3
"""
FastMCP Client for Phone Shop Agent.
Connects to the FastMCP server to provide database-backed phone information tools.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastmcp import Client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("phone-shop-fastmcp-client")

class PhoneShopFastMCPClient:
    """FastMCP Client for connecting to phone shop database server."""
    
    def __init__(self, server_script_path: str = None):
        if server_script_path is None:
            # Use absolute path to the server script
            server_script_path = Path(__file__).parent / "fastmcp_server.py"
            server_script_path = server_script_path.resolve()
        self.server_script_path = str(server_script_path)
        self.client: Optional[Client] = None
        self._connected = False
    
    async def ensure_connected(self) -> bool:
        """Ensure client is connected, connect if not."""
        if not self._connected or not self.client:
            try:
                self.client = Client(self.server_script_path)
                # Test connection with a simple ping
                async with self.client:
                    await self.client.ping()
                self._connected = True
                logger.info("✅ Connected to FastMCP server successfully")
                return True
            except Exception as e:
                logger.error(f"❌ Failed to connect to FastMCP server: {e}")
                logger.error(f"   Server script path: {self.server_script_path}")
                self._connected = False
                self.client = None
                return False
        return True
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the FastMCP server."""
        if not await self.ensure_connected():
            return {"error": "Failed to connect to FastMCP server"}
        
        try:
            async with self.client:
                result = await self.client.call_tool(tool_name, arguments)
                
                # FastMCP returns result with content array
                if result and hasattr(result, 'content') and result.content:
                    content = result.content[0]
                    if hasattr(content, 'text'):
                        try:
                            # Try to parse as JSON first
                            return json.loads(content.text)
                        except json.JSONDecodeError:
                            # If not JSON, return as text
                            return {"result": content.text}
                    else:
                        return {"result": str(content)}
                
                return {"error": "No content returned from tool"}
                
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            self._connected = False  # Reset connection on error
            self.client = None
            
            # Try once more with a fresh connection
            try:
                if await self.ensure_connected():
                    async with self.client:
                        result = await self.client.call_tool(tool_name, arguments)
                        
                        if result and hasattr(result, 'content') and result.content:
                            content = result.content[0]
                            if hasattr(content, 'text'):
                                try:
                                    return json.loads(content.text)
                                except json.JSONDecodeError:
                                    return {"result": content.text}
                            else:
                                return {"result": str(content)}
                        
                        return {"error": "No content returned from tool"}
            except Exception as retry_e:
                logger.error(f"Retry also failed for tool {tool_name}: {retry_e}")
            
            return {"error": str(e)}
    
    async def list_tools(self) -> List[str]:
        """Get list of available tool names."""
        if not await self.ensure_connected():
            return []
        
        try:
            async with self.client:
                tools = await self.client.list_tools()
                return [tool.name for tool in tools]
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            self._connected = False
            return []

# Global client instance
_fastmcp_client: Optional[PhoneShopFastMCPClient] = None

async def get_fastmcp_client() -> PhoneShopFastMCPClient:
    """Get or create the global FastMCP client instance."""
    global _fastmcp_client
    
    if _fastmcp_client is None:
        _fastmcp_client = PhoneShopFastMCPClient()
    
    return _fastmcp_client

# Tool wrapper functions for ADK integration
async def search_phones_fastmcp(query: str = "", min_price: float = None, 
                               max_price: float = None, year: int = None) -> str:
    """Search phones using FastMCP server."""
    client = await get_fastmcp_client()
    
    arguments = {"query": query}
    if min_price is not None:
        arguments["min_price"] = min_price
    if max_price is not None:
        arguments["max_price"] = max_price
    if year is not None:
        arguments["year"] = year
    
    result = await client.call_tool("search_phones", arguments)
    
    if "error" in result:
        return f"Error searching phones: {result['error']}"
    
    # Format the results for display
    if "results" in result and result["results"]:
        phones = result["results"]
        response = f"Found {len(phones)} phone(s):\n\n"
        
        for phone in phones:
            response += f"📱 **{phone['model_name']}** ({phone['year']})\n"
            response += f"   💰 Price: ${phone['price']}\n"
            response += f"   🔧 Chipset: {phone['chipset_name']}\n"
            response += f"   💾 RAM: {phone['ram_size']} | Storage: {phone['storage_size']}\n"
            response += f"   📺 Display: {phone['display_size']}\n"
            response += f"   🔋 Battery: {phone['battery_capacity']}\n\n"
        
        return response.strip()
    else:
        return "No phones found matching your criteria."

async def get_phone_details_fastmcp(phone_name: str) -> str:
    """Get detailed phone information using FastMCP server."""
    client = await get_fastmcp_client()
    
    result = await client.call_tool("get_phone_details", {"phone_name": phone_name})
    
    if "error" in result:
        return f"Error getting phone details: {result['error']}"
    
    phone = result
    if not phone or "error" in phone:
        return f"Phone '{phone_name}' not found."
    
    # Format detailed response
    response = f"📱 **{phone['model_name']}** ({phone['year']})\n\n"
    response += f"💰 **Price:** ${phone['price']}\n"
    response += f"🔧 **Chipset:** {phone['chipset_name']}\n"
    response += f"💾 **RAM:** {phone['ram_size']}\n"
    response += f"💽 **Storage:** {phone['storage_size']}\n"
    response += f"📺 **Display:** {phone['display_size']}\n"
    response += f"🔋 **Battery:** {phone['battery_capacity']}\n"
    response += f"📱 **OS:** {phone['operating_system']}\n"
    
    if phone.get('camera_features'):
        response += f"📸 **Camera:** {', '.join(phone['camera_features'])}\n"
    
    if phone.get('charging_features'):
        response += f"⚡ **Charging:** {', '.join(phone['charging_features'])}\n"
    
    # Stock information
    if phone.get('stock_quantity') is not None:
        stock = phone['stock_quantity']
        if stock > 0:
            response += f"📦 **Stock:** {stock} units available\n"
        else:
            response += f"📦 **Stock:** Out of stock\n"
    
    # Active offers
    if phone.get('active_offers'):
        response += f"\n🎁 **Current Offers:**\n"
        for offer in phone['active_offers']:
            response += f"   • {offer['title']}: "
            if offer.get('discount_percentage'):
                response += f"{offer['discount_percentage']}% off"
            elif offer.get('discount_amount'):
                response += f"${offer['discount_amount']} off"
            response += f" (until {offer.get('end_date', 'TBD')})\n"
    
    return response

async def get_phone_offers_fastmcp(phone_name: str = None) -> str:
    """Get current offers using FastMCP server."""
    client = await get_fastmcp_client()
    
    arguments = {}
    if phone_name:
        arguments["phone_name"] = phone_name
    
    result = await client.call_tool("get_phone_offers", arguments)
    
    if "error" in result:
        return f"Error getting offers: {result['error']}"
    
    offers = result.get("offers", [])
    
    if not offers:
        if phone_name:
            return f"No current offers for '{phone_name}'."
        else:
            return "No current offers available."
    
    response = "🎁 **Current Offers:**\n\n"
    
    for offer in offers:
        response += f"**{offer['title']}**\n"
        if offer.get('model_name'):
            response += f"📱 Phone: {offer['model_name']}\n"
        
        if offer.get('description'):
            response += f"📝 {offer['description']}\n"
        
        if offer.get('discount_percentage'):
            response += f"💰 Discount: {offer['discount_percentage']}% off\n"
        elif offer.get('discount_amount'):
            response += f"💰 Discount: ${offer['discount_amount']} off\n"
        
        if offer.get('offer_price'):
            response += f"🏷️  Offer Price: ${offer['offer_price']}\n"
        
        if offer.get('end_date'):
            response += f"⏰ Valid until: {offer['end_date']}\n"
        
        response += "\n"
    
    return response.strip()

async def compare_phones_fastmcp(phone1: str, phone2: str) -> str:
    """Compare two phones using FastMCP server."""
    client = await get_fastmcp_client()
    
    result = await client.call_tool("compare_phones", {
        "phone1": phone1,
        "phone2": phone2
    })
    
    if "error" in result:
        return f"Error comparing phones: {result['error']}"
    
    comparison = result.get("comparison", {})
    summary = result.get("summary", {})
    
    if not comparison:
        return "Unable to compare phones."
    
    p1 = comparison.get("phone1", {})
    p2 = comparison.get("phone2", {})
    
    response = f"📱 **Phone Comparison**\n\n"
    
    # Basic comparison table
    response += f"| Feature | {p1.get('model_name', 'Phone 1')} | {p2.get('model_name', 'Phone 2')} |\n"
    response += f"|---------|------------|------------|\n"
    response += f"| **Price** | ${p1.get('price', 'N/A')} | ${p2.get('price', 'N/A')} |\n"
    response += f"| **Year** | {p1.get('year', 'N/A')} | {p2.get('year', 'N/A')} |\n"
    response += f"| **Chipset** | {p1.get('chipset_name', 'N/A')} | {p2.get('chipset_name', 'N/A')} |\n"
    response += f"| **RAM** | {p1.get('ram_size', 'N/A')} | {p2.get('ram_size', 'N/A')} |\n"
    response += f"| **Storage** | {p1.get('storage_size', 'N/A')} | {p2.get('storage_size', 'N/A')} |\n"
    response += f"| **Battery** | {p1.get('battery_capacity', 'N/A')} | {p2.get('battery_capacity', 'N/A')} |\n"
    
    # Summary
    if summary:
        response += f"\n**Summary:**\n"
        if summary.get('price_difference'):
            diff = summary['price_difference']
            if diff > 0:
                response += f"• {p2.get('model_name')} is ${abs(diff)} more expensive\n"
            else:
                response += f"• {p1.get('model_name')} is ${abs(diff)} more expensive\n"
        
        if summary.get('newer_phone'):
            response += f"• Newer model: {summary['newer_phone']}\n"
        
        if summary.get('better_value'):
            response += f"• Better value: {summary['better_value']}\n"
    
    return response

async def check_inventory_fastmcp(phone_name: str = None) -> str:
    """Check inventory using FastMCP server."""
    client = await get_fastmcp_client()
    
    arguments = {}
    if phone_name:
        arguments["phone_name"] = phone_name
    
    result = await client.call_tool("check_inventory", arguments)
    
    if "error" in result:
        return f"Error checking inventory: {result['error']}"
    
    inventory = result.get("inventory", [])
    
    if not inventory:
        if phone_name:
            return f"No inventory information found for '{phone_name}'."
        else:
            return "No inventory information available."
    
    response = "📦 **Inventory Status:**\n\n"
    
    for item in inventory:
        response += f"📱 **{item['model_name']}**\n"
        response += f"   💰 Price: ${item['price']}\n"
        response += f"   📦 In Stock: {item['stock_quantity']} units\n"
        
        if item.get('reserved_quantity', 0) > 0:
            response += f"   🔒 Reserved: {item['reserved_quantity']} units\n"
        
        available = item['stock_quantity'] - item.get('reserved_quantity', 0)
        if available > 0:
            response += f"   ✅ Available: {available} units\n"
        else:
            response += f"   ❌ Not available\n"
        
        response += "\n"
    
    return response.strip()

# Synchronous wrapper functions for ADK compatibility
import concurrent.futures
import threading

def _run_async_safely(coro):
    """Run async function safely, handling event loop issues."""
    try:
        # Try to get existing event loop
        loop = asyncio.get_running_loop()
        # If we're in an event loop, create a new thread
        def run_in_thread():
            new_loop = asyncio.new_event_loop()
            try:
                asyncio.set_event_loop(new_loop)
                return new_loop.run_until_complete(coro)
            finally:
                new_loop.close()
                asyncio.set_event_loop(None)
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            return future.result(timeout=30)  # 30 second timeout
            
    except RuntimeError:
        # No event loop running, safe to use asyncio.run
        return asyncio.run(coro)

def search_phones_sync(query: str = "", min_price: float = None, 
                      max_price: float = None, year: int = None) -> str:
    """Synchronous wrapper for search_phones_fastmcp."""
    try:
        return _run_async_safely(search_phones_fastmcp(query, min_price, max_price, year))
    except Exception as e:
        logger.error(f"Error in search_phones_sync: {e}")
        return f"Error searching phones: {str(e)}"

def get_phone_details_sync(phone_name: str) -> str:
    """Synchronous wrapper for get_phone_details_fastmcp."""
    try:
        return _run_async_safely(get_phone_details_fastmcp(phone_name))
    except Exception as e:
        logger.error(f"Error in get_phone_details_sync: {e}")
        return f"Error getting phone details: {str(e)}"

def get_phone_offers_sync(phone_name: str = None) -> str:
    """Synchronous wrapper for get_phone_offers_fastmcp."""
    try:
        return _run_async_safely(get_phone_offers_fastmcp(phone_name))
    except Exception as e:
        logger.error(f"Error in get_phone_offers_sync: {e}")
        return f"Error getting offers: {str(e)}"

def compare_phones_sync(phone1: str, phone2: str) -> str:
    """Synchronous wrapper for compare_phones_fastmcp."""
    try:
        return _run_async_safely(compare_phones_fastmcp(phone1, phone2))
    except Exception as e:
        logger.error(f"Error in compare_phones_sync: {e}")
        return f"Error comparing phones: {str(e)}"

def check_inventory_sync(phone_name: str = None) -> str:
    """Synchronous wrapper for check_inventory_fastmcp."""
    try:
        return _run_async_safely(check_inventory_fastmcp(phone_name))
    except Exception as e:
        logger.error(f"Error in check_inventory_sync: {e}")
        return f"Error checking inventory: {str(e)}"

# Test function
async def test_fastmcp_client():
    """Test the FastMCP client functionality."""
    print("🧪 Testing FastMCP Client...")
    
    client = PhoneShopFastMCPClient()
    
    if await client.ensure_connected():
        print("✅ Connection successful")
        
        # Test search
        print("\n🔍 Testing phone search...")
        result = await search_phones_fastmcp("Samsung")
        print(result[:200] + "..." if len(result) > 200 else result)
        
        # Test phone details
        print("\n📱 Testing phone details...")
        result = await get_phone_details_fastmcp("iPhone 15")
        print(result[:200] + "..." if len(result) > 200 else result)
        
    else:
        print("❌ Connection failed")

if __name__ == "__main__":
    asyncio.run(test_fastmcp_client())
