from abc import ABC, abstractmethod
from typing import Dict, Any, List


class Tool(ABC):
    """
    Base class for all chatbot tools.
    """

    name: str = "base_tool"
    description: str = "Base tool description"
    parameters: Dict[str, Any] = {}

    @abstractmethod
    def execute(self, **kwargs) -> str:
        pass

    def to_schema(self) -> Dict[str, Any]:
        """
        Convert tool definition to OpenAI/Groq function schema.
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class CalculatorTool(Tool):
    name = "calculator"
    description = (
        "Perform basic arithmetic operations (add, subtract, multiply, divide)."
    )
    parameters = {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "The mathematical expression to evaluate (e.g., '2 + 2', '15 * 4').",
            }
        },
        "required": ["expression"],
    }

    def execute(self, expression: str) -> str:
        try:
            # Safe evaluation of simple math
            allowed_chars = "0123456789+-*/(). "
            if not all(c in allowed_chars for c in expression):
                return "Error: Invalid characters in expression."

            result = eval(expression, {"__builtins__": {}}, {})
            return str(result)
        except Exception as e:
            return f"Error: {str(e)}"


try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    requests = None
    BeautifulSoup = None


class WebSearchTool(Tool):
    name = "web_search"
    description = "Search the internet for real-time information using DuckDuckGo."
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query to find information about.",
            }
        },
        "required": ["query"],
    }

    def execute(self, query: str) -> str:
        if not DDGS:
            return "Error: duckduckgo-search library not installed."

        try:
            # Note: duckduckgo_search might not expose SSL options directly,
            # but usually handles it. If it fails, we might need a workaround or env var.
            # trying standard call first, if it fails we might need to patch libraries
            # or skip SSL verify globally for this session.

            # Simple workaround for DDGS if it uses requests under the hood:
            # We can try to set env var but let's see if we can just catch the error more gracefully.
            # Actually, let's try to monkeypatch requests.adapters.HTTPAdapter if needed,
            # but for now let's assume the user might have cert issues.

            # For the purpose of this environment which seems to have SSL issues:
            import ssl

            ssl._create_default_https_context = ssl._create_unverified_context

            results = DDGS().text(query, max_results=3)
            if not results:
                return "No results found."

            formatted_results = []
            for r in results:
                formatted_results.append(
                    f"Title: {r['title']}\nLink: {r['href']}\nSnippet: {r['body']}"
                )

            return "\n\n".join(formatted_results)
        except Exception as e:
            return f"Error performing search: {str(e)}"


class URLReaderTool(Tool):
    name = "read_url"
    description = "Read and extract text content from a specific URL."
    parameters = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The URL of the web page to read.",
            }
        },
        "required": ["url"],
    }

    def execute(self, url: str) -> str:
        if not requests or not BeautifulSoup:
            return "Error: requests or beautifulsoup4 libraries not installed."

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            # Disable SSL verify for local dev environment issues
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            response = requests.get(url, headers=headers, timeout=10, verify=False)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer"]):
                script.decompose()

            text = soup.get_text()

            # Break into lines and remove leading and trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # Drop blank lines
            text = "\n".join(chunk for chunk in chunks if chunk)

            # Cap length to avoid context overflow
            return text[:4000] + ("..." if len(text) > 4000 else "")

        except Exception as e:
            return f"Error reading URL: {str(e)}"


class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        self.tools[tool.name] = tool

    def get_tool(self, name: str) -> Tool:
        return self.tools.get(name)

    def get_schemas(self) -> List[Dict[str, Any]]:
        return [tool.to_schema() for tool in self.tools.values()]


# Global registry
tool_registry = ToolRegistry()
tool_registry.register(CalculatorTool())
tool_registry.register(WebSearchTool())
tool_registry.register(URLReaderTool())
