import json
from typing import TypedDict

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langfuse import observe


QUORUM_SYSTEM_PROMPT = """You are a quorum sensing coordinator for a bacterial colony simulation \
(Conway's Game of Life with biological extensions).

You monitor colony telemetry and decide on interventions, just like real bacteria \
use autoinducer molecules to coordinate group behavior.

Given the colony's current state and recent history, choose ONE action:

- NUTRIENT_BOOST: Seed new cells in sparse areas. Use when density is below 5% or \
the colony is declining steadily. (Biology: nutrient chemotaxis)
- PHAGE_CULL: Remove cells from the densest region. Use when density exceeds 40% or \
growth is explosive. (Biology: bacteriophage predation / contact inhibition)
- HOMEOSTASIS: No intervention. The colony is self-regulating. \
(Biology: quorum at steady-state)
- SPORULATION: Emergency reproduction burst — scatter cells randomly. Use when the \
population has crashed below 2% or is near extinction. \
(Biology: endospore formation under starvation)

Respond with ONLY valid JSON (no markdown fences):
{"decision": "<ACTION>", "reasoning": "<one sentence biological justification>"}"""


class QuorumState(TypedDict):
    board_summary: str
    telemetry_history: str
    decision: str
    reasoning: str


@observe(name="quorum_sensing")
def analyze_colony(state: QuorumState) -> QuorumState:
    llm = ChatAnthropic(
        model="claude-sonnet-5-5"
    )

    prompt = (
        f"Current colony state:\n{state['board_summary']}\n\n"
        f"Recent telemetry (last 10 epochs):\n{state['telemetry_history']}"
    )

    print(f"[workflow] Invoking Claude with board summary:\n{state['board_summary']}")
    response = llm.invoke(
        [SystemMessage(content=QUORUM_SYSTEM_PROMPT), HumanMessage(content=prompt)],
    )
    raw = response.content
    if isinstance(raw, list):
        raw = next(block["text"] for block in raw if block.get("type") == "text")
    print(f"[workflow] Raw response: {raw}")

    try:
        result = json.loads(raw)
        print(f"[workflow] Parsed decision: {result}")
        return {
            **state,
            "decision": result.get("decision", "HOMEOSTASIS"),
            "reasoning": result.get("reasoning", "No reasoning provided"),
        }
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"[workflow] Failed to parse response: {e}")
        return {
            **state,
            "decision": "HOMEOSTASIS",
            "reasoning": "Failed to parse LLM response — defaulting to no intervention",
        }


def build_graph():
    builder = StateGraph(QuorumState)
    builder.add_node("analyze", analyze_colony)
    builder.add_edge(START, "analyze")
    builder.add_edge("analyze", END)
    return builder.compile()


graph = build_graph()
