"""Basic demo of micro-agent-router task routing."""

from micro_agent_router import Agent, AgentRouter


def code_handler(task, context):
    return f"[CodeAgent] I'd help with: {task}\nHere's a skeleton:\n\ndef solution():\n    pass"

def research_handler(task, context):
    return f"[ResearchAgent] Researching: {task}\nFindings: 1) ... 2) ... 3) ..."

def writer_handler(task, context):
    return f"[WriterAgent] Drafting: {task}\n\nDraft: Lorem ipsum..."

def general_handler(task, context):
    return f"[GeneralAgent] I'll do my best with: {task}"


def main():
    code_agent = Agent(
        name="code-assistant",
        description="Writes, reviews, debugs, and explains code in Python and JavaScript",
        skills=["python", "javascript", "code review", "debugging", "programming", "function", "class", "algorithm"],
        handler=code_handler, priority=1,
    )
    research_agent = Agent(
        name="researcher",
        description="Searches the web and summarizes information on any topic",
        skills=["search", "summarize", "research", "find information", "fact check", "web"],
        handler=research_handler,
    )
    writer_agent = Agent(
        name="writer",
        description="Writes blog posts, emails, documentation, and creative content",
        skills=["write", "blog", "email", "documentation", "article", "creative writing", "draft"],
        handler=writer_handler,
    )
    general_agent = Agent(
        name="general",
        description="Handles general tasks and questions",
        skills=["general", "help", "question"],
        handler=general_handler,
    )

    router = AgentRouter(confidence_threshold=0.2, enable_logging=True)
    router.register(code_agent)
    router.register(research_agent)
    router.register(writer_agent)
    router.register(general_agent)
    router.set_fallback("general")

    print("=" * 60)
    print("micro-agent-router Demo")
    print("=" * 60)

    tasks = [
        "Write a Python function to sort a list of dictionaries by key",
        "Research the latest trends in renewable energy",
        "Draft a blog post about machine learning for beginners",
        "What is the weather like today?",
        "Debug this JavaScript code that throws a TypeError",
    ]

    for task in tasks:
        print(f"\nTask: {task}")
        print("-" * 40)
        result = router.route(task)
        print(f"Routed to: {result.agent_name} (score: {result.score:.3f})")
        print(f"All scores: {result.all_scores}")
        print(f"Response: {result.response}\n")


if __name__ == "__main__":
    main()
