import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Base path for prompts
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def load_prompt(name: str, default: str = "") -> str:
    """Load a prompt from the prompts directory.

    Args:
        name: Name of the prompt file (with or without extension)
        default: Default value to return if file not found

    Returns:
        The prompt content as a string
    """
    # Try with .md extension first
    prompt_path = PROMPTS_DIR / f"{name}.md"
    if not prompt_path.exists():
        # Try with .txt extension
        prompt_path = PROMPTS_DIR / f"{name}.txt"
    if not prompt_path.exists():
        # Try without extension
        prompt_path = PROMPTS_DIR / name

    try:
        content = prompt_path.read_text(encoding="utf-8").strip()
        logger.debug(f"Loaded prompt from {prompt_path}")
        return content
    except FileNotFoundError:
        logger.warning(f"Prompt file not found: {prompt_path}, using default")
        return default
    except Exception as e:
        logger.error(f"Error loading prompt from {prompt_path}: {e}")
        return default


def get_support_agent_prompt() -> str:
    """Get the support agent system prompt."""
    return load_prompt(
        "support_agent",
        default="You are a helpful customer support agent.",
    )


def get_welcome_title() -> str:
    """Get the welcome message title."""
    return load_prompt("welcome_title", default="Hi there! 👋")


def get_welcome_subtitle() -> str:
    """Get the welcome message subtitle."""
    return load_prompt(
        "welcome_subtitle",
        default="I'm your customer support assistant.",
    )


def get_welcome_features() -> str:
    """Get the welcome message features text."""
    return load_prompt(
        "welcome_features",
        default="Finding products, checking prices, and more.",
    )
