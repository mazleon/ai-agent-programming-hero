# This file contains all the tools for phone shop agent
import json
import os

# Load phone data
data_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'phone_specifications.json')
with open(data_file, 'r') as f:
    phones = json.load(f)

def get_phone_price(phone_name: str) -> str:
    """Get the price of a phone by its model name.
    
    Args:
        phone_name: The model name of the phone (e.g., 'Samsung Galaxy S23').
    
    Returns:
        A string with the price or a message if not found.
    """
    for phone in phones:
        if phone['model_name'].lower() == phone_name.lower():
            return f"The price of {phone['model_name']} is ${phone['price']}."
    return f"Sorry, I couldn't find a phone with the model name '{phone_name}'."

def get_phone_specs(phone_name: str) -> str:
    """Get the full specifications of a phone by its model name.
    
    Args:
        phone_name: The model name of the phone.
    
    Returns:
        A formatted string with all specifications or a message if not found.
    """
    for phone in phones:
        if phone['model_name'].lower() == phone_name.lower():
            specs = f"""
Model: {phone['model_name']}
Year: {phone['year']}
Chipset: {phone['chipset_name']}
RAM: {phone['ram_size']}
Storage: {phone['storage_size']}
Display: {phone['display_size']}
Camera: {', '.join(phone['camera_features'])}
Charging: {phone['charging_features']}
Battery: {phone['battery_capacity']}
OS: {phone['operating_system']}
Price: ${phone['price']}
"""
            return specs.strip()
    return f"Sorry, I couldn't find specifications for '{phone_name}'."

def list_available_phones() -> str:
    """List all available phone models.
    
    Returns:
        A string listing all phone model names.
    """
    models = [phone['model_name'] for phone in phones]
    return "Available phones: " + ", ".join(models)

def compare_phones(phone1: str, phone2: str) -> str:
    """Compare two phones by their specifications.
    
    Args:
        phone1: Model name of the first phone.
        phone2: Model name of the second phone.
    
    Returns:
        A comparison string or error if not found.
    """
    p1 = next((p for p in phones if p['model_name'].lower() == phone1.lower()), None)
    p2 = next((p for p in phones if p['model_name'].lower() == phone2.lower()), None)
    if not p1 or not p2:
        return "One or both phones not found."
    
    comparison = f"""
Comparison between {p1['model_name']} and {p2['model_name']}:

Price: ${p1['price']} vs ${p2['price']}
Year: {p1['year']} vs {p2['year']}
Chipset: {p1['chipset_name']} vs {p2['chipset_name']}
RAM: {p1['ram_size']} vs {p2['ram_size']}
Storage: {p1['storage_size']} vs {p2['storage_size']}
Display: {p1['display_size']} vs {p2['display_size']}
Battery: {p1['battery_capacity']} vs {p2['battery_capacity']}
"""
    return comparison.strip()
