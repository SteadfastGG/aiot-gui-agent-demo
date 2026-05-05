from __future__ import annotations

from typing import Any, Dict

from app.tools.safety_rules import review_actions


def run_safety_reviewer_agent(repair_plan: Dict[str, Any]) -> Dict[str, Any]:
    actions = repair_plan.get("repair_actions", [])
    return review_actions(actions, simulated_confirmation=True)

