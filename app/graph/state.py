from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, TypedDict


StageStatus = Literal["waiting", "running", "completed", "failed", "blocked"]


class WorkflowState(TypedDict, total=False):
    task_id: str
    user_issue: str
    status: StageStatus
    current_stage: str
    stage_statuses: Dict[str, StageStatus]
    device_id: Optional[str]
    fault_type: Optional[str]
    severity: Optional[str]
    triage_result: Optional[Dict[str, Any]]
    device_state: Optional[Dict[str, Any]]
    log_insights: Optional[Dict[str, Any]]
    device_graph: Optional[Dict[str, Any]]
    retrieved_knowledge: Optional[str]
    knowledge_result: Optional[Dict[str, Any]]
    gui_actions: List[Dict[str, Any]]
    repair_plan: Optional[Dict[str, Any]]
    safety_result: Optional[Dict[str, Any]]
    user_report: Optional[str]
    engineer_report: Optional[str]
    diagnosis_trace: Optional[str]
    output_files: Dict[str, str]
    iteration: int
    max_iterations: int
    errors: List[str]


STAGES = [
    "triage",
    "device_state",
    "log_parser",
    "device_graph",
    "knowledge",
    "gui_diagnosis",
    "repair",
    "safety_review",
    "gui_repair",
    "report",
]


def initial_stage_statuses() -> Dict[str, StageStatus]:
    return {stage: "waiting" for stage in STAGES}

