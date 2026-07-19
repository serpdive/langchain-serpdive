"""Tool behavior against a stubbed SDK client: no network, no key."""

import asyncio
from typing import Any, Dict, Optional

import pytest
from serpdive import SearchResponse

from langchain_serpdive import SerpdiveSearch


class StubClient:
    """Records the call, returns a canned SearchResponse."""

    def __init__(self, payload: Dict[str, Any]):
        self.payload = payload
        self.calls = []

    def search(self, query: str, **kwargs: Any) -> SearchResponse:
        self.calls.append({"query": query, **kwargs})
        return SearchResponse.from_dict(self.payload)


class StubAsyncClient(StubClient):
    async def search(self, query: str, **kwargs: Any) -> SearchResponse:  # type: ignore[override]
        return StubClient.search(self, query, **kwargs)


PAYLOAD = {
    "query": "seine temperature",
    "model": "mako",
    "response_time_ms": 900,
    "results": [
        {"url": "https://a.example", "title": "T", "date": "2026-07-01", "content": "C1"},
        {"url": "https://b.example", "title": None, "content": "C2"},
    ],
}


def make_tool(payload: Dict[str, Any] = PAYLOAD, **kwargs: Any) -> SerpdiveSearch:
    tool = SerpdiveSearch(api_key="sd_live_TEST", **kwargs)
    tool._client = StubClient(payload)
    tool._async_client = StubAsyncClient(payload)
    return tool


def test_invoke_returns_lean_dict():
    tool = make_tool()
    out = tool.invoke({"query": "seine temperature"})
    assert out["query"] == "seine temperature"
    assert [r["url"] for r in out["results"]] == ["https://a.example", "https://b.example"]
    # date only when present, no None padding
    assert "date" in out["results"][0] and "date" not in out["results"][1]
    # answer/extra_info absent when the API did not ship them
    assert "answer" not in out and "extra_info" not in out


def test_constructor_params_travel_to_the_sdk():
    tool = make_tool(model="moby", answer=True, max_results=3)
    tool.invoke({"query": "q"})
    assert tool._client.calls == [
        {"query": "q", "model": "moby", "answer": True, "max_results": 3}
    ]


def test_answer_included_when_shipped():
    tool = make_tool({**PAYLOAD, "answer": "It is 21 degrees."})
    out = tool.invoke({"query": "q"})
    assert out["answer"] == "It is 21 degrees."


def test_async_path():
    tool = make_tool()
    out = asyncio.run(tool.ainvoke({"query": "async q"}))
    assert out["query"] == "seine temperature"
    assert len(out["results"]) == 2


def test_tool_contract_for_agents():
    tool = SerpdiveSearch(api_key="sd_live_TEST")
    assert tool.name == "serpdive_search"
    assert "query" in tool.args_schema.model_json_schema()["properties"]
    # the description is what the LLM reads: it must say WHAT comes back
    assert "page content" in tool.description


def test_default_model_is_mako():
    tool = make_tool()
    tool.invoke({"query": "q"})
    assert tool._client.calls[0]["model"] == "mako"
