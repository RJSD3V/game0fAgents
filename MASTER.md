# 🧬 The Symbiosis Engine: Negotiating Cellular Growth at Matrix Scale
### 🎮 GitHub Repository Name: `game-of-agents`
### 🚀 A Split-Horizon Hybrid Framework for High-Throughput Cellular Automata

---

## 📌 Executive Summary
**The Symbiosis Engine** is a hybrid neuro-symbolic simulation project designed to model resource coordination and sustainable cellular growth. 

Putting an LLM inside a fast physical loop causes execution to lag and crash. Relying purely on traditional video game math removes strategic flexibility. This project resolves that challenge using a **Split-Horizon Architecture**:
1. **High-Speed Execution Layer (Micro-Steps / Epochs)**: A streamlined, single-colony 2D cellular automata engine (inspired by Conway’s Game of Life) handles fast, sub-second cell growth, overcrowding, and localized starvation decay based on randomized food cell spawns.
2. **High-Level Coordination Layer (Macro-Steps)**: A stateful **LangGraph** orchestration workflow acts as an artificial chemical signaling network (Quorum Sensing). It pauses the grid to enforce macroeconomic "Fasting Directives" when cellular expansion threatens environmental resource collapse.

To validate this high-throughput pipeline, **ClickHouse** acts as a high-speed telemetry black box recording individual cellular metabolism metrics under a variable **Dynamic Time-Warp Controller**, while **Langfuse** instruments and monitors the prompt logic, latency, and operational cost of the AI treaties.

---

## 📚 Academic Research Foundations & Citation Links

This architecture aligns directly with cutting-edge academic paradigms bridging language processing, cellular arrays, and high-frequency analytical data logging:

*   **Training Language Models via Neural Cellular Automata (MIT / Columbia University)**: Recent deep learning research proves that training transformer models to interpret 2D spatial layouts and grid mechanics builds advanced, robust token-reasoning pathways. Read the full paper layout here: [Training Language Models via Neural Cellular Automata (arXiv)](https://arxiv.org/html/2603.10055v1).
*   **LLM-Driven Spatial Macro-Coordination**: Academic engineering frameworks increasingly utilize split-horizon workloads where localized, high-speed physics remain in a matrix grid while a stateful LLM layer directs macro policy rules during system anomalies. Read the implementation design here: [Large-Language-Model-Driven Agents for Spatial Evacuation (ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S0925753525001602).
*   **LifeGPT & The Computational Conway Engine (Nature)**: This baseline research trained large generative transformers to process discrete multi-agent time-series steps inside Conway's Game of Life. Read the publication review here: [LifeGPT: Generative Pre-training on Cellular Automata (Nature)](https://www.nature.com/articles/s44387-025-00014-w).

---

## 🧬 Biological Core Concepts & Science Mapping

The project translates real-world microbiological pathways into deterministic software design choices:

```
REAL-WORLD MICROBIOLOGY         ==►    SIMULATION ENGINE ARCHITECTURE
-----------------------                ------------------------------
Density-Dependent Crowding             Conway's 8-Neighbor Rules (Death by Overcrowding)
Inter-Species Quorum Sensing           LangGraph Stateful Policy Nodes
The Stringent Response                 Growth Stagnation Phase (Forced Fasting Loop)
Cellular Lysis (Disintegration)        Starvation Multiplier Event (Max Step Limit)
Metabolic Energy Sizing                Dynamic Age-Fraction Allocation Formula
```

### 1. Quorum Sensing & Policy Regulation
In nature, cell colonies track population density by releasing and measuring chemical signaling molecules. Once a crowd threshold is breached, they coordinate resource consumption. In this project, **LangGraph** models this biochemical feedback loop as a stateful, symbolic coordinator that can issue a global `allowed_to_eat = False` constraint.

### 2. Age-Based Fractional Allocation
Cellular nutrient absorption changes with cell maturity. This project implements a precise floating-point resource-draw rule tied to the individual cell's lifecycle percentage:
$$\text{Maturity Fraction } (P) = \frac{\text{Current Age}}{\text{Max Age}}$$
$$\text{Individual Resource Consumed} = 1.0 \times P$$

*   **Young/Incubating Cell ($10\%$ lifespan)**: Draws only $0.1$ units of its allocation slice.
*   **Fully Mature Cell ($100\%$ lifespan)**: Draws the full $1.0$ unit slice to fuel cell structures.

---

## 🏗️ System Architecture & Data Flow

```
     [Single Cell Colony Expands] 
                  │
                  ▼
   [Grid Population Satures/Spikes] ──► (Pause Matrix Loop) ──► [LangGraph Quorum Node]
                                                                       │ (Enforces Fasting Directive)
                                                                       ▼
[ClickHouse DB Ingestion] ◄── (Execute Cell Step) ◄── [Langfuse Audit Trail]
(Saved: Granular Telemetry     (Cells Bypasses Food,       (Saved: Traces, Prompt Tokens,
 Rows at Cell Level)            Starvation Counter Ticks)   LLM Decision Latency)
```

### The ClickHouse Stress Test (Dynamic Time-Warp Controller)
To demonstrate the capabilities of a columnar data store over row-based structures, the framework implements an adjustable `current_time_warp` variable (e.g., 1x, 50x, 200x). 
* When accelerated to 200x, the engine processes 200 micro-epochs behind the scenes before drawing a single frame in Pygame.
* Because telemetry is logged at the **individual cell level** rather than aggregated by colony, a single visual frame generates tens of thousands of floating-point records seamlessly, creating a massive ingestion stress-test.

---

## 📂 Repository File Directory

```text
game-of-agents/
│
├── config/
│   └── docker-compose.yml       # Provisions local ClickHouse cluster instance
│
├── src/
│   ├── __init__.py
│   ├── models.py                # Pydantic data schemas for data type validation
│   ├── cells.py                 # Object-Oriented Cell definitions & metabolism functions
│   ├── engine.py                # Grid matrix computation & Temporal Time-Warp loops
│   ├── database.py              # ClickHouse batch injection streaming client
│   ├── agents.py                # LangGraph nodes and Langfuse tracer wrappers
│   └── main.py                  # Pygame graphical UI dashboard entry point
│
├── requirements.txt             # Project library package configurations
└── README.md                    # Core documentation landing page
```

---

## ⚙️ Data Engineering & Infrastructure Contracts

### 1. Pydantic Verification Structures (`src/models.py`)
```python
from pydantic import BaseModel, Field
from enum import Enum

class CellPhase(str, Enum):
    INCUBATING = "incubating"
    MATURE = "mature"
    DISEASED = "diseased"

class CellTelemetrySchema(BaseModel):
    timestamp_ns: int
    epoch: int
    cell_id: str
    neighbor_count: int = Field(..., ge=0, le=8)
    steps_since_last_meal: int = Field(..., ge=0)
    fasting_enforced: int = Field(..., ge=0, le=1) # 1 if AI blocked consumption
```

### 2. High-Frequency ClickHouse Table Architecture (`config/`)
```sql
CREATE TABLE cell_telemetry (
    timestamp_ns Int64,
    epoch UInt32,
    cell_id String,
    neighbor_count UInt8,
    steps_since_last_meal UInt16,
    fasting_enforced UInt8
) ENGINE = MergeTree()
ORDER BY (epoch, timestamp_ns, cell_id);
```

---

## 🖥️ Live Presentation Analytical Showcases

During live evaluation runs, the power of **Langfuse** and **ClickHouse** can be demonstrated by shifting the dynamic time-warp control parameters:

### A. The Ingestion Flood (Throttling the Time Warp)
*   **1x Speed**: Point to the database logs showing a clean baseline row ingestion rate.
*   **200x Speed**: Crank the time-warp multiplier. Let the board blur with rapid evolution and show the total row count instantly jump by **250,000+ rows** in seconds, proving ClickHouse streams high-velocity micro-logs without dropping visual frames.

### B. The ClickHouse Query Analytics (High-Throughput Telemetry)
Run these commands live in a terminal window to scan thousands of rows in milliseconds:

*   **Query 1: Dynamic Foraging & Hunger Index**
    ```sql
    SELECT cell_id, AVG(steps_since_last_meal) AS average_hunger, MAX(epoch) AS lifespan 
    FROM cell_telemetry 
    GROUP BY cell_id ORDER BY average_hunger DESC LIMIT 10;
    ```
*   **Query 2: Identifying AI Treaty Sacrifices**
    ```sql
    SELECT epoch, COUNT(*) AS starvation_deaths_by_treaty 
    FROM cell_telemetry 
    WHERE steps_since_last_meal >= 20 AND fasting_enforced = 1
    GROUP BY epoch ORDER BY epoch DESC LIMIT 5;
    ```
