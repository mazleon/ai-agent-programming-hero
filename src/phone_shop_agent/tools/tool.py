# This file contains all the tools for phone shop agent
import json
import os
import sys
from pathlib import Path

# Add the parent directory to sys.path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Try to import RAG functions, with fallback to simple text search
RAG_AVAILABLE = False
try:
    from rag import (
        search_warranty_info,
        search_replacement_info,
        search_customer_support_info,
        search_general_policy_info
    )
    RAG_AVAILABLE = True
except ImportError as e:
    print(f"RAG system not available: {e}")
    # Fallback: create simple text search functions using the markdown files directly
    
    def _simple_text_search(file_path, query, max_results=3):
        """Simple text search in markdown files as fallback."""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Simple keyword matching
                query_words = query.lower().split()
                lines = content.split('\n')
                
                # Find lines containing query words
                matching_sections = []
                for i, line in enumerate(lines):
                    if any(word in line.lower() for word in query_words):
                        # Get context around the match
                        start = max(0, i - 2)
                        end = min(len(lines), i + 3)
                        section = '\n'.join(lines[start:end]).strip()
                        if section and section not in matching_sections:
                            matching_sections.append(section)
                
                return matching_sections[:max_results]
            return []
        except Exception:
            return []
    
    def search_warranty_info(query, max_results=3):
        warranty_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'warranty_policy.md')
        results = _simple_text_search(warranty_file, query, max_results)
        return {
            "found": len(results) > 0,
            "warranty_info": results if results else ["No warranty information found for your query."],
            "sources": ["warranty_policy"] if results else []
        }
    
    def search_replacement_info(query, max_results=3):
        replacement_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'replacement_policy.md')
        results = _simple_text_search(replacement_file, query, max_results)
        return {
            "found": len(results) > 0,
            "replacement_info": results if results else ["No replacement information found for your query."],
            "sources": ["replacement_policy"] if results else []
        }
    
    def search_customer_support_info(query, max_results=3):
        support_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'customer_support_faq.md')
        results = _simple_text_search(support_file, query, max_results)
        return {
            "found": len(results) > 0,
            "support_info": results if results else ["No customer support information found for your query."],
            "sources": ["customer_support_faq"] if results else []
        }
    
    def search_general_policy_info(query, max_results=5):
        all_results = []
        files = [
            ('warranty_policy.md', 'warranty'),
            ('replacement_policy.md', 'replacement'),
            ('customer_support_faq.md', 'support')
        ]
        
        for filename, doc_type in files:
            file_path = os.path.join(os.path.dirname(__file__), '..', 'data', filename)
            results = _simple_text_search(file_path, query, 2)
            for result in results:
                all_results.append({
                    'content': result,
                    'source': filename.replace('.md', ''),
                    'type': doc_type,
                    'relevance': 0.5  # Simple fallback relevance
                })
        
        return {
            "found": len(all_results) > 0,
            "policy_info": all_results[:max_results],
            "total_found": len(all_results)
        }

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


# RAG-powered policy search functions
def get_warranty_information(query: str) -> str:
    """Get warranty information based on user query.
    
    Args:
        query: User's question about warranty (e.g., "How long is the warranty?", "What's covered?")
    
    Returns:
        Relevant warranty information from policy documents.
    """
    try:
        result = search_warranty_info(query, max_results=3)
        
        if result.get('found', False):
            warranty_info = result['warranty_info']
            sources = result.get('sources', [])
            
            response = "Here's the warranty information I found:\n\n"
            for i, info in enumerate(warranty_info):
                response += f"{i+1}. {info}\n\n"
            
            if sources:
                response += f"Source: {', '.join(set(sources))}"
            
            return response.strip()
        else:
            return "I couldn't find specific warranty information for your query. Please contact our customer service at 1-800-PHONE-FIX for detailed warranty assistance."
            
    except Exception as e:
        return f"I'm having trouble accessing warranty information right now. Please contact our customer service at 1-800-PHONE-FIX for assistance. Error: {str(e)}"


def get_replacement_information(query: str) -> str:
    """Get replacement policy information based on user query.
    
    Args:
        query: User's question about replacement policy (e.g., "Can I return my phone?", "How to exchange?")
    
    Returns:
        Relevant replacement policy information from policy documents.
    """
    try:
        result = search_replacement_info(query, max_results=3)
        
        if result.get('found', False):
            replacement_info = result['replacement_info']
            sources = result.get('sources', [])
            
            response = "Here's the replacement policy information I found:\n\n"
            for i, info in enumerate(replacement_info):
                response += f"{i+1}. {info}\n\n"
            
            if sources:
                response += f"Source: {', '.join(set(sources))}"
            
            return response.strip()
        else:
            return "I couldn't find specific replacement policy information for your query. Please contact our customer service at 1-800-REPLACE for detailed replacement assistance."
            
    except Exception as e:
        return f"I'm having trouble accessing replacement policy information right now. Please contact our customer service at 1-800-REPLACE for assistance. Error: {str(e)}"


def get_customer_support_information(query: str) -> str:
    """Get customer support information based on user query.
    
    Args:
        query: User's question about customer support (e.g., "How to contact support?", "Store hours?")
    
    Returns:
        Relevant customer support information from policy documents.
    """
    try:
        # Add debug info about RAG availability
        rag_status = "RAG system" if RAG_AVAILABLE else "Simple text search"
        
        result = search_customer_support_info(query, max_results=3)
        
        if result.get('found', False):
            support_info = result['support_info']
            sources = result.get('sources', [])
            
            response = "Here's the customer support information I found:\n\n"
            for i, info in enumerate(support_info):
                response += f"{i+1}. {info}\n\n"
            
            if sources:
                response += f"Source: {', '.join(set(sources))}"
            
            # Add system info for debugging
            response += f"\n\n(Retrieved using: {rag_status})"
            
            return response.strip()
        else:
            return f"I couldn't find specific customer support information for your query using {rag_status}. You can reach our customer service at 1-800-PHONE-HELP or visit our website for live chat support."
            
    except Exception as e:
        return f"I'm having trouble accessing customer support information right now ({rag_status}). Please contact us at 1-800-PHONE-HELP for assistance. Error: {str(e)}"


def search_phone_shop_policies(query: str) -> str:
    """Search all phone shop policies and information.
    
    Args:
        query: User's general question about policies, procedures, or information
    
    Returns:
        Relevant information from all policy documents.
    """
    try:
        result = search_general_policy_info(query, max_results=5)
        
        if result.get('found', False):
            policy_info = result['policy_info']
            
            response = "Here's what I found in our policies:\n\n"
            for i, info in enumerate(policy_info):
                response += f"{i+1}. **{info['type'].replace('_', ' ').title()}** (Relevance: {info['relevance']})\n"
                response += f"   {info['content']}\n"
                response += f"   Source: {info['source']}\n\n"
            
            return response.strip()
        else:
            return "I couldn't find relevant policy information for your query. Please contact our customer service at 1-800-PHONE-HELP for more specific assistance."
            
    except Exception as e:
        return f"I'm having trouble accessing policy information right now. Please contact our customer service at 1-800-PHONE-HELP for assistance. Error: {str(e)}"
