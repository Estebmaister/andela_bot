# Andela Bot - Customer Support Chatbot

A customer support chatbot that connects to an MCP (Model Context Protocol) server to access product data and generate augmented responses using an LLM.

## Features

- **MCP Integration**: Connects to MCP server for real-time product data access
- **Tool Calling**: LLM can call MCP tools to retrieve and act on data
- **Conversation History**: In-memory session management per user (IP-based)
- **Markdown Support**: Rich formatted responses with code highlighting
- **Simple UI**: Clean web interface for customer interactions

## Architecture

```
                    +-----------+
                    |   Browser |
                    +-----+-----+
                          | HTTP
                          v
                    +-----------+      +------------------+
                    |  FastAPI  |<---->| Conversation     |
                    |  Routes   |      | Store (In-Memory)|
                    +-----+-----+      +------------------+
                          |                  |
                    +-----+-----+            |
                    |   Agent   |<-----------+
                    +-----+-----+
                          |                  +------------------+
                    +-----+-----+            |   Prompt Loader  |
                    | LLM       |            |   (/prompts)     |
                    | Service   |            +------------------+
                    +-----+-----+
                          |
                    +-----+-----+            +------------------+
                    | MCP       |<-----------+   Configuration  |
                    | Client    |            |   (.env)         |
                    +-----------+            +------------------+
```

## Project Structure

```
andela_bot/
├── app/
│   ├── agent.py              # Main support agent with tool calling
│   ├── config.py             # Environment configuration
│   ├── conversation_store.py # In-memory conversation history
│   ├── llm_service.py        # OpenAI/OpenRouter LLM wrapper
│   ├── mcp_client.py         # MCP client implementation
│   ├── models.py             # Pydantic request/response models
│   └── prompt_loader.py      # Loads prompts from /prompts folder
├── api/
│   └── routes.py             # FastAPI route handlers
├── prompts/
│   ├── support_agent.md      # System prompt for the agent
│   ├── welcome_title.txt     # Welcome message title
│   ├── welcome_subtitle.txt  # Welcome message subtitle
│   └── welcome_features.txt  # Welcome message features list
├── static/
│   └── index.html            # Chat UI
├── main.py                   # Application entry point
├── requirements.txt          # Python dependencies
├── Dockerfile                # Container configuration
└── render.yaml               # Render deployment config
```

## Setup

### Prerequisites

- Python 3.12 (not 3.14+ due to pydantic-core compatibility)
- OpenRouter API key
- MCP server URL

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd andela_bot
   ```

2. **Create virtual environment**
   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create a `.env` file in the project root:
   ```env
   # Required: OpenRouter API Key
   OPENROUTER_API_KEY=your_openrouter_api_key_here

   # Optional: LLM Configuration
   OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
   MODEL_NAME=openai/gpt-4o-mini

   # Optional: MCP Server Configuration
   MCP_SERVER_URL=https://your-mcp-server.com/mcp

   # Optional: Server Configuration
   HOST=0.0.0.0
   PORT=8000

   # Optional: LLM Parameters
   TEMPERATURE=0.7
   MAX_TOKENS=700
   ```

5. **Run the server**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the chat UI**
   Open your browser to: `http://localhost:8000`

## Usage

### Chat Endpoint

**POST** `/v1/chat`

Submit a message to the support agent.

```json
{
  "message": "Do you have any monitors?",
  "remember": false,
  "clear_history": false
}
```

**Parameters:**
- `message` (string, required): User's message
- `remember` (boolean, optional): Use full conversation history instead of last 10 messages
- `clear_history` (boolean, optional): Clear conversation history before processing

**Response:**
```json
{
  "response": "Yes, we have several monitors available...",
  "tool_calls": [
    {
      "name": "search_products",
      "arguments": {"category": "monitors"}
    }
  ]
}
```

### Conversation History

The bot maintains conversation history per user (based on IP address):

- **Default Mode**: Last 10 messages are sent to the LLM
- **Remember Mode**: Full conversation history is sent to the LLM
  - Enable via the "Remember Mode" button in the UI
  - Automatically triggered when user says "remember" in their message
- **Clear History**: Resets the conversation for the current user
  - Click the "Clear History" button in the UI

### Health Check

**GET** `/ping`

Check service health and connectivity.

```json
{
  "status": "ok",
  "mcp_connected": true,
  "llm_configured": true
}
```

### Welcome Prompts

**GET** `/v1/prompts/welcome`

Get welcome message content for the UI.

```json
{
  "title": "Hi there!",
  "subtitle": "I'm your customer support assistant.",
  "features": "Finding products, checking prices, viewing orders, and more."
}
```

## Customization

### Prompts

Edit the files in the `/prompts` folder to customize the bot's behavior:

- `support_agent.md`: System prompt defining the agent's personality and behavior
- `welcome_title.txt`: Welcome message heading
- `welcome_subtitle.txt`: Welcome message subheading
- `welcome_features.txt`: List of capabilities shown in the welcome message

### Configuration

Edit `.env` file or use environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | OpenRouter API key | *Required* |
| `OPENROUTER_BASE_URL` | OpenRouter base URL | `https://openrouter.ai/api/v1` |
| `MODEL_NAME` | LLM model to use | `openai/gpt-4o-mini` |
| `MCP_SERVER_URL` | MCP server endpoint | `https://vipfapwm3x.us-east-1.awsapprunner.com/mcp` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `TEMPERATURE` | LLM temperature | `0.7` |
| `MAX_TOKENS` | LLM max tokens | `700` |

## Deployment

### Render

The project includes `render.yaml` for easy deployment to Render.

1. Push your code to a Git repository
2. Create a new Web Service on Render
3. Connect your repository
4. Render will automatically detect and use `render.yaml`
5. Set environment variables in the Render dashboard:
   - `OPENROUTER_API_KEY`
   - `MCP_SERVER_URL` (if different from default)

### Docker

Build and run using Docker:

```bash
docker build -t andela-bot .
docker run -p 8000:8000 --env-file .env andela-bot
```

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serve chat UI |
| GET | `/ping` | Health check |
| POST | `/v1/chat` | Send message to agent |
| GET | `/v1/prompts/welcome` | Get welcome prompts |

## 👤 Author & Support

Developed by [Esteban Camargo](https://github.com/estebmaister)

📧 **Email**: [estebmaister@gmail.com](mailto:estebmaister@gmail.com)
🌐 **LinkedIn**: [https://linkedin.com/in/estebmaister](https://linkedin.com/in/estebmaister)
🐙 **GitHub**: [https://github.com/estebmaister](https://github.com/estebmaister)

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
