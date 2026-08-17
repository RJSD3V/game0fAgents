# game0fAgents

🧬 A hybrid neuro-symbolic simulation mapping microbial quorum sensing and cellular mitosis using Pygame, with a LangGraph strategic coordination layer, monitored via Langfuse tracing and ClickHouse high-frequency telemetry analytics.

## What is included

- `game0fagents/simulation.py` models microbial quorum sensing and mitosis with symbolic rules plus a simple neural scoring heuristic.
- `LangGraphCoordinator` chooses colony strategy across explore, broadcast, mitosis, and synchronized growth phases.
- `LangfuseTracer` and `ClickHouseTelemetry` capture per-tick trace and telemetry events for high-frequency inspection.
- `PygameRenderer` produces a renderable sprite snapshot for each tick.

## Run

```bash
python -m game0fagents
```

## Test

```bash
python -m unittest discover -s tests
```
