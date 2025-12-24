import logging
from collections import deque
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """A message in the conversation."""
    role: str
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Conversation:
    """A conversation session for a user."""
    messages: deque[Message] = field(default_factory=lambda: deque(maxlen=50))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation."""
        self.messages.append(Message(role=role, content=content))
        self.last_activity = datetime.now(timezone.utc)

    def get_history(self, limit: Optional[int] = None, include_all: bool = False) -> List[Dict[str, str]]:
        """Get conversation history as a list of message dicts.

        Args:
            limit: Maximum number of recent messages to include (None for all)
            include_all: If True, include all messages ignoring limit

        Returns:
            List of message dictionaries with 'role' and 'content' keys
        """
        if include_all or limit is None:
            messages = list(self.messages)
        else:
            messages = list(self.messages)[-limit:]

        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

    def is_stale(self, timeout_minutes: int = 30) -> bool:
        """Check if the conversation is stale (no activity for timeout minutes)."""
        return datetime.now(timezone.utc) - self.last_activity > timedelta(minutes=timeout_minutes)


class ConversationStore:
    """In-memory store for user conversations keyed by IP address."""

    def __init__(self, max_conversations: int = 1000, stale_timeout_minutes: int = 30):
        self.conversations: Dict[str, Conversation] = {}
        self.max_conversations = max_conversations
        self.stale_timeout_minutes = stale_timeout_minutes

    def get_or_create_conversation(self, identifier: str) -> Conversation:
        """Get or create a conversation for the given identifier (IP)."""
        # Clean up stale conversations periodically
        if len(self.conversations) > self.max_conversations * 0.8:
            self._cleanup_stale()

        if identifier not in self.conversations:
            self.conversations[identifier] = Conversation()
            logger.debug(f"Created new conversation for {identifier}")

        return self.conversations[identifier]

    def get_conversation(self, identifier: str) -> Optional[Conversation]:
        """Get an existing conversation or None if not found."""
        return self.conversations.get(identifier)

    def delete_conversation(self, identifier: str) -> bool:
        """Delete a conversation. Returns True if it existed."""
        if identifier in self.conversations:
            del self.conversations[identifier]
            logger.debug(f"Deleted conversation for {identifier}")
            return True
        return False

    def _cleanup_stale(self) -> None:
        """Remove stale conversations to free memory."""
        stale_keys = [
            key for key, conv in self.conversations.items()
            if conv.is_stale(self.stale_timeout_minutes)
        ]
        for key in stale_keys:
            del self.conversations[key]
        if stale_keys:
            logger.info(f"Cleaned up {len(stale_keys)} stale conversations")

    def get_stats(self) -> Dict[str, int]:
        """Get statistics about the store."""
        return {
            "total_conversations": len(self.conversations),
            "max_conversations": self.max_conversations,
        }


# Global conversation store instance
_store: Optional[ConversationStore] = None


def get_conversation_store() -> ConversationStore:
    """Get or create the global conversation store instance."""
    global _store
    if _store is None:
        _store = ConversationStore()
    return _store
