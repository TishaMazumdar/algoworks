from datetime import datetime
import json
import os

CACHE_FILE = os.path.join("src", "models", "cache.json")
MAX_CACHE_SIZE = 6

class ChatEntry:
    def __init__(self, question: str, answer: str, sources: list[str], timestamp: str = None):
        self.question = question
        self.answer = answer
        self.sources = sources
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self):
        return {
            "question": self.question,
            "answer": self.answer,
            "sources": self.sources,
            "timestamp": self.timestamp
        }

    @staticmethod
    def from_dict(data: dict):
        return ChatEntry(
            question=data["question"],
            answer=data["answer"],
            sources=data.get("sources", []),
            timestamp=data.get("timestamp")
        )

# ---------- Caching Functions ----------

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            try:
                data = json.load(f)
                return [ChatEntry.from_dict(entry) for entry in data]
            except json.JSONDecodeError:
                return []
    return []

def get_all_cached_entries():
    return [ChatEntry.from_dict(entry) for entry in load_cache()]

def get_from_cache(question: str):
    question_lower = question.strip().lower()
    for entry in get_all_cached_entries():
        if entry.question.strip().lower() == question_lower:
            return entry
    return None

def save_cache(entry: ChatEntry):
    data = load_cache()  # Returns List[ChatEntry]

    # Avoid duplicates
    if any(e.question.strip().lower() == entry.question.strip().lower() for e in data):
        return

    data.append(entry)

    with open(CACHE_FILE, "w") as f:
        json.dump([e.to_dict() for e in data], f, indent=2)

def clear_cache():
    with open(CACHE_FILE, "w") as f:
        json.dump([], f)