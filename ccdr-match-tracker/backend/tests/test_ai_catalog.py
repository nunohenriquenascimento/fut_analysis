"""Public descriptors are derived from dispatch, never from runtime identity."""
import json
from typing import get_args

import pytest
from pydantic import ValidationError

from app.ai import catalog, executor, registry
from app.ai.schemas import MatchStatisticsInput, ToolCatalogEntry, ToolName


def test_catalog_matches_ollama_structure_and_pydantic_parameters():
    entry, = catalog.get_tool_catalog()
    assert set(entry) == {"type", "function"} and entry["type"] == "function"
    function = entry["function"]
    assert set(function) == {"name", "description", "parameters"}
    assert function["name"] == "get_match_statistics" and function["description"]
    assert function["parameters"] == {
        "type": "object", "additionalProperties": False, "required": ["match_id"],
        "properties": {"match_id": {"type": "integer", "exclusiveMinimum": 0, "maximum": 2_147_483_647}},
    }
    derived = MatchStatisticsInput.model_json_schema()
    assert function["parameters"]["properties"]["match_id"] == {
        key: value for key, value in derived["properties"]["match_id"].items() if key != "title"
    }
    assert ToolCatalogEntry.model_validate(entry).model_dump(mode="json") == entry
    assert json.loads(json.dumps([entry], ensure_ascii=False)) == [entry]


def test_catalog_and_executor_share_one_registry():
    assert catalog.TOOLS is registry.TOOLS is executor._TOOLS
    assert {entry["function"]["name"] for entry in catalog.get_tool_catalog()} == set(registry.TOOLS)
    assert set(get_args(ToolName)) == set(registry.TOOLS) == {"get_match_statistics"}
    assert registry.TOOLS["get_match_statistics"].arguments_schema is MatchStatisticsInput


def test_catalog_is_static_and_contains_only_public_arguments(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Catalogue generation must not authenticate or connect to a database")

    monkeypatch.setattr(executor, "resolve_match_context", forbidden)
    entries = catalog.get_tool_catalog()
    properties = entries[0]["function"]["parameters"]["properties"]
    assert set(properties) == {"match_id"}
    encoded = json.dumps(entries)
    for private in ["engine", "request", "context", "role", "permissions", "team_id", "season_id",
                    "password", "token", "DATABASE_URL", "app.", "MatchStatisticsInput"]:
        assert private not in encoded


def test_mutating_catalog_cannot_change_registry_or_executor_validation(monkeypatch):
    original = catalog.get_tool_catalog()
    changed = catalog.get_tool_catalog()
    changed[0]["function"]["parameters"]["properties"]["match_id"]["exclusiveMinimum"] = -100
    changed[0]["function"]["parameters"]["properties"]["engine"] = {"type": "string"}
    changed[0]["function"]["parameters"]["additionalProperties"] = True
    changed[0]["function"]["parameters"]["required"].clear()
    changed[0]["function"]["name"] = "delete_match"
    changed.append({"type": "function", "function": {"name": "execute_sql"}})
    assert catalog.get_tool_catalog() == original

    def forbidden(*args, **kwargs):
        pytest.fail("Modified descriptions must not grant execution")

    monkeypatch.setattr(executor, "resolve_match_context", forbidden)
    for name, arguments, code in [
        ("delete_match", {"match_id": 1}, "UNKNOWN_TOOL"),
        ("get_match_statistics", {"match_id": -1}, "INVALID_ARGUMENTS"),
        ("get_match_statistics", {"match_id": 1, "engine": "private"}, "INVALID_ARGUMENTS"),
    ]:
        result = executor.execute_tool(name, arguments, request=None, engine=None)
        assert result.status == "error" and result.error.code == code


def test_catalog_descriptor_rejects_unknown_names_and_additional_fields():
    entry = catalog.get_tool_catalog()[0]
    with pytest.raises(ValidationError):
        ToolCatalogEntry.model_validate({**entry, "engine": "private"})
    with pytest.raises(ValidationError):
        ToolCatalogEntry.model_validate({"function": {**entry["function"], "name": "execute_sql"}})
