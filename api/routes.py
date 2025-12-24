import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, FileResponse

from app.models import ChatRequest, ChatResponse, HealthResponse
from app.agent import get_support_agent
from app.mcp_client import get_mcp_client
from app.llm_service import get_llm_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/ping", response_model=HealthResponse)
async def ping():
    """Health check endpoint."""
    mcp_client = get_mcp_client()
    llm_service = get_llm_service()

    # Check MCP connection
    mcp_connected = await mcp_client.health_check()

    # Check LLM configuration (simple check - API key presence)
    llm_configured = bool(llm_service.client.api_key)

    return HealthResponse(
        status="ok",
        mcp_connected=mcp_connected,
        llm_configured=llm_configured,
    )


@router.post("/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint for customer support."""
    try:
        agent = get_support_agent()
        response = await agent.chat(request.message)
        return response
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_class=HTMLResponse)
async def serve_chat_ui():
    """Serve the chat UI HTML page."""
    try:
        with open("static/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Chat UI not found")
