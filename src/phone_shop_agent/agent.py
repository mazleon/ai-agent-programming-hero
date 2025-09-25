from google.adk.agents import Agent
from .tools.tool import (
    get_phone_price, 
    get_phone_specs, 
    list_available_phones, 
    compare_phones,
    get_warranty_information,
    get_replacement_information,
    get_customer_support_information,
    search_phone_shop_policies
)




root_agent = Agent(
    name="phone_shop_agent",
    model="gemini-2.0-flash",
    description=(
        "A comprehensive phone shop agent that can answer questions about phone specifications, prices, "
        "warranty policies, replacement procedures, and customer support. Uses RAG (Retrieval-Augmented Generation) "
        "to provide accurate information from policy documents."
    ),
    instruction=(
        "You are a concise, knowledgeable phone shop assistant.\n"
        "• Use `get_phone_price`, `get_phone_specs`, `list_available_phones`, or `compare_phones` for device data.\n"
        "• Use the policy search tools for any warranty, replacement, support, or general store questions.\n"
        "• If a tool returns no relevant information, state that clearly and suggest contacting human support.\n"
        "Respond professionally, keep answers focused on the customer's question, and cite sources when available."
    ),
    tools=[
        get_phone_price, 
        get_phone_specs, 
        list_available_phones, 
        compare_phones,
        get_warranty_information,
        get_replacement_information,
        get_customer_support_information,
        search_phone_shop_policies
    ],
)