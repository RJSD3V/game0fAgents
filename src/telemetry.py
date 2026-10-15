from datetime import datetime, timezone
import clickhouse_connect
import numpy as np


class Telemetry:
    def __init__(self, host="localhost", port=8123, database="symbiosis",
                 username="clickhouse", password="clickhouse"):
        self.client = clickhouse_connect.get_client(
            host=host, port=port, database=database,
            username=username, password=password,
        )
        self.epoch = 0
        self._prev_alive = 0

    def record(self, grid: np.ndarray, ai_decision: str = "", ai_reasoning: str = ""):
        alive = int(grid.sum())
        total = grid.size
        density = alive / total if total > 0 else 0.0
        births = max(0, alive - self._prev_alive)
        deaths = max(0, self._prev_alive - alive)

        self.client.insert(
            "epoch_telemetry",
            [[
                self.epoch,
                datetime.now(timezone.utc),
                alive,
                total,
                density,
                births,
                deaths,
                ai_decision,
                ai_reasoning,
            ]],
            column_names=[
                "epoch", "timestamp", "alive_count", "total_cells",
                "density", "births", "deaths", "ai_decision", "ai_reasoning",
            ],
        )

        self._prev_alive = alive
        self.epoch += 1

    def recent_history(self, limit: int = 20) -> list[dict]:
        result = self.client.query(
            "SELECT epoch, alive_count, total_cells, density, births, deaths, "
            "ai_decision, ai_reasoning "
            "FROM epoch_telemetry ORDER BY epoch DESC LIMIT {limit:UInt32}",
            parameters={"limit": limit},
        )
        rows = []
        for row in result.result_rows:
            rows.append({
                "epoch": row[0],
                "alive_count": row[1],
                "total_cells": row[2],
                "density": round(row[3], 4),
                "births": row[4],
                "deaths": row[5],
                "ai_decision": row[6],
                "ai_reasoning": row[7],
            })
        return rows

    def clear(self):
        self.client.command("TRUNCATE TABLE epoch_telemetry")
        self.epoch = 0
        self._prev_alive = 0
