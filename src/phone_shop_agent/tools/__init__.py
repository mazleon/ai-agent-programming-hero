#!/usr/bin/env python3
"""
Phone Shop Agent Tools Module

This module provides two categories of tools:
1. MCP-powered tools for real-time phone database operations
2. RAG-powered tools for policy and support information
"""

# MCP-powered phone database tools
from .mcp_tools import (
    get_phone_price,
    get_phone_specs,
    list_available_phones,
    compare_phones,
    search_phones_by_criteria,
    get_current_offers,
    check_phone_availability,
)

# RAG-powered policy tools
from .tool import (
    get_warranty_information,
    get_replacement_information,
    get_customer_support_information,
    search_phone_shop_policies,
)

# Export all tools
__all__ = [
    # MCP-powered phone tools
    'get_phone_price',
    'get_phone_specs',
    'list_available_phones',
    'compare_phones',
    'search_phones_by_criteria',
    'get_current_offers',
    'check_phone_availability',
    
    # RAG-powered policy tools
    'get_warranty_information',
    'get_replacement_information',
    'get_customer_support_information',
    'search_phone_shop_policies',
]
