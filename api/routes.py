import logging
from typing import Dict
from pathlib import Path
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse

from app.models import ChatRequest, ChatResponse, HealthResponse
from app.agent import get_support_agent
from app.mcp_client import get_mcp_client
from app.llm_service import get_llm_service
from app.prompt_loader import (
    get_welcome_title,
    get_welcome_subtitle,
    get_welcome_features,
)

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
async def chat(request: ChatRequest, http_request: Request):
    """Chat endpoint for customer support."""
    try:
        # Extract client IP for conversation tracking
        client_ip = http_request.client.host
        agent = get_support_agent()
        response = await agent.chat(
            user_message=request.message,
            user_identifier=client_ip,
            remember=request.remember,
            clear_history=request.clear_history,
        )
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


@router.get("/static/style.css")
async def serve_style_css():
    """Serve the CSS stylesheet."""
    css_path = Path("static/style.css")
    if not css_path.exists():
        raise HTTPException(status_code=404, detail="CSS file not found")
    return FileResponse(css_path, media_type="text/css")


@router.get("/v1/prompts/welcome")
async def get_welcome_prompts() -> Dict[str, str]:
    """Get welcome message prompts for the UI."""
    return {
        "title": get_welcome_title(),
        "subtitle": get_welcome_subtitle(),
        "features": get_welcome_features(),
    }
