"""Conversation memory store for agent context."""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class MemoryEntry:
    """A single entry in conversation memory."""
    task: str
    agent_name: str
    response: Any
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


class MemoryStore:
    """Short-term conversation memory for agent routing context.

    Stores recent task-response pairs so agents can reference prior
    conversation history when processing new tasks.
    """

    def __init__(self, max_entries: int = 50, ttl_seconds: int = 0) -> None:
        self.max_entries = max_entries
        self.ttl_seconds = ttl_seconds
        self._entries: deque = deque(maxlen=max_entries)
        self._tags: Dict[str, List[MemoryEntry]] = {}

    def add(self, task, agent_name, response, tags=None, metadata=None):
        """Add a new entry to memory."""
        entry = MemoryEntry(task=task, agent_name=agent_name, response=response, metadata=metadata or {})
        self._entries.append(entry)
        if tags:
            for tag in tags:
                self._tags.setdefault(tag, []).append(entry)
        return entry

    def get_recent(self, n: int = 10) -> List[MemoryEntry]:
        """Get the N most recent memory entries."""
        self._cleanup_expired()
        return list(self._entries)[-n:]

    def get_by_agent(self, agent_name: str, n: int = 10) -> List[MemoryEntry]:
        """Get recent entries handled by a specific agent."""
        self._cleanup_expired()
        return [e for e in self._entries if e.agent_name == agent_name][-n:]

    def get_by_tag(self, tag: str) -> List[MemoryEntry]:
        """Get all entries with a specific tag."""
        self._cleanup_expired()
        return self._tags.get(tag, [])

    def search(self, keyword: str) -> List[MemoryEntry]:
        """Search memory entries by keyword in task text."""
        self._cleanup_expired()
        kw = keyword.lower()
        return [e for e in self._entries if kw in e.task.lower()]

    def to_context_dict(self, n: int = 5) -> Dict[str, Any]:
        """Export recent memory as a context dictionary for agents."""
        recent = self.get_recent(n)
        return {
            "conversation_history": [
                {"task": e.task, "agent": e.agent_name, "response": str(e.response)[:500], "timestamp": e.timestamp}
                for e in recent
            ],
            "total_entries": len(self._entries),
        }

    def clear(self) -> None:
        """Clear all memory entries."""
        self._entries.clear()
        self._tags.clear()

    def _cleanup_expired(self) -> None:
        """Remove entries that have exceeded their TTL."""
        if self.ttl_seconds <= 0:
            return
        now = time.time()
        while self._entries and (now - self._entries[0].timestamp) > self.ttl_seconds:
            expired = self._entries.popleft()
            for tag_entries in self._tags.values():
                if expired in tag_entries:
                    tag_entries.remove(expired)

    def __len__(self): return len(self._entries)
    def __repr__(self): return f"MemoryStore(entries={len(self._entries)}, max={self.max_entries})"
