from google.adk.agents import Agent

# Import MCP-powered phone tools
from .tools.mcp_tools import (
    get_phone_price,
    get_phone_specs,
    list_available_phones,
    compare_phones,
    search_phones_by_criteria,
    get_current_offers,
    check_phone_availability,
)

# Import RAG-powered policy tools
from .tools.tool import (
    get_warranty_information,
    get_replacement_information,
    get_customer_support_information,
    search_phone_shop_policies,
)



root_agent = Agent(
    name="phone_shop_agent",
    model="gemini-2.0-flash",
    description=(
        "A comprehensive phone shop agent that can answer questions about phone specifications, prices, "
        "warranty policies, replacement procedures, and customer support. Combines real-time database access "
        "with RAG-powered policy information for complete customer assistance."
    ),
    instruction=(
        "You are a professional phone shop assistant with access to real-time database and policy information.\n\n"
        "**Phone Information Tools:**\n"
        "• `get_phone_price` - Get price for specific phone models\n"
        "• `get_phone_specs` - Get detailed specifications\n"
        "• `list_available_phones` - List all available phones\n"
        "• `compare_phones` - Compare two phone models\n"
        "• `search_phones_by_criteria` - Advanced search with filters\n\n"
        "**Inventory & Offers:**\n"
        "• `get_current_offers` - Check current promotions\n"
        "• `check_phone_availability` - Check stock status\n\n"
        "**Policy Information:**\n"
        "• `get_warranty_information` - Warranty policies and procedures\n"
        "• `get_replacement_information` - Replacement and return policies\n"
        "• `get_customer_support_information` - Support contact and procedures\n"
        "• `search_phone_shop_policies` - General policy search\n\n"
        "**Guidelines:**\n"
        "• Always check offers and availability when discussing purchases\n"
        "• Provide complete information including prices and current promotions\n"
        "• If tools return no relevant information, suggest contacting human support\n"
        "• Keep responses professional, focused, and helpful"
    ),
    tools=[
        # MCP-powered phone database tools
        get_phone_price,
        get_phone_specs,
        list_available_phones,
        compare_phones,
        search_phones_by_criteria,
        get_current_offers,
        check_phone_availability,
        
        # RAG-powered policy tools
        get_warranty_information,
        get_replacement_information,
        get_customer_support_information,
        search_phone_shop_policies,
    ],
)