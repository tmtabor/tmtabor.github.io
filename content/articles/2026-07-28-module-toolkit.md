Title: Building the GenePattern Module Toolkit
Date: 2026-07-28
Slug: genepattern-module-toolkit
Tags: genepattern, agentic-ai, open-source, pydantic-ai
Summary: How a hierarchical multi-agent pipeline increased GenePattern module production fivefold.

It's five o'clock on a Wednesday, and I have twelve tabs open across two monitors. Four of them are Google searches. One is a Biostars thread from a few months back that I've had bookmarked for three days now, because it's the closest thing anyone has written to what I'm trying to understand. Another is a conversation with an AI assistant that's now twenty messages deep, patiently walking me through spatial transcriptomic gradients like a TA answering the same question for the fifth time this semester.

I'm not a biologist. I'm a software engineer by training. And I have been assigned to integrate the [spatialGE](https://github.com/FridleyLab/spatialGE) suite of tools into GenePattern, a bioinformatics platform used by researchers who mostly just want their data to turn into an answer to their scientific inquiries.

This isn't a task I can fake my way through. spatialGE consists of a non-linear workflow with at least nine distinct steps and speaks two separate data formats. The modules I'm building have to work together as a coherent, containerized, multi-step pipeline instead of nine stand-alone scripts that happen to share a folder. Getting that right means actually understanding when a researcher would reach for enrichment versus differential expression versus one of half a dozen normalization schemes, because if I get that wrong, the module is wrong no matter how clean the code underneath it is.

The people who wrote spatialGE are not in the room. They're not on Slack. As far as I can tell they're two time zones and a very long email chain away, and I've decided not to bother them until I've exhausted every other option. So it's just me, the documentation and however much of Biostars I can absorb before I have to go make dinner.

This isn't really a story about spatial transcriptomics, though it starts there. [GenePattern](https://www.genepattern.org/) has been around since the early 2000s and the idea behind it has aged well: researchers don't want to spend their afternoons untangling dependency trees or memorizing the command-line flags for a tool some grad student wrote eight years ago. The platform takes hundreds of independently developed bioinformatics tools, most written by academic labs with no particular interest in software engineering practices, and wraps each one in a user-friendly web form. It's a translation layer between "here is a tool that does interesting science" and "here is something a non-programmer can actually run." 

The catch is that every one of those tools has to be integrated by hand: someone sits down with the documentation, or with the scientists who built it if they're lucky enough to get a response, and figures out which parameters actually matter, what the true dependencies are, how to wrap it in a containerized environment and how to test that all of it works. 

For spatialGE, that someone was me, and by the time this story is over, that someone was going to become a pipeline of AI agents that eventually pushed our module output up by roughly 500 percent.

## The toolkit gets its green light

We were a small team with a long backlog. Every new tool integration was traditionally a multi-day undertaking: read the docs, talk to the lab if you could, write the wrapper, write the manifest, write the tests and hope you haven't missed an edge case a scientist would find obvious.

I'd just come off a different corner of the GenePattern ecosystem: a project called GenePattern Copilot, which was an agentic assistant that could answer platform and genomics questions, as well as execute tasks on a user's behalf. This meant agentic AI was already on my mind. So a week into teaching myself spatial transcriptomics by trial and Biostars, I had the thought that eventually occurs to every engineer stuck doing something repetitive and well-specified: *there has to be a better way to do it.*

I sketched the architecture on my whiteboard, not a single model doing everything end to end, but a hierarchy: an orchestrator agent at the top, and underneath it, a set of agents each responsible for producing one specific artifact a GenePattern module needs. I brought the sketch to my boss. It got the green light, and the GenePattern Module Toolkit was born.

The idea was simple to state and much harder to build. Point the toolkit at a tool's documentation and its git repository, optionally tell it which user stories or features to prioritize, and let it do the work. What comes out the other end is a module a human can QA in an afternoon instead of building from scratch over three days.

## One orchestrator, eight agents

Here's roughly what the toolkit looked like once it settled into a stable shape. At the top sits an orchestrator, managing a pipeline of eight subagents. The first two that get called are a researcher agent, which pulls documentation and context from online sources, and a planner agent, whose entire job is making sure every other agent is working from the same set of assumptions. Execution is then passed to a pipeline of six artifact agents, each responsible for a single component: manifest, wrapper script, parameter groups, documentation, tests and Dockerfile.

The artifact agents use a pattern called chain of verification, though at the time I was just calling it "check the thing before moving to the next thing." Each agent generates its artifact. A linter script then runs against that artifact and checks whether it's actually valid. If it passes, the pipeline moves to the next agent. If it fails, the error gets escalated to the orchestrator, which has to make a judgment call: is this a bad run of this one artifact, or is it symptomatic of an upstream failure, something an earlier agent produced? If it's upstream, the orchestrator kicks the pipeline back to that earlier step and reruns from there. This is gated by a maximum number of iterations before it gives up and flags the run for human evaluation.

## Starting with the scaffolding, not the model

GenePattern was old and had grown organically enough over two decades. It never had a formal definition for what a manifest file was supposed to contain, let alone the rest of its artifacts. This was a problem that needed to be solved before I could even think about agents: there was no ground truth to check anything against.

So the first thing I built for an AI-driven project was not AI. It was linter scripts, effectively defining a de facto standard for what a valid GenePattern manifest, and the other artifacts, look like. 

Manifests are Java properties files. Every required key has to be present, every value has to be of a type the platform expects and a literal `=` inside a value has to be escaped or the parser reads it as the start of a new key. None of this is exotic. It's the kind of thing a human engineer internalizes after their third or fourth manifest and then never thinks about again. It is also exactly the kind of detail an LLM will cheerfully get wrong, because nothing about "write a manifest" tells it that an unescaped `=` is fatal. 

The linters caught missing keys, wrong value types, unescaped `=` characters, dependencies missing from the Dockerfile and property names that quietly drifted between artifacts that were supposed to agree with each other. Those scripts would go on to become the backbone of the chain-of-verification pattern, but at the time they were just me trying to codify rules that had only ever existed as institutional knowledge.

Is it strange to start an agentic AI project by writing rigid, deterministic scripts that have nothing to do with the model? I don't think so. Every project I've built has reinforced the same lesson: the harness around a model matters at least as much as the model itself. Without it you don't have an agent, you have a very confident guess.

## Wiring the linters to the AI

With the linters working on their own, the next job was hooking them up to something that could actually write the artifacts they were checking. 

For the agent framework I picked [Pydantic AI](https://pydantic.dev/docs/ai/overview/) because it's fast, lightweight and good at structured output. This mattered because nearly everything in this system, from planning a module to writing its manifest, depended on getting the model to hand back data in a shape you can work with rather than a paragraph you have to regex apart.

Once that plumbing was in place, the real work started: iterating on prompts, which is a deceptively glamorous phrase for staring at outputs and trying to figure out why an agent decided a parameter should be an integer when it should have been a float. More than once, an artifact would sail through its own generation and then fail the linter for something that looked cosmetic, such as a manifest key spelled slightly differently than the wrapper script expected, and the chain-of-verification loop would kick the run back to the step that actually introduced the problem. 

That's the pattern doing its job: catching the kind of small, specific mistake that wouldn't announce itself until a researcher tried to actually run the module and it silently used the wrong default.

## Evals before anything else

My last project, GenePattern Copilot, taught me a lesson the hard way: if you don't build a formal evaluation suite from the beginning, you end up debugging by vibes, and vibes do not scale. I started this project determined not to repeat that mistake.

Building a good eval suite from scratch is often a project of its own, but GenePattern had one advantage: it was a mature platform with a large corpus of known-good modules already sitting in production. That corpus became my known-good outputs, and I worked backwards from there, generating synthetic inputs that should produce something close to those known-good modules. Early runs of the toolkit added to that suite too, mostly by failing, with each bad output becoming a documented failure state I could check future runs against.

## Where the breakages happened

A single input-and-output eval may be enough for a system with one model doing one job. It isn't enough for a pipeline with eight subagents, each with its own inputs, outputs and failure modes. I needed to evaluate each one independently, or I'd have no way of knowing which agent was actually responsible when something broke downstream. That's where nearly all of my early failures lived, and this project is what taught me that in a multi-agent system, observability isn't optional.

Once one agent's output becomes another agent's input, a small ambiguity introduced three steps upstream can surface as a completely unrelated-looking failure two agents later. Trying to debug that by reading logs after the fact felt like reconstructing a car crash from the skid marks. I needed to watch it happen with better clarity.

I picked [Logfire](https://github.com/pydantic/logfire) for this, mostly because it's built by the same team behind Pydantic AI and the integration took 10 minutes. This let me trace a single request from the initial prompt through the orchestrator and out through each subagent in order. More importantly, it also let me see exactly where the context handed from one agent to the next started to drift from what the next agent needed. Once I had that visibility, progress on stability went from slow and confusing to fast and specific.

## Learning to survive a crash

A full run of the toolkit was not fast. Between the researcher agent pulling context from the web, the linter scripts running their checks, a Docker image building as part of the containerization tests and the LLM calls themselves, a typical run took twenty to thirty minutes. And in the early days, that half hour was not guaranteed to finish.

Inference calls hung. Web requests from the researcher agent hung. Docker builds ran out of disk space partway through and died. Agents hit their maximum number of retries without resolving whatever had gone wrong. None of this was exotic. It was just what happens when you chain together enough steps that each have their own independent failure modes.

The fix started small. I wanted a way to test one step of the pipeline in isolation without rerunning the whole thing from scratch every time, so I started to serialize the current state of the pipeline to disk as a status.json file. This also became the artifact each agent handed off to the next. From there it was easy to implement a flag letting a run resume from an existing status.json. A handful of additional flags let me target specific steps or ranges of steps directly. This made both testing and recovery faster.

What I'd actually built, without ever calling it that at the time, was a crude, hand-rolled version of durable execution: a workflow whose state survives the process running it, so that a crash costs you the time since your last checkpoint instead of the entire run. That wasn't my initial goal. My goal was to get my afternoon back after watching a Docker build die partway through for the third time. But once it existed, I couldn't unsee how much of the pipeline's actual reliability was coming from that one property rather than from anything about the agents themselves.

## The planner agent

The planner wasn't part of my original design. It got added later because of a specific, repeated failure: the agents kept producing artifacts that were each individually correct, but which didn't agree with each other. The manifest agent might settle on one set of parameter names while the wrapper script agent settled on a slightly different set. Each would pass its own linter checks in isolation, then fail the moment you tried to assemble them into one working whole.

The planner's job is to make that decision once, upstream of the six artifact agents, instead of letting the six agents make six independent guesses. It looks at the researcher agent's report and figures out the right general approach: an R script gets handled differently than a Python library, which gets handled differently than a raw shell script or a compiled C binary, etc. It decides which parameters are worth exposing, and settles on the actual names and descriptions those parameters will have in GenePattern's interface. All this becomes shared context for every downstream agent.

## Handing it to the interns

Once the pipeline was running reliably for me, it was time to see if it worked for anyone else. So we handed it to our interns and asked them to use it for the modules already on their plate.

It broke almost immediately. Runs failed constantly at the planning stage, or hit their maximum iteration count in the first two artifact stages before anything useful came out.

Part of this was a decision made above my pay grade, and a reasonable one. We'd just had an API key leak that racked up a sizable bill before anyone noticed, and the lab had no interest in handing a new set of keys to a room full of interns. Instead, we set them up with a local Qwen model we'd tested ourselves and found passable, albeit not nearly as strong as Claude.

This worked for me. It failed for most of them. I still don't have a clean explanation for the gap between my machine and theirs, but the failure I could actually see and fix was structural: Qwen produced malformed, structurally hallucinated JSON (e.g. invented fields, wrong nesting, values in the wrong shape entirely) far more often than Claude did.

I spent some real effort trying to close that gap by fine-tuning Qwen at the San Diego Supercomputer Center, and in the end achieved something like a 50 percent reduction in the structural hallucination rate. This was good progress, but it wasn't enough.

So I made the call: I stopped trying to optimize the model further, and instead threw together a lightweight hosted frontend on AWS, backed by Claude via Bedrock. After that, the reliability problem which had eaten weeks of intern time mostly stopped being a problem.

## Conclusions

Once the interns had their turn and the production hardening was done, we rolled the toolkit out to the rest of the GenePattern team. As a result, module production went up roughly 500 percent. And along the way I learned a few lessons.

The scaffolding around a model—the linters, the schemas, the harness that tells it when it's wrong—deserves to be built before the model touches anything, not bolted on once things are already unstable.

A strong planner sitting upstream of your artifact-generating agents will save you from an entire category of bugs that look like model-quality problems, but which are actually coordination problems. Six correct answers that don't agree with each other just aren't that useful. 

Observability isn't optional in anything where one agent talks to another. That's where a lot of non-obvious bugs can hide, rather than in any single agent's output. Before implementing observability, I spent more hours confused than I want to admit.

Don't overlook durability. Any workflow that runs long enough to be worth building is going to run long enough to fail partway through, and if you haven't decided in advance what happens when it does, you'll end up deciding it anyway, at 5pm, under worse conditions than if you'd just planned for it.

Sometimes the scaffolding's real value is proving, with evidence, exactly where a model's ceiling sits, turning the decision to replace it into a documented engineering call instead of a shrug.

None of these lessons are especially profound on their own. But together they compound: Solving the coordination problem with a planner made the durability problem more visible. Better observability made the coordination problem easier to fix. None of it works if the scaffolding underneath is an afterthought. 

That's not a spatialGE story, or even a bioinformatics one. It's just what happens when you build something agentic that has to survive contact with real work.