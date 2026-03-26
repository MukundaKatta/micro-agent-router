"""Scoring strategies for matching tasks to agents."""

from __future__ import annotations

import re
from enum import Enum
from typing import Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .agent import Agent


class ScoringStrategy(Enum):
    """Available scoring strategies for agent selection."""

    KEYWORD_MATCH = "keyword_match"
    WEIGHTED_KEYWORDS = "weighted_keywords"
    DESCRIPTION_SIMILARITY = "description_similarity"


def _tokenize(text: str) -> List[str]:
    """Split text into lowercase tokens, removing punctuation."""
    return re.findall(r"\b[a-z0-9]+\b", text.lower())


def _compute_keyword_overlap(tokens: List[str], skills: List[str]) -> float:
    """Compute what fraction of skills appear in the token set."""
    if not skills:
        return 0.0
    task_text = " ".join(tokens)
    matches = 0
    for skill in skills:
        skill_tokens = _tokenize(skill)
        if all(st in tokens for st in skill_tokens):
            matches += 1
        elif any(st in task_text or task_text.find(st[:4]) >= 0 for st in skill_tokens if len(st) >= 4):
            matches += 0.4
        elif any(st in tokens for st in skill_tokens):
            matches += 0.5
    return matches / len(skills)


def _compute_description_similarity(task_tokens: List[str], desc_tokens: List[str]) -> float:
    """Compute Jaccard similarity between task and description tokens."""
    if not task_tokens or not desc_tokens:
        return 0.0
    task_set = set(task_tokens)
    desc_set = set(desc_tokens)
    intersection = task_set & desc_set
    union = task_set | desc_set
    return len(intersection) / len(union) if union else 0.0


def score_agent(task, agent, strategy=None):
    """Score how well an agent matches a given task."""
    if strategy is None:
        strategy = ScoringStrategy.WEIGHTED_KEYWORDS
    task_tokens = _tokenize(task)
    if strategy == ScoringStrategy.KEYWORD_MATCH:
        return _compute_keyword_overlap(task_tokens, agent.skills)
    elif strategy == ScoringStrategy.WEIGHTED_KEYWORDS:
        keyword_score = _compute_keyword_overlap(task_tokens, agent.skills)
        desc_tokens = _tokenize(agent.description)
        desc_score = _compute_description_similarity(task_tokens, desc_tokens)
        return 0.6 * keyword_score + 0.4 * desc_score
    elif strategy == ScoringStrategy.DESCRIPTION_SIMILARITY:
        desc_tokens = _tokenize(agent.description)
        return _compute_description_similarity(task_tokens, desc_tokens)
    return 0.0


def rank_agents(task, agents, strategy=None):
    """Rank all agents by their match score for a task."""
    if strategy is None:
        strategy = ScoringStrategy.WEIGHTED_KEYWORDS
    scored = []
    for agent in agents:
        if not agent.is_available:
            continue
        s = score_agent(task, agent, strategy)
        scored.append({"agent": agent, "score": s})
    scored.sort(key=lambda x: (x["score"], x["agent"].priority), reverse=True)
    return scored
