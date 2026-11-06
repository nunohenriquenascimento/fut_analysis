"""Fresh, validated JSON descriptions; this catalogue never grants access."""
from typing import Any

from app.ai.registry import TOOLS
from app.ai.schemas import ToolCatalogEntry, ToolCatalogFunction


def get_tool_catalog() -> list[dict[str, Any]]:
    """Return Ollama-compatible descriptors, without server-only dependencies.

    JSON Schema is generated from the exact argument models used by dispatch.
    Root class names/docstrings and property titles are implementation annotations,
    so they are omitted. A fresh tree is returned on every call: mutating it
    cannot modify the registry, argument validation or subsequent catalogues.
    """
    catalog = []
    for name, definition in TOOLS.items():
        parameters = definition.arguments_schema.model_json_schema()
        parameters.pop("title", None)
        parameters.pop("description", None)
        for parameter in parameters.get("properties", {}).values():
            parameter.pop("title", None)
        entry = ToolCatalogEntry(function=ToolCatalogFunction(
            name=name, description=definition.description, parameters=parameters,
        ))
        catalog.append(entry.model_dump(mode="json"))
    return catalog
