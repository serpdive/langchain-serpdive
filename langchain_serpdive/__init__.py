"""LangChain integration for SERPdive, the AI Search API.

Quickstart::

    from langchain_serpdive import SerpdiveSearch

    tool = SerpdiveSearch()  # reads SERPDIVE_API_KEY
    tool.invoke({"query": "latest developments in solid state batteries"})
"""

from .tools import SerpdiveInput, SerpdiveSearch

__version__ = "0.1.0"

# The brand is written SERPdive: any reasonable guess at the name imports fine.
SERPdiveSearch = SerpdiveSearch

__all__ = ["SerpdiveSearch", "SerpdiveInput", "SERPdiveSearch", "__version__"]
