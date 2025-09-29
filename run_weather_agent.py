#!/usr/bin/env python3
"""
Weather Agent Runner using Google ADK

This script demonstrates how to run the weather agent using Google ADK.
The agent can answer questions about weather and time in various cities.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def run_weather_agent():
    """Run the weather agent interactively."""
    print("🌤️  Weather & Time Agent")
    print("=" * 50)
    print("Ask me about weather or time in any city!")
    print("Examples:")
    print("  - What's the weather in New York?")
    print("  - What time is it in Tokyo?")
    print("  - Tell me about the weather in London")
    print("  - Current time in Paris")
    print("\nType 'quit' to exit")
    print("=" * 50)
    
    try:
        # Import the weather agent
        from weather_agent import root_agent
        print(f"✅ Weather agent loaded: {root_agent.name}")
        print(f"   Model: {root_agent.model}")
        print(f"   Available tools: {len(root_agent.tools)}")
        
        # Interactive loop
        while True:
            try:
                user_input = input("\n🌍 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                print("🤖 Agent: Processing your request...")
                
                # Here you would typically use the Google ADK to process the input
                # For now, let's demonstrate the tools directly
                
                # Check if it's a weather question
                if any(word in user_input.lower() for word in ['weather', 'temperature', 'wind']):
                    # Extract city name (simple approach)
                    words = user_input.split()
                    city = None
                    for i, word in enumerate(words):
                        if word.lower() in ['in', 'for', 'at']:
                            if i + 1 < len(words):
                                city = ' '.join(words[i+1:]).strip('?.,!')
                                break
                    
                    if city:
                        from weather_agent.agent import get_weather
                        result = get_weather(city)
                        if result['status'] == 'success':
                            print(f"🌤️  {result['report']}")
                        else:
                            print(f"❌ {result['error_message']}")
                    else:
                        print("❓ Please specify a city for the weather query.")
                
                # Check if it's a time question
                elif any(word in user_input.lower() for word in ['time', 'clock']):
                    # Extract city name (simple approach)
                    words = user_input.split()
                    city = None
                    for i, word in enumerate(words):
                        if word.lower() in ['in', 'for', 'at']:
                            if i + 1 < len(words):
                                city = ' '.join(words[i+1:]).strip('?.,!')
                                break
                    
                    if city:
                        from weather_agent.agent import get_current_time
                        result = get_current_time(city)
                        if result['status'] == 'success':
                            print(f"🕐 {result['report']}")
                        else:
                            print(f"❌ {result['error_message']}")
                    else:
                        print("❓ Please specify a city for the time query.")
                
                else:
                    print("❓ I can help with weather and time information. Try asking about weather or time in a city!")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    except ImportError as e:
        print(f"❌ Failed to import weather agent: {e}")
        print("Make sure the weather_agent module is properly set up.")
    except Exception as e:
        print(f"❌ Error running weather agent: {e}")

def test_weather_agent():
    """Test the weather agent tools directly."""
    print("🧪 Testing Weather Agent Tools")
    print("=" * 40)
    
    try:
        from weather_agent.agent import get_weather, get_current_time
        
        # Test weather function
        print("\n🌤️  Testing Weather Function:")
        result = get_weather("New York")
        if result['status'] == 'success':
            print(f"✅ {result['report']}")
        else:
            print(f"❌ {result['error_message']}")
        
        # Test time function
        print("\n🕐 Testing Time Function:")
        result = get_current_time("Tokyo")
        if result['status'] == 'success':
            print(f"✅ {result['report']}")
        else:
            print(f"❌ {result['error_message']}")
        
        print("\n✅ Weather agent tools are working!")
        
    except Exception as e:
        print(f"❌ Error testing weather agent: {e}")

def main():
    """Main function to choose between running or testing the agent."""
    print("🌤️  Weather Agent with Google ADK")
    print("=" * 50)
    print("Choose an option:")
    print("1. Run interactive weather agent")
    print("2. Test weather agent tools")
    print("3. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == '1':
                run_weather_agent()
                break
            elif choice == '2':
                test_weather_agent()
                break
            elif choice == '3':
                print("👋 Goodbye!")
                break
            else:
                print("❓ Please enter 1, 2, or 3")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

if __name__ == "__main__":
    main()
