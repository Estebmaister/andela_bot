from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., description="User message")


class ToolCall(BaseModel):
    """Model for a tool call made by the agent."""
    name: str = Field(..., description="Tool function name")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="Agent response message")
    tool_calls: Optional[List[ToolCall]] = Field(default=None, description="Tool calls made")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Service status")
    mcp_connected: bool = Field(..., description="MCP server connection status")
    llm_configured: bool = Field(..., description="LLM configuration status")
