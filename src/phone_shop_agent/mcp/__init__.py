#!/usr/bin/env python3
"""
FastMCP Module for Phone Shop Agent

This module provides FastMCP client and server components for
real-time database access to phone information.
"""

from .fastmcp_client import (
    PhoneShopFastMCPClient,
    search_phones_sync,
    get_phone_details_sync,
    get_phone_offers_sync,
    compare_phones_sync,
    check_inventory_sync,
)

__all__ = [
    'PhoneShopFastMCPClient',
    'search_phones_sync',
    'get_phone_details_sync',
    'get_phone_offers_sync',
    'compare_phones_sync',
    'check_inventory_sync',
]
