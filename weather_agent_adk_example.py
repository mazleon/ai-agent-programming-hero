#!/usr/bin/env python3
"""
Weather Agent Google ADK Integration Example

This script shows how to properly integrate and run the weather agent
using Google ADK in different scenarios.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def run_with_google_adk():
    """Example of running weather agent with Google ADK."""
    print("🌤️  Weather Agent with Google ADK Integration")
    print("=" * 60)
    
    try:
        # Import the weather agent
        from weather_agent import root_agent
        
        print(f"✅ Agent loaded: {root_agent.name}")
        print(f"   Model: {root_agent.model}")
        print(f"   Description: {root_agent.description}")
        print(f"   Tools: {[tool.__name__ for tool in root_agent.tools]}")
        
        # Example 1: Direct tool usage
        print("\n📋 Example 1: Direct Tool Usage")
        print("-" * 40)
        
        from weather_agent.agent import get_weather, get_current_time
        
        # Test weather
        weather_result = get_weather("London")
        print(f"Weather in London: {weather_result}")
        
        # Test time
        time_result = get_current_time("New York")
        print(f"Time in New York: {time_result}")
        
        # Example 2: Agent configuration for different use cases
        print("\n📋 Example 2: Agent Configuration")
        print("-" * 40)
        
        print("Agent Instructions:")
        print(root_agent.instruction)
        
        # Example 3: Integration patterns
        print("\n📋 Example 3: Integration Patterns")
        print("-" * 40)
        
        print("1. **Standalone Agent**: Use the agent directly in your application")
        print("2. **API Integration**: Expose agent through REST API")
        print("3. **Chat Interface**: Integrate with chat applications")
        print("4. **Scheduled Tasks**: Use for automated weather reports")
        
        return root_agent
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def create_weather_api_server():
    """Example of creating a simple API server for the weather agent."""
    print("\n🌐 Creating Weather API Server Example")
    print("-" * 50)
    
    api_code = '''
from flask import Flask, request, jsonify
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from weather_agent.agent import get_weather, get_current_time

app = Flask(__name__)

@app.route('/weather/<city>')
def weather_api(city):
    """Get weather for a city."""
    result = get_weather(city)
    return jsonify(result)

@app.route('/time/<city>')
def time_api(city):
    """Get current time for a city."""
    result = get_current_time(city)
    return jsonify(result)

@app.route('/agent/query', methods=['POST'])
def agent_query():
    """Process natural language queries."""
    data = request.get_json()
    query = data.get('query', '')
    
    # Simple query processing (in real implementation, use the full ADK)
    if 'weather' in query.lower():
        # Extract city and get weather
        # This is simplified - use proper NLP in production
        words = query.split()
        for i, word in enumerate(words):
            if word.lower() in ['in', 'for', 'at'] and i + 1 < len(words):
                city = words[i + 1]
                return jsonify(get_weather(city))
    
    elif 'time' in query.lower():
        # Extract city and get time
        words = query.split()
        for i, word in enumerate(words):
            if word.lower() in ['in', 'for', 'at'] and i + 1 < len(words):
                city = words[i + 1]
                return jsonify(get_current_time(city))
    
    return jsonify({"status": "error", "error_message": "Could not understand query"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
'''
    
    print("Save this code as 'weather_api.py' to create a REST API:")
    print("```python")
    print(api_code)
    print("```")
    
    print("\nTo run the API server:")
    print("1. Install Flask: pip install flask")
    print("2. Run: python weather_api.py")
    print("3. Test endpoints:")
    print("   - GET /weather/London")
    print("   - GET /time/Tokyo")
    print("   - POST /agent/query with JSON: {'query': 'What is the weather in Paris?'}")

def show_deployment_options():
    """Show different deployment options for the weather agent."""
    print("\n🚀 Deployment Options")
    print("-" * 30)
    
    print("1. **Local Development**:")
    print("   - Run directly with: python run_weather_agent.py")
    print("   - Test tools individually")
    print("   - Interactive development")
    
    print("\n2. **Google ADK Integration**:")
    print("   - Import the agent: from weather_agent import root_agent")
    print("   - Use with Google ADK runtime")
    print("   - Leverage ADK's conversation management")
    
    print("\n3. **API Server**:")
    print("   - Create REST API endpoints")
    print("   - Use Flask/FastAPI")
    print("   - Deploy to cloud platforms")
    
    print("\n4. **Chat Integration**:")
    print("   - Integrate with Discord/Slack bots")
    print("   - Use with Telegram/WhatsApp")
    print("   - Web chat interfaces")
    
    print("\n5. **Scheduled Services**:")
    print("   - Daily weather reports")
    print("   - Automated notifications")
    print("   - Monitoring systems")

def main():
    """Main function to demonstrate weather agent usage."""
    print("🌤️  Weather Agent Google ADK Guide")
    print("=" * 60)
    
    # Run the main example
    agent = run_with_google_adk()
    
    if agent:
        # Show API server example
        create_weather_api_server()
        
        # Show deployment options
        show_deployment_options()
        
        print("\n✅ Weather Agent Setup Complete!")
        print("\nNext Steps:")
        print("1. Run: python run_weather_agent.py")
        print("2. Test the agent interactively")
        print("3. Integrate with your application")
        print("4. Deploy using your preferred method")
    
    else:
        print("❌ Failed to load weather agent. Please check the setup.")

if __name__ == "__main__":
    main()
