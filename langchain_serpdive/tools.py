"""LangChain tool for SERPdive, the AI Search API."""

from __future__ import annotations

from typing import Any, Dict, Optional, Type

from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr
from serpdive import AsyncSerpDive, SearchResponse, SerpDive


class SerpdiveInput(BaseModel):
    """Input schema for the SERPdive search tool."""

    query: str = Field(
        description="The search query, in any language, phrased like a real web search."
    )


class SerpdiveSearch(BaseTool):
    """Web search that returns extracted, answer-ready page content.

    Every result carries the actual text of the page (url, title, date,
    content), already cleaned and sized for LLM consumption, so agents can
    quote and cite straight from the tool output.

    Setup:
        Install ``langchain-serpdive`` and set the ``SERPDIVE_API_KEY``
        environment variable (free key at https://serpdive.com/dashboard/keys).

        .. code-block:: bash

            pip install langchain-serpdive
            export SERPDIVE_API_KEY="sd_live_..."

    Instantiate:
        .. code-block:: python

            from langchain_serpdive import SerpdiveSearch

            tool = SerpdiveSearch(
                # model="krill",     # free and unlimited (fair use)
                # model="moby",      # full page text, for deep research
                # answer=True,       # also return a synthesized answer
                # max_results=5,     # hard cap on delivered results, 1-10
            )

    Invoke directly:
        .. code-block:: python

            tool.invoke({"query": "latest developments in solid state batteries"})

    Use within an agent: pass ``[tool]`` as the tools list of any LangChain
    or LangGraph agent; the tool description tells the model when to call it.
    """

    name: str = "serpdive_search"
    description: str = (
        "Search the live web and get back answer-ready page content, not a list "
        "of links. Each result carries the actual text of the page (url, title, "
        "date, content), already extracted and cleaned, so facts can be quoted "
        "and cited straight from the response. Use it for anything that needs "
        "current or post-training information: news, prices, releases, docs, "
        "niche facts. Write the query the way a person would type it, in any "
        "language: localization is automatic."
    )
    args_schema: Type[BaseModel] = SerpdiveInput

    model: str = "mako"
    """Retrieval depth: "mako" (default) returns the fact-carrying sentences of
    each page, fast; "krill" is the free tier — unlimited under fair use, the
    smallest useful payload, one request at a time, at low priority; "moby"
    returns the full readable text, for deep research."""

    answer: bool = False
    """When True, the output also carries an "answer" field: a direct answer
    synthesized from the sources (concise on mako, cited on moby). Not
    available on krill, which returns sources only."""

    max_results: Optional[int] = None
    """Hard cap on delivered results (1-10). None lets the engine pick its
    calibrated mix."""

    api_key: Optional[str] = None
    """SERPdive API key. Defaults to the SERPDIVE_API_KEY environment variable."""

    _client: Optional[SerpDive] = PrivateAttr(default=None)
    _async_client: Optional[AsyncSerpDive] = PrivateAttr(default=None)

    def _payload(self, response: SearchResponse) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "query": response.query,
            "results": [
                {
                    "url": result.url,
                    "title": result.title,
                    **({"date": result.date} if result.date else {}),
                    "content": result.content,
                }
                for result in response.results
            ],
        }
        if response.answer is not None:
            payload["answer"] = response.answer
        if response.extra_info is not None:
            payload["extra_info"] = response.extra_info
        return payload

    def _search_kwargs(self) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {"model": self.model}
        if self.answer:
            kwargs["answer"] = True
        if self.max_results is not None:
            kwargs["max_results"] = self.max_results
        return kwargs

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Dict[str, Any]:
        if self._client is None:
            self._client = SerpDive(api_key=self.api_key)
        return self._payload(self._client.search(query, **self._search_kwargs()))

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> Dict[str, Any]:
        if self._async_client is None:
            self._async_client = AsyncSerpDive(api_key=self.api_key)
        return self._payload(
            await self._async_client.search(query, **self._search_kwargs())
        )
