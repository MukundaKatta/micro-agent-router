# micro-agent-router

A lightweight Python framework for routing tasks to specialized AI agents. Define agents with specific skills, and let the router automatically dispatch tasks to the best-fit agent based on intent matching.

Built for developers who want multi-agent orchestration without the complexity of heavyweight frameworks.

## Features

- **Intent-based routing** - Automatically match incoming tasks to the right agent using keyword and semantic similarity scoring
- **Pluggable agents** - Define custom agents with just a name, description, and handler function
- **Fallback chains** - Configure fallback agents when the primary match confidence is low
- **Conversation memory** - Built-in short-term memory store so agents can reference prior context
- **Async-ready** - Full async/await support for concurrent agent execution
- **Zero dependencies on LLM providers** - Bring your own model or API; the router is model-agnostic

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from micro_agent_router import AgentRouter, Agent

# Define specialized agents
code_agent = Agent(
    name="code-assistant",
    description="Writes, reviews, and explains code",
    skills=["python", "javascript", "code review", "debugging"],
    handler=my_code_handler
)

research_agent = Agent(
    name="researcher",
    description="Searches and summarizes information from the web",
    skills=["web search", "summarization", "fact checking"],
    handler=my_research_handler
)

# Create router and register agents
router = AgentRouter()
router.register(code_agent)
router.register(research_agent)

# Route a task - the router picks the best agent
result = router.route("Write a Python function to sort a list of dictionaries by key")
print(result)
```

## Advanced Usage

### Custom Scoring

```python
from micro_agent_router import AgentRouter, ScoringStrategy

router = AgentRouter(scoring=ScoringStrategy.WEIGHTED_KEYWORDS)
```

### Fallback Chains

```python
router.set_fallback("general-assistant")

# If no agent scores above the confidence threshold,
# the fallback agent handles the task
result = router.route("Tell me a joke")
```

### Memory Store

```python
from micro_agent_router import MemoryStore

memory = MemoryStore(max_entries=100)
router = AgentRouter(memory=memory)

# Agents can now access conversation history
router.route("Summarize what we discussed earlier")
```

## Project Structure

```
micro_agent_router/
  __init__.py        - Package exports
  agent.py           - Agent definition and registration
  router.py          - Core routing engine with intent matching
  memory.py          - Conversation memory store
  scoring.py         - Scoring strategies for agent selection
examples/
  demo_basic.py      - Basic routing example
  demo_memory.py     - Memory-enabled routing example
```

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `confidence_threshold` | `0.3` | Minimum score to match an agent |
| `scoring` | `WEIGHTED_KEYWORDS` | Scoring strategy for matching |
| `max_memory` | `50` | Max conversation entries in memory |
| `enable_logging` | `False` | Enable debug logging |

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) for details.
