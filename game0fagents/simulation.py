from __future__ import annotations

from dataclasses import asdict, dataclass, field
from statistics import mean
from typing import Any


@dataclass
class CellAgent:
    identifier: str
    x: float
    y: float
    energy: float
    signal: float
    generation: int = 0


@dataclass
class SimulationSnapshot:
    tick: int
    strategy: str
    quorum_reached: bool
    population: int
    average_signal: float
    average_energy: float
    telemetry_event: dict[str, Any]
    trace_event_names: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LangfuseTracer:
    traces: list[dict[str, Any]] = field(default_factory=list)

    def record(self, name: str, payload: dict[str, Any]) -> None:
        self.traces.append({"name": name, "payload": payload})

    def names(self) -> list[str]:
        return [trace["name"] for trace in self.traces]


@dataclass
class ClickHouseTelemetry:
    events: list[dict[str, Any]] = field(default_factory=list)

    def emit(self, event: dict[str, Any]) -> dict[str, Any]:
        self.events.append(event)
        return event

    def latest(self) -> dict[str, Any] | None:
        return self.events[-1] if self.events else None


@dataclass
class LangGraphCoordinator:
    quorum_threshold: float
    mitosis_threshold: float

    def coordinate(self, cells: list[CellAgent]) -> dict[str, Any]:
        average_signal = mean(cell.signal for cell in cells)
        average_energy = mean(cell.energy for cell in cells)
        quorum_reached = average_signal >= self.quorum_threshold
        can_divide = any(cell.energy >= self.mitosis_threshold for cell in cells)

        if quorum_reached and can_divide:
            strategy = "synchronize-growth"
        elif quorum_reached:
            strategy = "broadcast-signal"
        elif can_divide:
            strategy = "prepare-mitosis"
        else:
            strategy = "explore"

        return {
            "strategy": strategy,
            "quorum_reached": quorum_reached,
            "average_signal": average_signal,
            "average_energy": average_energy,
        }


@dataclass
class PygameRenderer:
    width: int = 640
    height: int = 480

    def render(self, cells: list[CellAgent]) -> dict[str, Any]:
        return {
            "backend": "pygame",
            "width": self.width,
            "height": self.height,
            "sprites": [
                {
                    "id": cell.identifier,
                    "position": (round(cell.x, 2), round(cell.y, 2)),
                    "signal": round(cell.signal, 3),
                    "energy": round(cell.energy, 3),
                }
                for cell in cells
            ],
        }


@dataclass
class NeuroSymbolicSimulation:
    cells: list[CellAgent]
    quorum_threshold: float = 0.65
    mitosis_threshold: float = 1.2
    tracer: LangfuseTracer = field(default_factory=LangfuseTracer)
    telemetry: ClickHouseTelemetry = field(default_factory=ClickHouseTelemetry)
    renderer: PygameRenderer = field(default_factory=PygameRenderer)
    tick: int = 0

    @classmethod
    def default(cls) -> "NeuroSymbolicSimulation":
        return cls(
            cells=[
                CellAgent("cell-0", x=40.0, y=60.0, energy=1.4, signal=0.85),
                CellAgent("cell-1", x=75.0, y=60.0, energy=0.9, signal=0.55),
            ]
        )

    def step(self) -> SimulationSnapshot:
        self.tick += 1
        self.tracer.record("tick.start", {"tick": self.tick, "population": len(self.cells)})

        coordinator = LangGraphCoordinator(
            quorum_threshold=self.quorum_threshold,
            mitosis_threshold=self.mitosis_threshold,
        )
        coordination = coordinator.coordinate(self.cells)
        self.tracer.record("langgraph.strategy", coordination)

        updated_cells: list[CellAgent] = []
        for index, cell in enumerate(self.cells):
            signal_delta = self._neural_signal_delta(cell, coordination["average_signal"])
            next_signal = min(1.0, cell.signal + signal_delta)
            next_energy = cell.energy + (0.2 if coordination["quorum_reached"] else 0.05)

            if next_energy >= self.mitosis_threshold:
                daughter_energy = round(next_energy / 2, 3)
                updated_cells.extend(
                    [
                        CellAgent(
                            identifier=f"{cell.identifier}-a{self.tick}",
                            x=cell.x - 6,
                            y=cell.y + index,
                            energy=daughter_energy,
                            signal=round(next_signal * 0.92, 3),
                            generation=cell.generation + 1,
                        ),
                        CellAgent(
                            identifier=f"{cell.identifier}-b{self.tick}",
                            x=cell.x + 6,
                            y=cell.y - index,
                            energy=daughter_energy,
                            signal=round(next_signal * 0.88, 3),
                            generation=cell.generation + 1,
                        ),
                    ]
                )
            else:
                updated_cells.append(
                    CellAgent(
                        identifier=cell.identifier,
                        x=cell.x + 1.5,
                        y=cell.y,
                        energy=round(next_energy, 3),
                        signal=round(next_signal, 3),
                        generation=cell.generation,
                    )
                )

        self.cells = updated_cells
        render_state = self.renderer.render(self.cells)
        telemetry_event = self.telemetry.emit(
            {
                "tick": self.tick,
                "strategy": coordination["strategy"],
                "population": len(self.cells),
                "average_signal": round(mean(cell.signal for cell in self.cells), 3),
                "average_energy": round(mean(cell.energy for cell in self.cells), 3),
                "renderer": render_state["backend"],
            }
        )
        self.tracer.record("clickhouse.telemetry", telemetry_event)
        self.tracer.record("tick.complete", {"tick": self.tick, "population": len(self.cells)})

        return SimulationSnapshot(
            tick=self.tick,
            strategy=coordination["strategy"],
            quorum_reached=coordination["quorum_reached"],
            population=len(self.cells),
            average_signal=telemetry_event["average_signal"],
            average_energy=telemetry_event["average_energy"],
            telemetry_event=telemetry_event,
            trace_event_names=self.tracer.names()[-4:],
        )

    @staticmethod
    def _neural_signal_delta(cell: CellAgent, average_signal: float) -> float:
        symbolic_boost = 0.08 if average_signal >= cell.signal else 0.03
        return round((cell.energy * 0.04) + symbolic_boost, 3)
