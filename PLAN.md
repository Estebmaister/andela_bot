# Customer Support Chatbot - Project Plan

## Overview
A customer support chatbot for a computer products company (monitors, printers, etc.) that integrates with an MCP server for product data access.

## Tech Stack
- **Backend**: FastAPI (Python)
- **LLM**: OpenRouter/OpenAI GPT-4o-mini (cheap, fast, supports tool calling)
- **MCP Client**: FastMCP Python SDK (connects via Streamable HTTP)
- **Frontend**: Simple HTML/JS chat UI served directly by FastAPI
- **Deployment**: Render (free tier)

---

## Architecture

```
andela_bot/
├── app/
│   ├── __init__.py
│   ├── config.py              # Environment configuration
│   ├── models.py              # Pydantic models
│   ├── mcp_client.py          # MCP client using FastMCP
│   ├── llm_service.py         # OpenAI LLM service
│   ├── agent.py               # Support agent with tool calling
│   └── api/
│       ├── __init__.py
│       └── routes.py          # API routes
├── static/
│   └── index.html             # Simple chat UI
├── main.py                    # Application entry point
├── requirements.txt
├── Dockerfile
├── render.yaml
└── .env
```

---

## Environment Variables

```env
# OpenRouter API Configuration
OPENROUTER_API_KEY=sk-xxx
OPENROUTER_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4o-mini

# MCP Server (Company Product Data)
MCP_SERVER_URL=https://vipfapwm3x.us-east-1.awsapprunner.com/mcp

# Server Configuration
HOST=0.0.0.0
PORT=8000

# LLM Parameters
TEMPERATURE=0.7
MAX_TOKENS=700
```

---

## API Endpoints

### `GET /ping`
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "mcp_connected": true,
  "llm_configured": true
}
```

### `POST /v1/chat`
Chat endpoint for customer support.

**Request:**
```json
{
  "message": "Do you have any 27-inch monitors available?"
}
```

**Response:**
```json
{
  "response": "Yes, we have several 27-inch monitors available...",
  "tool_calls": [
    {
      "name": "search_products",
      "arguments": {"category": "monitors", "size": "27"}
    }
  ]
}
```

### `GET /`
Serve the chat UI HTML page.

---

## Components

### 1. Configuration (`app/config.py`)
- Load environment variables using `pydantic-settings`
- Validate required settings

### 2. Models (`app/models.py`)
- `ChatRequest`: Incoming chat message
- `ChatResponse`: Agent response with optional tool calls
- `HealthResponse`: Health check status

### 3. MCP Client (`app/mcp_client.py`)
- Connect to company MCP server via Streamable HTTP
- List available tools
- Execute tool calls
- Uses `mcp.client.streamable_http` from FastMCP SDK

### 4. LLM Service (`app/llm_service.py`)
- OpenAI client wrapper
- Support for chat completions
- Tool calling integration

### 5. Support Agent (`app/agent.py`)
- Orchestrates LLM + MCP tools
- System prompt for customer support
- Handles tool call execution flow

### 6. API Routes (`app/api/routes.py`)
- `/ping` - Health check
- `/v1/chat` - Chat endpoint
- `/` - Serve static UI

### 7. Chat UI (`static/index.html`)
- Simple HTML/CSS/JS chat interface
- WebSocket or polling for real-time updates
- Responsive design

---

## Flow Diagram

```
User → Web UI → FastAPI (/v1/chat)
                      ↓
                 Support Agent
                      ↓
          ┌──────────┴──────────┐
          ↓                      ↓
    OpenAI GPT-4o-mini      MCP Server
    (with tool schema)     (product data)
          ↓                      ↓
          └──────────┬──────────┘
                     ↓
              Tool calls executed
                     ↓
              Final response to user
```

---

## Implementation Steps

1. Set up project structure
2. Create `requirements.txt`
3. Create configuration module
4. Create Pydantic models
5. Create MCP client (FastMCP)
6. Create LLM service
7. Create support agent
8. Create FastAPI routes
9. Create simple HTML chat UI
10. Create main.py
11. Create Dockerfile
12. Create Render deployment config
13. Test locally
14. Deploy to Render

---

## References

- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP Documentation](https://gofastmcp.com/)
- [OpenAI API](https://platform.openai.com/docs)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Render Deployment](https://render.com/docs)
