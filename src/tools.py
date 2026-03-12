"""
MCP Tool definitions for Perplexity.

Two tools:
- perplexity_ask: Pro search + reasoning (auto-detected from model name)
- perplexity_research: Deep research mode

Tool descriptions are optimized for LLM agents.
"""

from mcp.types import Tool

from perplexity.config import MODEL_MAPPINGS

# Reasoning model keywords — if model name contains these, use reasoning mode
_REASONING_KEYWORDS = ("thinking", "reasoning")


def _model_description() -> str:
    """Generate model description dynamically from MODEL_MAPPINGS."""
    all_models = sorted({
        name
        for models in MODEL_MAPPINGS.values()
        for name in models
        if name is not None
    })
    return (
        f"Optional model selection. Available: {', '.join(all_models)}. "
        "Leave empty for default. "
        "Models with 'thinking'/'reasoning' in the name automatically use reasoning mode."
    )


def get_mode_for_tool(name: str, model: str = None) -> str:
    """Determine the Perplexity search mode from tool name and model."""
    if name == "perplexity_research":
        return "deep research"
    # perplexity_ask — auto-detect reasoning mode from model name
    if model and any(kw in model for kw in _REASONING_KEYWORDS):
        return "reasoning"
    return "pro"


# Default sources per tool
TOOL_DEFAULT_SOURCES = {
    "perplexity_ask": ["web"],
    "perplexity_research": ["web", "scholar"],
}

# Tool definitions for MCP server
TOOLS = [
    Tool(
        name="perplexity_ask",
        description=(
            "AI-powered answer engine for tech questions, documentation lookups, and how-to guides. "
            "Perplexity is an AI model (not a search engine) - provide context and specific requirements "
            "in your query for better results. Returns synthesized answers with citations."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Natural language question with context. Include specific requirements, "
                        "constraints, or use case. Example: 'How to implement JWT auth in Next.js 14 "
                        "App Router with httpOnly cookies for a SaaS app?'"
                    )
                },
                "sources": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["web", "scholar", "social"]},
                    "description": "Information sources to search. Default: ['web']"
                },
                "language": {
                    "type": "string",
                    "description": "ISO 639 language code. Default: 'en-US'"
                },
                "model": {
                    "type": "string",
                    "description": _model_description()
                }
            },
            "required": ["query"]
        }
    ),
    Tool(
        name="perplexity_research",
        description=(
            "Deep research agent for comprehensive analysis of complex topics. "
            "Provide detailed context about what you need and why - this AI model spends more time "
            "gathering and synthesizing information. Returns extensive reports with 10-30+ citations. "
            "Use for architecture decisions, technology comparisons, or thorough investigations."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Detailed research question with full context. Explain the problem, "
                        "constraints, and what insights you need. Example: 'Best practices for "
                        "LLM API key rotation in production Node.js apps - need patterns for "
                        "zero-downtime rotation, secret storage options, and monitoring.'"
                    )
                },
                "sources": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["web", "scholar", "social"]},
                    "description": "Information sources. Default: ['web', 'scholar']"
                },
                "language": {
                    "type": "string",
                    "description": "ISO 639 language code. Default: 'en-US'"
                }
            },
            "required": ["query"]
        }
    ),
]
