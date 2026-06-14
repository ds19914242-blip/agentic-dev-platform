# Agentic Console (web UI)

Local web control plane for the Agentic Dev Platform. Stage 1: drive the
**human request → product spec** step from a browser and inspect every
artifact and which agent produced it — instead of typing CLI commands.

Zero external dependencies. Pure Python stdlib + one static HTML file.

## Run

From the platform root (the folder that contains `agentic.py`):

```bash
python3 webui/server.py            # http://127.0.0.1:8765
python3 webui/server.py --port 9000
```

Open the printed URL. The server runs the real platform code, so it must
sit next to `agentic.py`, `orchestrator/`, `products/`, `backlog/`, `runs/`.

## What stage 1 does

- **Compose** — type a request, pick a product, hit *Decompose*. This creates
  `backlog/<epic>/` and runs the **Product Agent** to write `product-spec.md`
  (same code path as `agentic.py decompose`). The run log shows each step.
  > The Product Agent calls the `claude` CLI. If `claude` isn't installed, the
  > epic scaffold (`epic.md`, `outcome.json`) is still created and the log says
  > the agent was skipped — no crash.
- **Epics** — browse every epic with status and task count; open one to see its
  pipeline rail, artifacts (rendered markdown / JSON), and backlog tasks.
- **Runs** — recent execution runs from `runs/` with type, stage and status.
- **Agents** — the roster: spec personas (Product Agent, Analyst, Decomposer)
  and runtime agents (architect → implementation → validation → review →
  acceptance → release), each tied to its pipeline stage.

## Endpoints (for the next iterations)

```
GET  /api/state                  version, products, agents, pipeline
GET  /api/epics                  list of epics
GET  /api/epic?id=<epic>         stations, artifacts, tasks, outcome
GET  /api/runs                   recent runs
GET  /api/file?path=backlog/...  artifact contents (sandboxed to backlog|runs|products)
POST /api/decompose {product, request}   create epic + run Product Agent
```

## Roadmap

- **Stage 2** — wire `approve-product-spec` and `approve-spec` buttons so the
  whole spec pipeline runs from the UI; live-stream agent logs (SSE).
- **Stage 3** — task execution view: trigger `schedule`/`backlog`, watch run
  stages (implementation → validation → review → PR) update live.
- **Stage 4** — DAG visualization for tasks, acceptance + release-check panels.
- **Stage 5** — multi-product switching and the agent-graph (dynamic/multi)
  view for the new Agent Runtime.
