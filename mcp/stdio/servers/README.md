# MCP Weather Server

A Model Context Protocol (MCP) server that provides weather information through the National Weather Service (NWS) API.

## Overview

This MCP server provides two main tools:
- **get-alerts**: Retrieve active weather alerts for a US state
- **get-forecast**: Get weather forecasts for specific coordinates (latitude/longitude)

## Prerequisites

### System Requirements
- **Node.js**: Version 18 or higher
- **npm** or **pnpm**: Package manager
- **TypeScript**: For development (installed as dev dependency)

### API Requirements
- This server uses the **National Weather Service (NWS) API**
- No API key required (free public API)
- Only supports US locations

## Installation

1. Navigate to the server directory:
   ```bash
   cd mcp/stdio/servers
   ```

2. Install dependencies:
   ```bash
   pnpm install
   # or
   npm install
   ```

3. Build the TypeScript code:
   ```bash
   pnpm run build
   # or
   npm run build
   ```

## Usage

### Running the Server

The server is designed to be used with MCP clients via stdio transport:

```bash
node ./build/example/index.js
```

### Available Tools

#### 1. get-alerts
Retrieves active weather alerts for a US state.

**Parameters:**
- `state` (string): Two-letter state code (e.g., "CA", "NY", "TX")

**Example usage:**
```json
{
  "name": "get-alerts",
  "arguments": {
    "state": "CA"
  }
}
```

#### 2. get-forecast
Gets weather forecast for specific coordinates.

**Parameters:**
- `latitude` (number): Latitude (-90 to 90)
- `longitude` (number): Longitude (-180 to 180)

**Example usage:**
```json
{
  "name": "get-forecast",
  "arguments": {
    "latitude": 37.7749,
    "longitude": -122.4194
  }
}
```

## Development

### Project Structure

```
mcp/stdio/servers/
├── example/
│   ├── index.ts              # Main server implementation
│   ├── tools.ts              # Tool definitions (currently empty)
│   └── utils/
│       └── makeNWSRequest.ts # NWS API helper functions
├── build/                    # Compiled JavaScript output
├── package.json              # Dependencies and scripts
├── tsconfig.json            # TypeScript configuration
└── README.md                # This file
```

### Key Files

- **`index.ts`**: Main server entry point with tool registrations
- **`utils/makeNWSRequest.ts`**: Contains:
  - HTTP request helper for NWS API
  - Zod schemas for API response validation
  - Alert formatting utilities

### Building from Source

```bash
# Install dependencies
pnpm install

# Build TypeScript
pnpm run build

# The compiled JavaScript will be in ./build/example/
```

### Error Handling

The server includes comprehensive error handling:
- Invalid coordinates return descriptive error messages
- Network failures are caught and logged
- Unsupported locations (non-US) return appropriate responses
- Malformed API responses are handled gracefully

## Integration with MCP Clients

This server is designed to work with any MCP-compatible client. The most common integration is with:

1. **Claude Desktop**: Configure in Claude's MCP settings
2. **Custom MCP Clients**: Connect via stdio transport
3. **Development Tools**: Use for testing MCP implementations

### Example Client Configuration

For Claude Desktop, add to your MCP configuration:

```json
{
  "mcpServers": {
    "weather": {
      "command": "node",
      "args": ["/path/to/mcp/stdio/servers/build/example/index.js"]
    }
  }
}
```

## API Reference

### National Weather Service API

This server uses the following NWS endpoints:
- **Alerts**: `https://api.weather.gov/alerts?area={STATE}`
- **Grid Points**: `https://api.weather.gov/points/{lat},{lon}`
- **Forecasts**: `https://api.weather.gov/gridpoints/{office}/{gridX},{gridY}/forecast`

### Response Formats

All tools return content in the MCP standard format:

```json
{
  "content": [
    {
      "type": "text",
      "text": "Formatted weather information..."
    }
  ]
}
```

## Troubleshooting

### Common Issues

1. **"Failed to retrieve grid point data"**
   - Ensure coordinates are within the US
   - Check latitude/longitude format (decimal degrees)

2. **"No active alerts"**
   - This is normal - indicates no current weather alerts

3. **Network errors**
   - Check internet connectivity
   - NWS API may be temporarily unavailable

### Debugging

Enable debug logging by running:
```bash
DEBUG=* node ./build/example/index.js
```

## License

ISC License

## Contributing

1. Make changes to TypeScript files in `example/`
2. Run `pnpm run build` to compile
3. Test with an MCP client
4. Submit pull requests with clear descriptions 