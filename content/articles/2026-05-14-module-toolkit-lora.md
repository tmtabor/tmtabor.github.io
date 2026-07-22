Title: Fine-Tuning Six LoRAs for the Module Toolkit
Date: 2026-05-14
Slug: module-toolkit-lora
Tags: agentic-ai, lora, bioinformatics
Summary: How a hierarchical multi-agent pipeline and six task-specific LoRAs increased GenePattern module production roughly fivefold.

The GenePattern AI Module Toolkit wraps arbitrary bioinformatics CLI tools as GenePattern modules automatically: point it at a repository, its docs, and some example data, and a pipeline of agents produces a working module.

## Why six LoRAs instead of one model

Each artifact the pipeline produces — manifest, wrapper script, parameter definitions, documentation, test data, GenomeSpace metadata — has different failure modes. A single general-purpose model tended to do fine on five of six and quietly mangle the sixth. Splitting into six Qwen3.5-9B LoRAs, one per artifact type, let each adapter specialize on its own synthetic training distribution, generated and hand-curated on SDSC compute.

## The supervisor loop

A supervisor agent coordinates a researcher, a planner, and the six artifact agents, with structured escalation back up the chain when an artifact agent gets stuck or produces something that fails validation. It's not glamorous, but it's the piece that took module production from "the bottleneck is engineer time" to "the bottleneck is which tools to wrap next."
