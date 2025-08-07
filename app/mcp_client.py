import requests

MCP_URL = "http://localhost:11434/api/chat"  # Adjust if your MCP expects a different endpoint

def ask_mcp(question: str) -> dict:
    try:
        res = requests.post(MCP_URL, json={"question": question})
        res.raise_for_status()
        return res.json()  # should return dict with "answer" and optionally "sources"
    except Exception as e:
        print(f"[MCP ERROR] {e}")
        return {"answer": "Failed to get answer from MCP.", "sources": []}