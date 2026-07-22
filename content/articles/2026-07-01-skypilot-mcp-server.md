Title: Giving SkyPilot an MCP Server
Date: 2026-07-01
Slug: skypilot-mcp-server
Tags: mcp, agentic-ai, open-source
Summary: Letting AI agents schedule posts, manage queues, and read analytics on SkyPilot programmatically, on top of a Django/Celery/RabbitMQ stack.

SkyPilot is a scheduling and analytics tool for Bluesky and Threads that I built and have run solo since launch. Adding an MCP server on top of the existing REST API turned out to be a small amount of new code for a large amount of new capability.

## What the server exposes

- Scheduling and queue management for posts across both networks
- Media upload
- Analytics: hashtag performance, engagement trends, optimal posting windows, audience growth projections

## The unglamorous part

The interesting engineering here isn't the MCP layer itself — it's that Celery and RabbitMQ were already handling distributed task execution across worker nodes before any of this existed, so wrapping it in tools an agent can call was mostly a matter of picking sane boundaries, not building new infrastructure.
