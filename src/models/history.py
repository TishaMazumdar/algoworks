from datetime import datetime
import json
import os
from typing import List

CHAT_CACHE_DIR = ("chat_cache")
os.makedirs(CHAT_CACHE_DIR, exist_ok=True)

MAX_CACHE_SIZE = 6

class ChatEntry:
    def __init__(self, question: str, answer: str, sources: List[str], timestamp: str = None):
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

# ---------- Per-User Caching Functions ----------

def get_user_cache_file(username: str) -> str:
    return os.path.join(CHAT_CACHE_DIR, f"{username}.json")


def load_user_cache(username: str) -> List[ChatEntry]:
    file_path = get_user_cache_file(username)
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                content = f.read().strip()
                if not content:
                    return []
                data = json.loads(content)
                return [ChatEntry.from_dict(entry) for entry in data]
            except json.JSONDecodeError:
                return []
    return []


def save_user_cache(username: str, entry: ChatEntry):
    entries = load_user_cache(username)

    # Avoid duplicates
    if any(e.question.strip().lower() == entry.question.strip().lower() for e in entries):
        return

    entries.append(entry)
    entries = entries[-MAX_CACHE_SIZE:]  # Keep only the last N entries

    with open(get_user_cache_file(username), "w") as f:
        json.dump([e.to_dict() for e in entries], f, indent=2)


def get_user_cached_entry(username: str, question: str) -> ChatEntry | None:
    question_lower = question.strip().lower()
    for entry in load_user_cache(username):
        if entry.question.strip().lower() == question_lower:
            return entry
    return None

def clear_user_cache(username: str):
    with open(get_user_cache_file(username), "w") as f:
        f.write("[]")