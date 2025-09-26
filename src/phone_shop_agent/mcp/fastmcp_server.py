#!/usr/bin/env python3
"""
FastMCP Server for Phone Shop SQLite Database.
Provides tools for querying phone specifications, prices, offers, and inventory.
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("phone-shop-fastmcp-server")

# Initialize FastMCP server
mcp = FastMCP(name="PhoneShopServer")

# Database path - will be set during initialization
DB_PATH = None

def get_db_connection() -> sqlite3.Connection:
    """Get database connection with row factory."""
    if not DB_PATH or not Path(DB_PATH).exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn

def format_phone_dict(phone_row: sqlite3.Row) -> Dict[str, Any]:
    """Convert database row to dictionary with proper formatting."""
    phone = dict(phone_row)
    
    # Parse comma-separated features
    if phone.get('camera_features'):
        phone['camera_features'] = phone['camera_features'].split(',')
    else:
        phone['camera_features'] = []
        
    if phone.get('charging_features'):
        phone['charging_features'] = phone['charging_features'].split(',')
    else:
        phone['charging_features'] = []
    
    return phone

@mcp.tool
def search_phones(query: str = "", min_price: float = None, max_price: float = None, year: int = None) -> Dict[str, Any]:
    """Search phones by various criteria (name, price range, specs).
    
    Args:
        query: Search query (phone name, brand, or feature)
        min_price: Minimum price filter
        max_price: Maximum price filter
        year: Filter by release year
    
    Returns:
        Dictionary with search results and metadata
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql = '''
            SELECT p.*, 
                   GROUP_CONCAT(DISTINCT cf.feature) as camera_features,
                   GROUP_CONCAT(DISTINCT chf.feature) as charging_features
            FROM phones p
            LEFT JOIN camera_features cf ON p.id = cf.phone_id
            LEFT JOIN charging_features chf ON p.id = chf.phone_id
            WHERE 1=1
        '''
        params = []
        
        if query:
            sql += " AND (p.model_name LIKE ? OR p.chipset_name LIKE ? OR p.operating_system LIKE ?)"
            query_param = f"%{query}%"
            params.extend([query_param, query_param, query_param])
        
        if min_price is not None:
            sql += " AND p.price >= ?"
            params.append(min_price)
        
        if max_price is not None:
            sql += " AND p.price <= ?"
            params.append(max_price)
        
        if year is not None:
            sql += " AND p.year = ?"
            params.append(year)
        
        sql += " GROUP BY p.id ORDER BY p.price"
        
        cursor.execute(sql, params)
        
        phones = []
        for row in cursor.fetchall():
            phone = format_phone_dict(row)
            phones.append(phone)
        
        conn.close()
        
        return {
            "query": query,
            "filters": {
                "min_price": min_price,
                "max_price": max_price,
                "year": year
            },
            "results": phones,
            "count": len(phones)
        }
        
    except Exception as e:
        logger.error(f"Error searching phones: {str(e)}")
        return {
            "error": str(e),
            "results": [],
            "count": 0
        }

@mcp.tool
def get_phone_details(phone_name: str) -> Dict[str, Any]:
    """Get complete details for a specific phone.
    
    Args:
        phone_name: Exact phone model name
    
    Returns:
        Complete phone information with offers and inventory
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get phone details
        cursor.execute('''
            SELECT p.*, 
                   GROUP_CONCAT(DISTINCT cf.feature) as camera_features,
                   GROUP_CONCAT(DISTINCT chf.feature) as charging_features,
                   i.stock_quantity, i.reserved_quantity
            FROM phones p
            LEFT JOIN camera_features cf ON p.id = cf.phone_id
            LEFT JOIN charging_features chf ON p.id = chf.phone_id
            LEFT JOIN inventory i ON p.id = i.phone_id
            WHERE p.model_name LIKE ?
            GROUP BY p.id
        ''', (f"%{phone_name}%",))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return {"error": f"Phone '{phone_name}' not found"}
        
        phone = format_phone_dict(row)
        
        # Get active offers for this phone
        cursor.execute('''
            SELECT * FROM offers 
            WHERE phone_id = ? AND is_active = 1 
            AND (end_date IS NULL OR end_date >= date('now'))
        ''', (phone['id'],))
        
        offers = [dict(row) for row in cursor.fetchall()]
        phone['active_offers'] = offers
        
        conn.close()
        return phone
        
    except Exception as e:
        logger.error(f"Error getting phone details: {str(e)}")
        return {"error": str(e)}

@mcp.tool
def get_phone_offers(phone_name: str = None) -> Dict[str, Any]:
    """Get current offers for a specific phone or all phones.
    
    Args:
        phone_name: Phone model name (optional, if not provided returns all offers)
    
    Returns:
        Dictionary with current offers
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if phone_name:
            cursor.execute('''
                SELECT o.*, p.model_name
                FROM offers o
                JOIN phones p ON o.phone_id = p.id
                WHERE p.model_name LIKE ? AND o.is_active = 1
                AND (o.end_date IS NULL OR o.end_date >= date('now'))
                ORDER BY o.created_at DESC
            ''', (f"%{phone_name}%",))
        else:
            cursor.execute('''
                SELECT o.*, p.model_name
                FROM offers o
                LEFT JOIN phones p ON o.phone_id = p.id
                WHERE o.is_active = 1
                AND (o.end_date IS NULL OR o.end_date >= date('now'))
                ORDER BY o.created_at DESC
            ''')
        
        offers = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return {
            "phone_name": phone_name,
            "offers": offers,
            "count": len(offers)
        }
        
    except Exception as e:
        logger.error(f"Error getting offers: {str(e)}")
        return {"error": str(e), "offers": [], "count": 0}

@mcp.tool
def compare_phones(phone1: str, phone2: str) -> Dict[str, Any]:
    """Compare specifications between two phones.
    
    Args:
        phone1: First phone model name
        phone2: Second phone model name
    
    Returns:
        Detailed comparison between the two phones
    """
    try:
        phone1_details = get_phone_details(phone1)
        phone2_details = get_phone_details(phone2)
        
        if "error" in phone1_details:
            return phone1_details
        if "error" in phone2_details:
            return phone2_details
        
        return {
            "comparison": {
                "phone1": phone1_details,
                "phone2": phone2_details
            },
            "summary": {
                "price_difference": phone2_details['price'] - phone1_details['price'],
                "newer_phone": phone1_details['model_name'] if phone1_details['year'] > phone2_details['year'] else phone2_details['model_name'],
                "better_value": phone1_details['model_name'] if phone1_details['price'] < phone2_details['price'] else phone2_details['model_name']
            }
        }
        
    except Exception as e:
        logger.error(f"Error comparing phones: {str(e)}")
        return {"error": str(e)}

@mcp.tool
def check_inventory(phone_name: str = None) -> Dict[str, Any]:
    """Check stock availability for phones.
    
    Args:
        phone_name: Phone model name (optional, if not provided returns all inventory)
    
    Returns:
        Dictionary with inventory information
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if phone_name:
            cursor.execute('''
                SELECT i.*, p.model_name, p.price
                FROM inventory i
                JOIN phones p ON i.phone_id = p.id
                WHERE p.model_name LIKE ?
            ''', (f"%{phone_name}%",))
        else:
            cursor.execute('''
                SELECT i.*, p.model_name, p.price
                FROM inventory i
                JOIN phones p ON i.phone_id = p.id
                ORDER BY p.model_name
            ''')
        
        inventory = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return {
            "phone_name": phone_name,
            "inventory": inventory,
            "count": len(inventory)
        }
        
    except Exception as e:
        logger.error(f"Error checking inventory: {str(e)}")
        return {"error": str(e), "inventory": [], "count": 0}

@mcp.tool
def get_price_range(min_price: float, max_price: float) -> Dict[str, Any]:
    """Get phones within a specific price range.
    
    Args:
        min_price: Minimum price
        max_price: Maximum price
    
    Returns:
        Dictionary with phones in the price range
    """
    return search_phones(min_price=min_price, max_price=max_price)

# Resources for direct database access
@mcp.resource("sqlite://phones")
def get_all_phones() -> str:
    """Get all phones from database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.*, 
                   GROUP_CONCAT(DISTINCT cf.feature) as camera_features,
                   GROUP_CONCAT(DISTINCT chf.feature) as charging_features
            FROM phones p
            LEFT JOIN camera_features cf ON p.id = cf.phone_id
            LEFT JOIN charging_features chf ON p.id = chf.phone_id
            GROUP BY p.id
            ORDER BY p.model_name
        ''')
        
        phones = []
        for row in cursor.fetchall():
            phone = format_phone_dict(row)
            phones.append(phone)
        
        conn.close()
        return json.dumps(phones, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting all phones: {str(e)}")
        return json.dumps({"error": str(e)})

@mcp.resource("sqlite://offers")
def get_active_offers() -> str:
    """Get all active offers."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT o.*, p.model_name
            FROM offers o
            LEFT JOIN phones p ON o.phone_id = p.id
            WHERE o.is_active = 1 
            AND (o.end_date IS NULL OR o.end_date >= date('now'))
            ORDER BY o.created_at DESC
        ''')
        
        offers = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return json.dumps(offers, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting active offers: {str(e)}")
        return json.dumps({"error": str(e)})

@mcp.resource("sqlite://inventory")
def get_inventory_status() -> str:
    """Get inventory status for all phones."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT i.*, p.model_name, p.price
            FROM inventory i
            JOIN phones p ON i.phone_id = p.id
            ORDER BY p.model_name
        ''')
        
        inventory = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return json.dumps(inventory, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting inventory status: {str(e)}")
        return json.dumps({"error": str(e)})

def initialize_server(db_path: str):
    """Initialize the server with database path."""
    global DB_PATH
    DB_PATH = db_path
    
    if not Path(db_path).exists():
        raise FileNotFoundError(f"Database not found: {db_path}")
    
    logger.info(f"FastMCP server initialized with database: {db_path}")

def main():
    """Run the FastMCP server."""
    # Database path - use absolute path
    db_path = Path(__file__).parent.parent / "database" / "phone_shop.db"
    db_path = db_path.resolve()  # Convert to absolute path
    
    try:
        initialize_server(str(db_path))
        logger.info(f"Starting FastMCP Phone Shop Server with database: {db_path}")
        
        # Verify database exists and is accessible
        if not db_path.exists():
            raise FileNotFoundError(f"Database file not found: {db_path}")
        
        # Test database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM phones")
        phone_count = cursor.fetchone()[0]
        conn.close()
        logger.info(f"Database connected successfully. Found {phone_count} phones.")
        
        # Run the server
        mcp.run()
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise

if __name__ == "__main__":
    main()
