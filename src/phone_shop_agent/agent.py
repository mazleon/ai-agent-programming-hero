from google.adk.agents import Agent
from .tools.tool import get_phone_price, get_phone_specs, list_available_phones, compare_phones




root_agent = Agent(
    name="phone_shop_agent",
    model="gemini-2.0-flash",
    description=(
        "A phone shop agent to answer questions about the phone shop."
    ),
    instruction=(
        "You are a helpful phone shop agent who can answer user questions about the phone shop."
    ),
    tools=[get_phone_price, get_phone_specs, list_available_phones, compare_phones],
)