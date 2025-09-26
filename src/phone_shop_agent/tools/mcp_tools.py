#!/usr/bin/env python3
"""
FastMCP-powered tools for phone shop agent.
Provides database-backed phone information tools via FastMCP server.

This module contains only MCP-powered tools for phone database operations.
RAG-powered policy tools are in the separate 'tool.py' module.
"""

import logging
from typing import Optional

# Import FastMCP client functions
from ..mcp.fastmcp_client import (
    search_phones_sync,
    get_phone_details_sync,
    get_phone_offers_sync,
    check_inventory_sync
)

# Configure logging
logger = logging.getLogger(__name__)


# MCP-powered phone tools
def get_phone_price(phone_name: str) -> str:
    """Get the price of a phone by its model name using MCP database.
    
    Args:
        phone_name: The model name of the phone (e.g., 'Samsung Galaxy S23').
    
    Returns:
        A string with the price information or error message.
    """
    try:
        result = get_phone_details_sync(phone_name)
        
        # Extract price from the detailed result
        if "not found" in result.lower() or "error" in result.lower():
            return f"Sorry, I couldn't find a phone with the model name '{phone_name}'."
        
        # Parse the price from the formatted response
        lines = result.split('\n')
        for line in lines:
            if 'Price:' in line:
                price_part = line.split('Price:')[1].strip()
                return f"The price of {phone_name} is {price_part}."
        
        return f"Price information not available for '{phone_name}'."
        
    except Exception as e:
        return f"Error retrieving price for '{phone_name}': {str(e)}"

def get_phone_specs(phone_name: str) -> str:
    """Get the full specifications of a phone by its model name using MCP database.
    
    Args:
        phone_name: The model name of the phone.
    
    Returns:
        A formatted string with all specifications or error message.
    """
    try:
        return get_phone_details_sync(phone_name)
    except Exception as e:
        return f"Error retrieving specifications for '{phone_name}': {str(e)}"

def list_available_phones() -> str:
    """List all available phones in the database.
    
    Returns:
        A formatted string with all available phones.
    """
    try:
        # Search with empty query to get all phones
        return search_phones_sync("")
    except Exception as e:
        return f"Error retrieving phone list: {str(e)}"

def compare_phones(phone1: str, phone2: str) -> str:
    """Compare specifications between two phones using MCP database.
    
    Args:
        phone1: First phone model name.
        phone2: Second phone model name.
    
    Returns:
        A formatted comparison between the two phones.
    """
    try:
        # Import and call the sync wrapper function to avoid any circular imports
        from ..mcp.fastmcp_client import compare_phones_sync as mcp_compare_sync
        result = mcp_compare_sync(phone1, phone2)
        return result
    except Exception as e:
        logger.error(f"Error in compare_phones: {e}")
        return f"Error comparing phones: {str(e)}"

def search_phones_by_criteria(query: str = "", min_price: Optional[float] = None, 
                             max_price: Optional[float] = None, year: Optional[int] = None) -> str:
    """Search phones by various criteria using MCP database.
    
    Args:
        query: Search query (phone name, brand, or feature).
        min_price: Minimum price filter.
        max_price: Maximum price filter.
        year: Filter by release year.
    
    Returns:
        A formatted string with search results.
    """
    try:
        result = search_phones_sync(query, min_price, max_price, year)
        return result
    except Exception as e:
        logger.error(f"Error in search_phones_by_criteria: {e}")
        return f"Error searching phones: {str(e)}"

def get_current_offers(phone_name: Optional[str] = None) -> str:
    """Get current offers for phones using MCP database.
    
    Args:
        phone_name: Optional phone model name. If not provided, returns all offers.
    
    Returns:
        A formatted string with current offers.
    """
    try:
        from ..mcp.fastmcp_client import get_phone_offers_sync
        result = get_phone_offers_sync(phone_name)
        return result
    except Exception as e:
        logger.error(f"Error in get_current_offers: {e}")
        return f"Error retrieving offers: {str(e)}"

def check_phone_availability(phone_name: Optional[str] = None) -> str:
    """Check stock availability for phones using MCP database.
    
    Args:
        phone_name: Optional phone model name. If not provided, returns all inventory.
    
    Returns:
        A formatted string with inventory information.
    """
    try:
        result = check_inventory_sync(phone_name)
        return result
    except Exception as e:
        logger.error(f"Error in check_phone_availability: {e}")
        return f"Error checking availability: {str(e)}"

# Export all MCP-powered phone tools
__all__ = [
    'get_phone_price',
    'get_phone_specs',
    'list_available_phones',
    'compare_phones',
    'search_phones_by_criteria',
    'get_current_offers',
    'check_phone_availability',
]
