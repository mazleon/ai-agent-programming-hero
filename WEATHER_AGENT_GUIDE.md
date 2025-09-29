# Weather Agent with Google ADK - Complete Guide

## 🌤️ Overview

The Weather Agent is a Google ADK-powered agent that can provide weather information and current time for various cities around the world.

## ✅ Features

- **Weather Information**: Get current weather for any city using Open-Meteo API
- **Time Information**: Get current time for major cities with timezone support
- **Google ADK Integration**: Fully compatible with Google ADK framework
- **Error Handling**: Robust error handling for API failures and invalid inputs

## 🚀 Quick Start

### 1. **Run Interactive Weather Agent**
```bash
python run_weather_agent.py
```

### 2. **Test Agent Tools**
```bash
python weather_agent_adk_example.py
```

### 3. **Import in Your Code**
```python
from weather_agent import root_agent, get_weather, get_current_time

# Use the agent
agent = root_agent

# Or use tools directly
weather = get_weather("London")
time = get_current_time("Tokyo")
```

## 🛠️ Usage Examples

### Direct Tool Usage
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from weather_agent import get_weather, get_current_time

# Get weather
result = get_weather("New York")
if result['status'] == 'success':
    print(result['report'])
else:
    print(result['error_message'])

# Get time
result = get_current_time("Tokyo")
if result['status'] == 'success':
    print(result['report'])
else:
    print(result['error_message'])
```

### Google ADK Integration
```python
from weather_agent import root_agent

# The agent is ready to use with Google ADK
print(f"Agent: {root_agent.name}")
print(f"Model: {root_agent.model}")
print(f"Tools: {len(root_agent.tools)}")

# Use with ADK runtime (example)
# response = adk_runtime.process(root_agent, "What's the weather in Paris?")
```

## 🌍 Supported Cities

### Weather (Any city supported by Open-Meteo API)
- Works with any city name worldwide
- Automatically geocodes city names to coordinates
- Returns temperature and wind speed

### Time (Pre-configured timezones)
- New York (America/New_York)
- London (Europe/London)
- Tokyo (Asia/Tokyo)
- Paris (Europe/Paris)
- Sydney (Australia/Sydney)
- Los Angeles (America/Los_Angeles)
- Chicago (America/Chicago)
- Dubai (Asia/Dubai)
- Singapore (Asia/Singapore)
- Mumbai (Asia/Kolkata)
- Dhaka (Asia/Dhaka)

## 📋 API Reference

### `get_weather(city: str) -> dict`
Get current weather for a city.

**Parameters:**
- `city` (str): Name of the city

**Returns:**
```python
{
    "status": "success",
    "report": "The weather in London is 15°C with windspeed of 10 km/h."
}
# or
{
    "status": "error", 
    "error_message": "City 'InvalidCity' not found."
}
```

### `get_current_time(city: str) -> dict`
Get current time for a city.

**Parameters:**
- `city` (str): Name of the city

**Returns:**
```python
{
    "status": "success",
    "report": "The current time in Tokyo is 2025-01-26 15:30:45 JST+0900"
}
# or
{
    "status": "error",
    "error_message": "Sorry, I don't have timezone information for InvalidCity."
}
```

## 🔧 Configuration

### Agent Configuration
```python
root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.0-flash",
    description="Agent to answer questions about the time and weather in a city.",
    instruction="You are a helpful agent who can answer user questions about the time and weather in a city.",
    tools=[get_weather, get_current_time],
)
```

### Adding More Timezones
Edit the `timezone_map` in `get_current_time()` function:
```python
timezone_map = {
    "new york": "America/New_York",
    "your_city": "Your/Timezone",
    # Add more cities here
}
```

## 🌐 Deployment Options

### 1. **Local Development**
```bash
python run_weather_agent.py
```

### 2. **REST API Server**
```python
from flask import Flask, jsonify
from weather_agent import get_weather, get_current_time

app = Flask(__name__)

@app.route('/weather/<city>')
def weather_api(city):
    return jsonify(get_weather(city))

@app.route('/time/<city>')
def time_api(city):
    return jsonify(get_current_time(city))

if __name__ == '__main__':
    app.run(debug=True)
```

### 3. **Google ADK Production**
```python
from weather_agent import root_agent
# Deploy with Google ADK runtime
```

## 🧪 Testing

### Run All Tests
```bash
python weather_agent_adk_example.py
```

### Test Individual Functions
```python
from weather_agent import get_weather, get_current_time

# Test weather
print(get_weather("London"))

# Test time
print(get_current_time("New York"))
```

## 🔍 Troubleshooting

### Common Issues

1. **Import Error**: Make sure `src` directory is in Python path
2. **API Timeout**: Check internet connection for weather API
3. **Timezone Error**: City not in timezone_map - add it or use supported cities
4. **Requests Error**: Install requests: `pip install requests`

### Error Messages
- `"City 'X' not found"`: Invalid city name for weather
- `"Failed to fetch weather data"`: API connection issue
- `"Sorry, I don't have timezone information"`: City not in timezone map

## 📦 Dependencies

```bash
pip install requests google-adk-agents
```

## 🎯 Example Queries

When using with Google ADK, users can ask:
- "What's the weather in London?"
- "Tell me the current time in Tokyo"
- "How's the weather in New York today?"
- "What time is it in Paris right now?"

## 🚀 Next Steps

1. **Run the agent**: `python run_weather_agent.py`
2. **Test functionality**: Try weather and time queries
3. **Integrate**: Use in your applications
4. **Extend**: Add more cities or features
5. **Deploy**: Choose your deployment method

The weather agent is now ready for production use with Google ADK! 🌟
