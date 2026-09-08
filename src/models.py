from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional


class CellPhase(str, Enum):
    """Reflects the core cellular lifecycle phases from REFERENCE.md"""
    INCUBATING = "incubating"
    MATURE = "mature"
    DISEASED = "diseased"


class ColonyState(str, Enum):
    """Reflects the overall state of a distinct cellular population"""
    GROWING = "growing"
    NEED_MITOSIS = "need_mitosis"
    STAGNANT = "stagnant"

class CellTelemetry(BaseModel):
    """Strict data contract for an individual cell's physical metrics"""
    cell_id: str = Field(..., description="Unique ID combining colony name and index")
    colony_id: str = Field(..., description="Either 'alpha' or 'omega'")
    current_age: int = Field(..., ge=0, description="Age in simulation ticks")
    maturity_pct: float = Field(..., ge=0.0, le=100.0, description="Age percentage relative to max lifespan")
    resource_consumed: float = Field(..., ge=0.0, description="Fractional resource units consumed this tick")


class System(BaseModel):
    """The master macro state packet passed to langGraph and processed by ClickHouse"""
    epoch: int = Field(..., ge=0, description="The current discrete time step of the system")
    global_resource: float = Field(..., description="The total available global resource in the system")
    colony_states: List[CellTelemetry] = Field(..., description="Flat collection of individual cell telemetry data within the colony")
    stagnation_flag: bool = Field(..., description="True if growth is completely locked")


