Title: A hallucinated module, a backfiring RAG pipeline and the MCP server that fixed it
Date: 2026-09-13
Slug: genepattern-copilot
Tags: genepattern, agentic-ai, rag, mcp, pydantic-ai
Image: images/og-genepattern-copilot.png
Summary: How an eval suite exposed a RAG pipeline that hurt GenePattern Copilot more than it helped, and what finally fixed it.

It’s a surprisingly humid day for San Diego. We’re running a workshop, teaching [GenePattern](https://www.genepattern.org/) to a dozen medical students, and we’re about to demo something in public for the first time: GenePattern Copilot, our first generative AI offering. Sweat drips. What could go wrong.

<blockquote class="float-right w-[300px] ml-8 mb-4 pl-5 border-l-[3px] border-gray-400
         font-serif text-xl leading-snug
         max-[700px]:float-none max-[700px]:w-auto max-[700px]:ml-0" aria-hidden="true">
  It’s sitting right there on the screen in the list the assistant just generated. And I know it’s a hallucination.
</blockquote>

One of the students types an innocent question into the chat window: *What GenePattern modules are available?* The answer comes back, and most of it is exactly what you’d expect: Gene Set Enrichment Analysis, Hierarchical Clustering, PCA. The usual suspects. Then he says something nice about the platform. He’s glad to see we offer [scPerturb](https://projects.sanderlab.org/scperturb/), a toolkit for single-cell perturbation analysis.

I cringe. It’s sitting right there on the screen in the list the assistant just generated. And I know it’s a hallucination.

We don’t have scPerturb. It’s a good idea for a module, one we should probably build someday, but it does not exist on GenePattern, and the assistant just told a room full of medical students that it does.

I don’t correct him in front of the group. I let it slide and make a mental note to fix it, which ends up taking longer than I expect.

None of that makes sense without knowing about GenePattern. It was a platform for reproducible bioinformatics research, taking tools built by labs worldwide and wrapping them into something a non-technical scientist could run without learning to code. The mission was accessibility.

Fast forward to early 2024. Generative AI was blowing up, and it looked like an obvious fit, even for a lab that spent most of its history doing traditional Bayesian AI rather than anything resembling deep learning.

A colleague got there first. He put together an early prototype of GenePattern Copilot, then left the group. I inherited the project without much ceremony. One day I didn’t have a generative AI project, and the next I had a mandate to turn a rough prototype into something we could put in front of real users.

The credit for the original idea belongs to him. Everything downstream of that, for better or worse, is mine.

## Inheriting a moving target

I inherited a [LangChain](https://www.langchain.com/) project written in Python, capable of switching between models through [AWS Bedrock](https://aws.amazon.com/bedrock/). At the time that meant Llama, GPT, Claude and Mistral, each with its own quirks, and each compared against the others manually.

I quickly found manual, informal comparisons between models to be unwieldy, and it only got worse once I started varying what data went into the RAG pipeline.

The assistant was never meant to be just a wrapper around an inference API. Its main value-add was the retrieval layer: a [ChromaDB](https://www.trychroma.com/) database, OpenAI embeddings and a RAG corpus built from our documentation, a decade’s worth of help forums and a handful of Jupyter notebooks. In theory, this gave the model everything it needed to answer questions about the platform and the underlying bioinformatics.

At this point, the prototype’s eval process was someone reading outputs and deciding if they looked right. The first real work I did on this project, beyond some basic code cleanup, was building a proper eval suite. I needed a concrete way to measure how well the assistant performed.

## The RAG that made things worse

Once the eval infrastructure existed, I ran the most obvious comparison: the assistant with full RAG retrieval turned on against the same model given a raw query and no retrieval.

<blockquote class="float-right w-[300px] ml-8 mb-4 pl-5 border-l-[3px] border-gray-400
         font-serif text-xl leading-snug
         max-[700px]:float-none max-[700px]:w-auto max-[700px]:ml-0" aria-hidden="true">
  The raw model, with no access to our documentation or forum data, outperformed our fully retrieval-augmented assistant on almost every substantial question I threw at it.
</blockquote>

I expected the RAG version to win comfortably. That’s the whole point of building a RAG pipeline.

Surprisingly, the assistant with RAG performed worse, and not by a narrow margin.

The raw model, with no access to our documentation or forum data, outperformed our fully retrieval-augmented assistant on almost every substantial question I threw at it.

That result sent me digging through the LangChain graph trying to figure out what was happening at each step, but I quickly ran into a wall: I had basic logs, but they weren’t structured in a way that made it easy to trace a single request end to end.

So I improved that logging by hand and was eventually able to track down the issue. Later we would move to a real observability platform, [Logfire](https://github.com/pydantic/logfire). But in the moment, it was mostly a lot of scrolling through raw output trying to find the thread.

## Getting the chunking right

The cause of the problem was in how we chunked the corpus, particularly the help forum data.

We used a naive, token-based chunking approach, the kind every RAG quick-start walks you through, and I discovered that it routinely split a forum thread’s question from its answer. When the vector search ran, it pulled in the question fragment, along with loosely related noise, and that got stuffed into the context window without actually picking up the answer.

The signal-to-noise ratio was bad, and that degraded the model’s reasoning.

The fix that worked was, before ingestion, preprocessing the corpus using an LLM-based fact extraction strategy. Instead of chunking documents by token count, I had a model read through each source and break it down into atomic statements of fact. Each statement was written to stand on its own, with ambiguous pronouns replaced by the nouns they referred to. Something like “GenePattern supports Gene Set Enrichment Analysis” became its own row in the vector database rather than a fragment of a longer paragraph that only made sense in context. That change alone measurably improved answer quality.

<div class="figure-wide"><svg width="100%" viewBox="0 0 680 260" role="img" xmlns="http://www.w3.org/2000/svg" style="font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif">
<title>Token chunking versus LLM fact extraction</title>
<desc>Before: naive token chunking splits a forum thread, so retrieval pulls in the question fragment and leaves its answer behind in a separate chunk. After: an LLM rewrites each source into atomic statements of fact, so every row in the vector database stands on its own.</desc>
<defs><marker id="arrow-chunk" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M2 1L8 5L2 9" fill="none" stroke="rgb(137, 135, 129)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></marker></defs>
<line x1="322" y1="130" x2="358" y2="130" stroke="rgb(137, 135, 129)" stroke-width="1.5" marker-end="url(#arrow-chunk)"/>
<g>
<rect x="40" y="30" width="280" height="200" rx="16" fill="rgb(250, 236, 231)" stroke="rgb(153, 60, 29)" stroke-width="0.5"/>
<text x="180" y="56" text-anchor="middle" dominant-baseline="central" fill="rgb(113, 43, 19)" font-size="14" font-weight="500">Naive token chunking</text>
<rect x="62" y="74" width="236" height="48" rx="8" fill="#ffffff" stroke="rgb(197, 138, 116)" stroke-width="0.75"/>
<text x="180" y="92" text-anchor="middle" dominant-baseline="central" fill="rgb(113, 43, 19)" font-size="11" font-weight="500">chunk 1 — retrieved</text>
<text x="180" y="110" text-anchor="middle" dominant-baseline="central" fill="rgb(153, 60, 29)" font-size="12">“How do I run GSEA?” + noise</text>
<line x1="62" y1="132" x2="298" y2="132" stroke="rgb(197, 138, 116)" stroke-width="1" stroke-dasharray="4 4"/>
<rect x="62" y="142" width="236" height="48" rx="8" fill="#ffffff" stroke="rgb(197, 138, 116)" stroke-width="0.75" stroke-dasharray="4 4"/>
<text x="180" y="160" text-anchor="middle" dominant-baseline="central" fill="rgb(113, 43, 19)" font-size="11" font-weight="500">chunk 2 — never retrieved</text>
<text x="180" y="178" text-anchor="middle" dominant-baseline="central" fill="rgb(153, 60, 29)" font-size="12">“Upload a GCT file, then…”</text>
<text x="180" y="212" text-anchor="middle" dominant-baseline="central" fill="rgb(113, 43, 19)" font-size="14" font-weight="500">The answer gets left behind</text>
</g>
<g>
<rect x="360" y="30" width="280" height="200" rx="16" fill="rgb(225, 245, 238)" stroke="rgb(15, 110, 86)" stroke-width="0.5"/>
<text x="500" y="56" text-anchor="middle" dominant-baseline="central" fill="rgb(8, 80, 65)" font-size="14" font-weight="500">LLM fact extraction</text>
<rect x="382" y="74" width="236" height="32" rx="8" fill="#ffffff" stroke="rgb(122, 186, 166)" stroke-width="0.75"/>
<text x="500" y="90" text-anchor="middle" dominant-baseline="central" fill="rgb(15, 110, 86)" font-size="12">“GenePattern supports GSEA.”</text>
<rect x="382" y="114" width="236" height="32" rx="8" fill="#ffffff" stroke="rgb(122, 186, 166)" stroke-width="0.75"/>
<text x="500" y="130" text-anchor="middle" dominant-baseline="central" fill="rgb(15, 110, 86)" font-size="12">“GSEA accepts GCT input files.”</text>
<rect x="382" y="154" width="236" height="32" rx="8" fill="#ffffff" stroke="rgb(122, 186, 166)" stroke-width="0.75"/>
<text x="500" y="170" text-anchor="middle" dominant-baseline="central" fill="rgb(15, 110, 86)" font-size="12">“GSEA reports enriched gene sets.”</text>
<text x="500" y="212" text-anchor="middle" dominant-baseline="central" fill="rgb(8, 80, 65)" font-size="14" font-weight="500">Each fact stands on its own</text>
</g>
</svg></div>

From this I learned that there is no one-size-fits-all chunking strategy. What works depends on the shape of the data you feed it. Help forum threads, module documentation and notebooks all have a different internal structure. Treating them identically at the chunking stage was the problem.

## The module list solution

Which brings me back to that workshop. By the time we ran it, the chunking fix was in place, and the assistant’s answers had gotten better across the board. Still, module hallucinations were a persistent problem. And it wasn’t a RAG issue: even with no retrieval involved, calls to the model routinely invented plausible-sounding GenePattern modules that never existed.

I tried a few approaches for fixing the hallucination issue before discovering one that worked. The solution was dumping a complete list of every real module name into the system prompt, along with an explicit instruction not to reference anything outside that list.

There were only a few hundred modules at the time, fitting comfortably inside the context window.

But while this was a working solution, it was also a band-aid. The list was accurate the day I wrote it and stale the moment we shipped a new module or deprecated an old one.

Maintaining a hardcoded list by hand, forever, was not a good longterm plan. What I wanted was something that could generate that list dynamically so it stayed current without anyone having to remember to update a prompt.

## Enter MCP

That thought turned into the next phase of the project. Rather than hardcoding the list of modules, I built a tool that the assistant could call to retrieve the current list from the server.

<blockquote class="float-right w-[300px] ml-8 mb-4 pl-5 border-l-[3px] border-gray-400
         font-serif text-xl leading-snug
         max-[700px]:float-none max-[700px]:w-auto max-[700px]:ml-0" aria-hidden="true">
  I spent more hours than I’d like to admit fighting basic plumbing problems that had nothing to do with the actual AI work I was supposed to be doing.
</blockquote>

That tool ended up being one small piece of something bigger: a GenePattern [Model Context Protocol](https://modelcontextprotocol.io/) server that wrapped the platform’s REST API, allowing the assistant to take actions on a user’s behalf.

By the time the MCP server was done, a user could ask about their running jobs, check the provenance of the data behind a result, launch new analyses, check statuses, retrieve results, summarize them or hand them off to a downstream visualization step—all through the same conversational interface.

Still, MCP was new at the time, and LangChain’s support for it was early. Almost immediately I ran into sync and async issues trying to get LangChain’s MCP integration to cooperate with the rest of the pipeline. I spent more hours than I’d like to admit fighting basic plumbing problems that had nothing to do with the actual AI work I was supposed to be doing.

Finally, after chasing down yet another LangChain bug, I decided to migrate the project to [Pydantic AI](https://pydantic.dev/docs/ai/overview/), which was working well for me at the time in a separate project, the [GenePattern Module Toolkit](/blog/genepattern-module-toolkit/).

Pydantic AI gave me better output validation, noticeably better developer ergonomics and none of the sync/async headaches that kept surfacing in LangChain’s MCP support. I never looked back.

## Trimming the toolbox

The first, naive version of the MCP server was, predictably, too ambitious. I wrapped nearly every endpoint in the GenePattern REST API on the theory that more capability was strictly better. It wasn’t.

In MCP, every tool comes with a description that gets injected into the model’s context whether or not that tool is relevant to the current conversation. With that many tools available at once, some models started to get noticeably confused about which one to reach for. At the time, MCP did not offer progressive disclosure, just a wall of tool descriptions competing for attention.

This needed fixed. So rather than wrapping all available REST endpoints, I began to think of MCP tool sets in terms of what user stories we wanted to enable, trimming unnecessary tools from the list. This made an immediate difference in how reliably the assistant picked the right tool.

From there I started iterating on the tool descriptions themselves, which quickly turned into its own small eval suite. Evals tested whether a specific tool should or shouldn’t be used, checked against whether a given model picked the right one on the first try or wandered into a wrong tool call and had to recover.

For a while I had already been versioning our main prompts, but when I extended that same discipline to the MCP tool descriptions, it became immediately clear how much a single word choice could change tool selection behavior.

## What full agentic looked like

MCP is what let GenePattern Copilot grow from a question-answering chatbot into something closer to a real agent: one that could run jobs, retrieve results and help a user explore the platform’s available tools.

By the time the project reached its mature state in mid-to-late 2025, the eval suite had grown into a full prompt library, built partly from real usage patterns and partly from the direction we wanted to push the assistant. Each prompt in that library was checked against a known ground-truth answer.

We could also run an eval matrix across combinations of model and RAG source to see how each performed relative to the others. We used LLM-as-judge to score responses against that ground truth, tracked the cost of each configuration and kept every prompt version tied to the eval results it produced.

As for that workshop demo, there was never a dramatic rematch where I proved that the hallucinations had been vanquished for good. Rather, the fix happened quietly, over days and then weeks of iteration, mostly unnoticed by anyone but me and the eval suite.
