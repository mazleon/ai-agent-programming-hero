# Gemini AI Chatbot

![Gemini AI Chatbot Cover](res/cover_photo.jpeg)

A powerful chatbot application powered by Google's Agent Development Kit (ADK), featuring multiple specialized agents for different domains.

## Features

- **Weather Agent**: Provides current weather information and time for various cities.
- **Phone Shop Agent**: A comprehensive phone shop assistant that can provide phone specifications, prices, comparisons, and list available models.

## Installation Process

1. **Create Virtual Environment**:
   You can use Python's built-in venv or uv for managing the virtual environment:
   ```bash
   python -m venv .venv
   ```
   or
   ```bash
   uv venv
   ```

2. **Activate Virtual Environment**:
   ```bash
   .venv\Scripts\activate  # On Windows
   source .venv/bin/activate  # On macOS/Linux
   ```

3. **Install Dependencies**:
   Install the Google Agent Development Kit:
   ```bash
   uv pip install google-adk
   ```

## Project Structure

```
gemini-ai-bot/
├── src/
│   ├── phone_shop_agent/
│   │   ├── __init__.py
│   │   ├── agent.py                 # Main phone shop agent configuration
│   │   ├── .env                     # Environment variables
│   │   ├── data/
│   │   │   └── phone_specifications.json  # Phone data with specs and prices
│   │   └── tools/
│   │       └── tool.py              # Tool functions for phone queries
│   └── weather_agent/
│       ├── __init__.py
│       ├── agent.py                 # Weather agent configuration
│       └── .env
├── pyproject.toml                   # Project configuration
├── uv.lock                          # Dependency lock file
└── README.md
```

## Running the Agents

Navigate to the `src` directory and run the desired agent:

### Phone Shop Agent
```bash
cd src
adk run phone_shop_agent
```

This agent can:
- Get phone prices by model name
- Retrieve detailed specifications
- List all available phones
- Compare specifications between two phones

Example queries:
- "What's the price of Samsung Galaxy S23?"
- "Tell me the specs of iPhone 15"
- "What phones do you have?"
- "Compare Google Pixel 8 and OnePlus 12"

### Weather Agent
```bash
cd src
adk run weather_agent
```

Provides weather and time information for cities.

## Configuration

Each agent has its own `.env` file for configuration. Make sure to set up any required API keys or environment variables there.

## Contributing

This project uses the Agent Development Kit for building modular AI agents. Feel free to add new agents or extend existing functionality.
