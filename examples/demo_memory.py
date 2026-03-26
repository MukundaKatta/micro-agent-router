"""Demo of micro-agent-router with conversation memory."""

from micro_agent_router import Agent, AgentRouter, MemoryStore


def handler_with_context(task, context):
    """Handler that uses conversation history from memory."""
    history = context.get("conversation_history", [])
    response = f"Processing: {task}\n"
    if history:
        response += f"I have context from {len(history)} previous interactions.\n"
        last = history[-1]
        response += f"Last task was handled by '{last['agent']}': {last['task'][:60]}..."
    else:
        response += "This is the first interaction - no prior context."
    return response


def main():
    memory = MemoryStore(max_entries=100)

    analyst = Agent(
        name="data-analyst",
        description="Analyzes data, creates charts, and provides statistical insights",
        skills=["data", "analysis", "statistics", "chart", "visualization", "csv", "numbers"],
        handler=handler_with_context,
    )
    coder = Agent(
        name="coder",
        description="Writes and reviews code, builds scripts and tools",
        skills=["code", "python", "script", "build", "programming", "function"],
        handler=handler_with_context,
    )

    router = AgentRouter(memory=memory, confidence_threshold=0.15)
    router.register(analyst)
    router.register(coder)
    router.set_fallback("coder")

    print("=" * 60)
    print("Memory-Enabled Routing Demo")
    print("=" * 60)

    conversation = [
        "Analyze the sales data from Q1 and find top performers",
        "Write a Python script to automate that analysis",
        "Now create a visualization of the results",
        "Can you refactor the script to use pandas more efficiently?",
    ]

    for i, task in enumerate(conversation, 1):
        print(f"\n--- Turn {i} ---")
        print(f"User: {task}")
        result = router.route(task)
        print(f"Agent: {result.agent_name} (score: {result.score:.3f})")
        print(f"Response: {result.response}")

    print("\n" + "=" * 60)
    print("Memory Contents:")
    print("=" * 60)
    for entry in memory.get_recent(10):
        print(f"  [{entry.agent_name}] {entry.task[:60]}...")

    print("\nSearching memory for 'script':")
    for entry in memory.search("script"):
        print(f"  Found: {entry.task[:60]}... (by {entry.agent_name})")


if __name__ == "__main__":
    main()
