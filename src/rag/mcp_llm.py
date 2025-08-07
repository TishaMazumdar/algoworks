from langchain_core.language_models.llms import LLM
from pydantic import Field
from typing import Optional, List
import requests

class McpLLM(LLM):
    model: str = Field(default="mistral")
    mcp_url: str = Field(default="http://localhost:11434/api/chat")
    temperature: float = Field(default=0.7)

    @property
    def _llm_type(self) -> str:
        return "mcp-llm"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Only use the provided context. Do not hallucinate."},
            {"role": "user", "content": prompt}
        ]

        try:
            response = requests.post(self.mcp_url, json={
                "model": self.model,
                "messages": messages,
                "stream": False
            })
            response.raise_for_status()
            result = response.json()
            return result.get("message", {}).get("content", "No response.")
        except requests.exceptions.ConnectionError:
            return f"Error: Cannot connect to MCP server at {self.mcp_url}. Please ensure the server is running."
        except requests.exceptions.RequestException as e:
            return f"Error: {str(e)}"