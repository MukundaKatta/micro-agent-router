"""Core routing engine for dispatching tasks to agents."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .agent import Agent
from .memory import MemoryStore
from .scoring import ScoringStrategy, rank_agents

logger = logging.getLogger("micro_agent_router")


@dataclass
class RouteResult:
    """Result of routing a task to an agent."""
    task: str
    agent_name: str
    score: float
    response: Any
    all_scores: List[Dict] = field(default_factory=list)


class AgentRouter:
    """Routes incoming tasks to the best-matching registered agent.

    The router scores each registered agent against the task using the
    configured scoring strategy, then dispatches to the highest-scoring
    agent that meets the confidence threshold.
    """

    def __init__(self, scoring=None, confidence_threshold=0.3, memory=None, enable_logging=False):
        self.scoring = scoring or ScoringStrategy.WEIGHTED_KEYWORDS
        self.confidence_threshold = confidence_threshold
        self.memory = memory
        self._agents: Dict[str, Agent] = {}
        self._fallback_name: Optional[str] = None
        if enable_logging:
            logging.basicConfig(level=logging.DEBUG)

    def register(self, agent: Agent) -> None:
        """Register an agent with the router."""
        if agent.name in self._agents:
            raise ValueError(f"Agent '{agent.name}' is already registered")
        self._agents[agent.name] = agent
        logger.debug(f"Registered agent: {agent.name} with skills {agent.skills}")

    def unregister(self, name: str) -> None:
        """Remove a registered agent."""
        self._agents.pop(name, None)
        if self._fallback_name == name:
            self._fallback_name = None

    def set_fallback(self, agent_name: str) -> None:
        """Set a fallback agent for when no good match is found."""
        if agent_name not in self._agents:
            raise ValueError(f"Agent '{agent_name}' is not registered")
        self._fallback_name = agent_name

    @property
    def agents(self) -> List[Agent]:
        """List all registered agents."""
        return list(self._agents.values())

    def find_best_agent(self, task: str) -> Optional[Dict]:
        """Find the best matching agent for a task without executing it."""
        rankings = rank_agents(task, self.agents, self.scoring)
        if not rankings:
            return None
        best = rankings[0]
        if best["score"] >= self.confidence_threshold:
            return best
        if self._fallback_name and self._fallback_name in self._agents:
            return {"agent": self._agents[self._fallback_name], "score": 0.0}
        return None

    def route(self, task: str) -> RouteResult:
        """Route a task to the best agent and execute it synchronously."""
        return asyncio.get_event_loop().run_until_complete(self.aroute(task))

    async def aroute(self, task: str) -> RouteResult:
        """Route a task to the best agent and execute it asynchronously."""
        rankings = rank_agents(task, self.agents, self.scoring)
        all_scores = [{"agent": r["agent"].name, "score": round(r["score"], 4)} for r in rankings]
        logger.debug(f"Task: '{task[:80]}...' | Scores: {all_scores}")

        best = None
        if rankings and rankings[0]["score"] >= self.confidence_threshold:
            best = rankings[0]
        if best is None and self._fallback_name and self._fallback_name in self._agents:
            best = {"agent": self._agents[self._fallback_name], "score": 0.0}
        if best is None:
            raise RuntimeError(f"No suitable agent found for task: '{task[:100]}'. Scores: {all_scores}")

        agent = best["agent"]
        context = self.memory.to_context_dict() if self.memory else {}
        response = await agent.execute(task, context)
        if self.memory:
            self.memory.add(task=task, agent_name=agent.name, response=response)

        return RouteResult(task=task, agent_name=agent.name, score=best["score"], response=response, all_scores=all_scores)

    async def broadcast(self, task: str) -> List[RouteResult]:
        """Send a task to ALL registered agents concurrently."""
        context = self.memory.to_context_dict() if self.memory else {}
        async def run_agent(agent):
            response = await agent.execute(task, context)
            return RouteResult(task=task, agent_name=agent.name, score=1.0, response=response)
        available = [a for a in self.agents if a.is_available]
        results = await asyncio.gather(*[run_agent(a) for a in available], return_exceptions=True)
        return [r for r in results if isinstance(r, RouteResult)]

    def __repr__(self):
        return f"AgentRouter(agents={[a.name for a in self.agents]}, strategy={self.scoring.value})"
