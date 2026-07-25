# langchain-serpdive

The official [LangChain](https://python.langchain.com) integration for [SERPdive](https://serpdive.com), the AI Search API: your agent asks a question, the tool returns answer-ready web content that is extracted, cleaned, and sized for an LLM. On a [public, replayable 1,000-question benchmark](https://github.com/edendalexis/serpdive-benchmark), SERPdive runs at the same speed as Tavily, feeds your LLM 20.2% fewer tokens, and wins 60.7% of decided quality duels.

**There is a free tier, and it has no ceiling.** The `krill` model is free and unlimited under fair use — no card, no credits, nothing to decrement. It returns the shortest set of sentences that still answers (about 700 tokens a search, roughly half what the usual alternatives send), one request at a time, at low priority. Use it to build; switch one word to `mako` when you need depth and steady latency.

## Install

```bash
pip install langchain-serpdive
```

Get a free API key (no card required) at [serpdive.com/dashboard/keys](https://serpdive.com/dashboard/keys) and set it:

```bash
export SERPDIVE_API_KEY="sd_live_..."
```

## Use as a tool

```python
from langchain_serpdive import SerpdiveSearch

tool = SerpdiveSearch()
tool.invoke({"query": "latest developments in solid state batteries"})
```

The output is a lean dict your model can quote and cite directly:

```python
{
    "query": "latest developments in solid state batteries",
    "results": [
        {
            "url": "https://...",
            "title": "...",
            "date": "2026-07-11",
            "content": "The fact-carrying text of the page, extracted and cleaned...",
        },
        ...
    ],
}
```

## Use in an agent

```python
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langchain_serpdive import SerpdiveSearch

agent = create_react_agent(
    init_chat_model("claude-sonnet-5"),
    tools=[SerpdiveSearch()],
)
agent.invoke({"messages": [("user", "What changed in the EU AI Act this month?")]})
```

## Options

```python
SerpdiveSearch(
    model="moby",     # "mako" (default): key sentences, fast. "moby": full page text, deep research
    answer=True,      # also return a direct answer synthesized from the sources
    max_results=5,    # hard cap on delivered results, 1-10
    api_key="sd_live_...",  # defaults to SERPDIVE_API_KEY
)
```

Localization is automatic: the language of the query picks where we search. There is no country parameter to configure. Failed searches are never billed.

## Links

- [API reference](https://serpdive.com/docs)
- [Public benchmark](https://github.com/edendalexis/serpdive-benchmark) (replayable end to end: same questions, same judge, your machine)
- [Python SDK](https://github.com/serpdive/serpdive-python) (this package is a thin layer over it)
- [MCP server](https://github.com/serpdive/serpdive-mcp) for Claude, Cursor and other MCP clients

## License

MIT
