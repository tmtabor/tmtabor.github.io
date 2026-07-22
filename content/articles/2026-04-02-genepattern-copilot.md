Title: Building GenePattern Copilot
Date: 2026-04-02
Slug: genepattern-copilot
Tags: agentic-ai, rag, mcp, pydantic-ai
Summary: Notes on building a RAG-based agentic assistant for bioinformatics research, and why we moved from LangChain to Pydantic AI.

GenePattern Copilot started as a question-answering bot over our documentation and grew into something that can operate the platform directly — launching jobs, checking on results, and explaining what a module actually does before you run it.

## Why we moved off LangChain

The initial prototype used LangChain and LangGraph, which got us moving fast but made structured output brittle as the agent's responsibilities grew. Migrating to Pydantic AI gave us:

- Typed, validated outputs at every step of the agent loop
- Much easier debugging when a tool call returns something unexpected
- A cleaner mental model for composing the MCP server tools

A tool definition ends up looking close to plain Python — no chain-building DSL to fight:

```python
from pydantic_ai import Agent, RunContext

copilot = Agent("openai:gpt-4.1", deps_type=GenePatternClient)


@copilot.tool
async def launch_job(ctx: RunContext[GenePatternClient], module: str, params: dict) -> str:
    """Launch a GenePattern module and return the job ID."""
    job = await ctx.deps.run_module(module, params)
    return job.id
```

## Observability

We wired in Logfire fairly early, which turned out to matter more than expected — once an agent can take actions on a user's behalf, being able to replay exactly what it saw and decided is not optional.

More on the MCP server side of this in a future post.
