"""LangChain integration for SERPdive, the AI Search API.

Quickstart::

    from langchain_serpdive import SerpdiveSearch

    tool = SerpdiveSearch()  # reads SERPDIVE_API_KEY
    tool.invoke({"query": "latest developments in solid state batteries"})
"""

from .tools import SerpdiveInput, SerpdiveSearch

from importlib.metadata import PackageNotFoundError, version as _pkg_version

try:  # single source of truth: the installed distribution
    __version__ = _pkg_version("langchain-serpdive")
except PackageNotFoundError:  # running from a source tree, not installed
    __version__ = "0.0.0.dev0"

# The brand is written SERPdive: any reasonable guess at the name imports fine.
SERPdiveSearch = SerpdiveSearch

__all__ = ["SerpdiveSearch", "SerpdiveInput", "SERPdiveSearch", "__version__"]
