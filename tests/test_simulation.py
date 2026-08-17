import unittest

from game0fagents import CellAgent, NeuroSymbolicSimulation


class NeuroSymbolicSimulationTests(unittest.TestCase):
    def test_langgraph_strategy_reflects_quorum_and_mitosis(self) -> None:
        simulation = NeuroSymbolicSimulation.default()

        snapshot = simulation.step()

        self.assertEqual(snapshot.strategy, "synchronize-growth")
        self.assertTrue(snapshot.quorum_reached)
        self.assertEqual(snapshot.population, len(simulation.cells))
        self.assertEqual(
            sorted(cell.identifier for cell in simulation.cells),
            [f"cell-0-a{snapshot.tick}", f"cell-0-b{snapshot.tick}", "cell-1"],
        )

    def test_step_emits_clickhouse_telemetry_and_langfuse_trace_events(self) -> None:
        simulation = NeuroSymbolicSimulation(
            cells=[CellAgent("cell-x", x=0.0, y=0.0, energy=0.8, signal=0.4)]
        )

        snapshot = simulation.step()

        self.assertEqual(snapshot.telemetry_event["renderer"], "pygame")
        self.assertEqual(snapshot.telemetry_event["population"], 1)
        self.assertEqual(
            snapshot.trace_event_names,
            ["tick.start", "langgraph.strategy", "clickhouse.telemetry", "tick.complete"],
        )

    def test_mitosis_creates_distinct_daughter_cells(self) -> None:
        simulation = NeuroSymbolicSimulation(
            cells=[CellAgent("cell-z", x=12.0, y=15.0, energy=1.3, signal=0.7)]
        )
        self.assertEqual(simulation.cells[0].generation, 0)

        simulation.step()

        self.assertEqual(len(simulation.cells), 2)
        self.assertNotEqual(simulation.cells[0].identifier, simulation.cells[1].identifier)
        self.assertNotEqual(simulation.cells[0].y, simulation.cells[1].y)
        self.assertTrue(all(cell.generation == 1 for cell in simulation.cells))


if __name__ == "__main__":
    unittest.main()
