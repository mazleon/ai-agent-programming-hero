# Claude Desktop MCP Configuration

## Configuration File Location (Windows)
```
%APPDATA%\Claude\claude_desktop_config.json
```

## Example Configuration
```json
{
  "mcpServers": {
    "phone-shop-server": {
      "command": "fastmcp",
      "args": ["run", "src/phone_shop_agent/mcp/fastmcp_server.py"],
      "cwd": "D:\\AI_Chatbot\\Gemini-ai-bot",
      "env": {
        "PYTHONPATH": "D:\\AI_Chatbot\\Gemini-ai-bot\\src"
      }
    }
  }
}
```

## Setup Steps

1. **Create the config file** at `%APPDATA%\Claude\claude_desktop_config.json`
2. **Copy the configuration** above into the file
3. **Restart Claude Desktop** completely
4. **Test the connection** by asking Claude about phones

## Troubleshooting

- **Server not found**: Make sure the `cwd` path is correct
- **Import errors**: The `PYTHONPATH` environment variable helps FastMCP find your modules
- **Database errors**: Ensure the database file exists at `src/phone_shop_agent/database/phone_shop.db`

## Available Tools in Claude Desktop

Once connected, Claude will have access to:
- `search_phones` - Search phones by criteria
- `get_phone_details` - Get detailed phone information
- `get_phone_offers` - Get current offers
- `compare_phones` - Compare two phones
- `check_inventory` - Check stock availability
- `get_price_range` - Get phones in price range

## Testing

Try asking Claude: *"What phones do you have available?"* or *"Tell me about the iPhone 15"* to test the connection.
