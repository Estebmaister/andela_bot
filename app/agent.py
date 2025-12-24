import json
import logging
import re
from typing import Any, Optional

from app.models import ChatResponse, ToolCall
from app.llm_service import get_llm_service
from app.mcp_client import get_mcp_client
from app.prompt_loader import get_support_agent_prompt
from app.conversation_store import get_conversation_store

logger = logging.getLogger(__name__)

# Pattern to detect "remember" phrase in user messages
REMEMBER_PHRASE_PATTERN = re.compile(
    r'\bremember\b',
    re.IGNORECASE
)


class SupportAgent:
    """Customer support agent with MCP tool calling capabilities."""

    # Default number of messages to include in context
    DEFAULT_HISTORY_LIMIT = 10

    def __init__(self):
        self.llm_service = get_llm_service()
        self.mcp_client = get_mcp_client()
        self._available_tools: Optional[list[dict]] = None
        self._system_prompt: Optional[str] = None

    def get_system_prompt(self) -> str:
        """Get the system prompt, loading from file if not cached."""
        if self._system_prompt is None:
            self._system_prompt = get_support_agent_prompt()
        return self._system_prompt

    async def get_available_tools(self) -> list[dict]:
        """Get available tools from MCP server, formatted for OpenAI."""
        if self._available_tools is None:
            self._available_tools = await self.mcp_client.list_tools()
            logger.info(f"Loaded {len(self._available_tools)} tools from MCP server")
        return self._available_tools

    def _should_use_full_history(self, message: str, remember_flag: bool) -> bool:
        """Determine if full conversation history should be used.

        Args:
            message: The user's message
            remember_flag: The remember flag from the request

        Returns:
            True if full history should be used
        """
        if remember_flag:
            return True
        # Check if message contains "remember" keyword
        return bool(REMEMBER_PHRASE_PATTERN.search(message))

    async def chat(
        self,
        user_message: str,
        user_identifier: str,
        remember: bool = False,
        clear_history: bool = False,
    ) -> ChatResponse:
        """Process a user message and return a response.

        Args:
            user_message: The user's message
            user_identifier: Unique identifier for the user (e.g., IP address)
            remember: If True, use full conversation history
            clear_history: If True, clear conversation history before processing
        """
        store = get_conversation_store()
        conversation = store.get_or_create_conversation(user_identifier)

        # Clear history if requested
        if clear_history:
            store.delete_conversation(user_identifier)
            conversation = store.get_or_create_conversation(user_identifier)
            logger.info(f"Cleared conversation history for {user_identifier}")

        # Add user message to conversation history
        conversation.add_message("user", user_message)

        # Determine history limit
        use_full_history = self._should_use_full_history(user_message, remember)
        history_limit = None if use_full_history else self.DEFAULT_HISTORY_LIMIT

        # Get conversation history
        history = conversation.get_history(limit=history_limit, include_all=use_full_history)
        logger.info(
            f"User {user_identifier}: using {len(history)} messages "
            f"({'all' if use_full_history else f'last {history_limit}'})"
        )

        # Build messages with system prompt and history
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            *history,  # Include conversation history
        ]

        # Get available tools
        tools = await self.get_available_tools()

        # Get LLM response
        llm_response = await self.llm_service.chat(messages, tools=tools)
        assistant_message = llm_response.choices[0].message

        # Track tool calls
        tool_calls_data: list[ToolCall] = []

        # Handle tool calls if present
        if assistant_message.tool_calls:
            # Build tool calls for the assistant message
            tool_calls_for_message = []
            for tool_call in assistant_message.tool_calls:
                tool_calls_for_message.append({
                    "id": tool_call.id,
                    "type": tool_call.type,
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    },
                })

            # Add assistant message with tool_calls to history
            messages.append({
                "role": "assistant",
                "content": assistant_message.content or "",
                "tool_calls": tool_calls_for_message,
            })

            # Execute each tool call and collect results
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                try:
                    function_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    function_args = {}

                logger.info(f"Executing tool: {function_name} with args: {function_args}")

                # Record the tool call
                tool_calls_data.append(ToolCall(
                    name=function_name,
                    arguments=function_args,
                ))

                # Execute the tool via MCP
                result = await self.mcp_client.call_tool(function_name, function_args)

                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })

            # Get final response with tool results
            final_response = await self.llm_service.chat(messages, tools=tools)
            final_message = final_response.choices[0].message

            # Save assistant response to conversation
            conversation.add_message("assistant", final_message.content or "")

            return ChatResponse(
                response=final_message.content or "I apologize, but I couldn't generate a response.",
                tool_calls=tool_calls_data if tool_calls_data else None,
            )

        # No tool calls, return direct response
        # Save assistant response to conversation
        conversation.add_message("assistant", assistant_message.content or "")

        return ChatResponse(
            response=assistant_message.content or "I apologize, but I couldn't generate a response.",
        )


# Global agent instance
_agent: Optional[SupportAgent] = None


def get_support_agent() -> SupportAgent:
    """Get or create the global support agent instance."""
    global _agent
    if _agent is None:
        _agent = SupportAgent()
    return _agent
