"""
MCP Tool definitions for Perplexity.

Two tools:
- perplexity_ask: Pro search + reasoning (auto-detected from model name)
- perplexity_research: Deep research mode

Tool descriptions are optimized for LLM agents.
"""

from mcp.types import Tool

from perplexity.config import COUNCIL_MODELS, MODEL_MAPPINGS, SEARCH_SOURCES, SOURCE_LABELS

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


def _council_description() -> str:
    """Generate council models description from COUNCIL_MODELS."""
    names = sorted(COUNCIL_MODELS.keys())
    return (
        f"Models for council consensus (1-3). Available: {', '.join(names)}. "
        "Each model object needs 'name' and optional 'thinking' (boolean, default true). "
        "Example: [{\"name\": \"gpt-5.4\", \"thinking\": true}, {\"name\": \"claude-4.6-opus\", \"thinking\": true}, {\"name\": \"gemini-3.1-pro\"}]"
    )


def _sources_description() -> str:
    """Generate sources description dynamically from config."""
    labels = [f"{v} ({k})" for k, v in SOURCE_LABELS.items()]
    return (
        f"Information sources. Available: {', '.join(labels)}. "
        "Connector sources (GitHub, Linear, Google Drive) require OAuth setup in Perplexity. "
        "Premium sources (Wiley, CB Insights, Statista, PitchBook) require Max subscription."
    )


def resolve_council_models(models_input: list) -> list:
    """Resolve council model selections to internal Perplexity names."""
    result = []
    for m in models_input[:3]:  # max 3
        name = m.get("name") if isinstance(m, dict) else m
        thinking = m.get("thinking", True) if isinstance(m, dict) else True
        if name in COUNCIL_MODELS:
            variant = "thinking" if thinking else "default"
            result.append(COUNCIL_MODELS[name][variant])
    return result


def get_mode_for_tool(name: str, model: str = None) -> str:
    """Determine the Perplexity search mode from tool name and model."""
    if name == "perplexity_research":
        return "deep research"
    if name == "perplexity_council":
        return "model council"
    if not model:
        return "pro"
    # Fast path: keyword detection for thinking/reasoning models
    if any(kw in model for kw in _REASONING_KEYWORDS):
        return "reasoning"
    # Fallback: find which mode actually contains this model
    for mode_name, mapping in MODEL_MAPPINGS.items():
        if model in mapping and mode_name != "auto":
            return mode_name
    return "pro"


# Default sources per tool
TOOL_DEFAULT_SOURCES = {
    "perplexity_ask": ["web"],
    "perplexity_research": ["web", "scholar"],
    "perplexity_council": ["web"],
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
                    "items": {"type": "string", "enum": SEARCH_SOURCES},
                    "description": _sources_description()
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
                    "items": {"type": "string", "enum": SEARCH_SOURCES},
                    "description": _sources_description()
                },
                "language": {
                    "type": "string",
                    "description": "ISO 639 language code. Default: 'en-US'"
                }
            },
            "required": ["query"]
        }
    ),
    Tool(
        name="perplexity_council",
        description=(
            "Model Council — runs the same query across multiple AI models (up to 3) and synthesizes "
            "a consensus answer. Each model can optionally use reasoning/thinking mode. "
            "Use for important decisions where you want cross-model validation, or to compare "
            "how different models approach a problem."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Question to send to the model council. Be specific — all selected models "
                        "will independently analyze this query and a consensus will be synthesized."
                    )
                },
                "models": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "thinking": {"type": "boolean", "default": True}
                        },
                        "required": ["name"]
                    },
                    "minItems": 1,
                    "maxItems": 3,
                    "description": _council_description()
                },
                "sources": {
                    "type": "array",
                    "items": {"type": "string", "enum": SEARCH_SOURCES},
                    "description": _sources_description()
                },
                "language": {
                    "type": "string",
                    "description": "ISO 639 language code. Default: 'en-US'"
                }
            },
            "required": ["query", "models"]
        }
    ),
]
