from datetime import datetime

class ChatEntry:
    def __init__(self, question: str, answer: str, sources: list[str]):
        self.question = question
        self.answer = answer
        self.sources = sources
        self.timestamp = datetime.now()