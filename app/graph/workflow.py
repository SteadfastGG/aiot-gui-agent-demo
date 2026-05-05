from __future__ import annotations

import uuid
from typing import Any, Callable

from app.agents.device_graph_agent import run_device_graph_agent
from app.agents.gui_agent import run_gui_diagnosis_agent, run_gui_repair_agent
from app.agents.knowledge_agent import run_knowledge_agent
from app.agents.repair_agent import run_repair_agent
from app.agents.report_agent import run_report_agent
from app.agents.safety_reviewer_agent import run_safety_reviewer_agent
from app.agents.triage_agent import run_triage_agent
from app.config import PROJECT_ROOT, settings
from app.graph.state import WorkflowState, initial_stage_statuses
from app.tools.device_state import load_device_state, reset_device_state
from app.tools.log_parser import parse_device_log


def run_diagnosis_workflow(user_issue: str, task_id: str | None = None) -> WorkflowState:
    task_id = task_id or f"task_{uuid.uuid4().hex[:8]}"
    state: WorkflowState = {
        "task_id": task_id,
        "user_issue": user_issue,
        "status": "running",
        "current_stage": "triage",
        "stage_statuses": initial_stage_statuses(),
        "device_id": None,
        "fault_type": None,
        "severity": None,
        "triage_result": None,
        "device_state": None,
        "log_insights": None,
        "device_graph": None,
        "retrieved_knowledge": None,
        "knowledge_result": None,
        "gui_actions": [],
        "repair_plan": None,
        "safety_result": None,
        "user_report": None,
        "engineer_report": None,
        "diagnosis_trace": None,
        "output_files": {},
        "iteration": 0,
        "max_iterations": settings.max_iterations,
        "errors": [],
    }

    try:
        if settings.reset_state_before_run:
            reset_device_state(settings.device_state_path)

        _run_stage(state, "triage", lambda: _triage(state))
        _run_stage(state, "device_state", lambda: _load_state(state))
        _run_stage(state, "log_parser", lambda: _parse_logs(state))
        _run_stage(state, "device_graph", lambda: _device_graph(state))
        _run_stage(state, "knowledge", lambda: _knowledge(state))
        _run_stage(state, "gui_diagnosis", lambda: _gui_diagnosis(state))
        _run_stage(state, "repair", lambda: _repair(state))
        _run_stage(state, "safety_review", lambda: _safety_review(state))
        _run_stage(state, "gui_repair", lambda: _gui_repair(state))
        _run_stage(state, "report", lambda: _report(state))
        state["status"] = "completed"
        state["current_stage"] = "completed"
    except Exception as exc:
        state["status"] = "failed"
        state["errors"].append(f"{exc.__class__.__name__}: {exc}")
        if state.get("current_stage"):
            state["stage_statuses"][state["current_stage"]] = "failed"
    return state


def _run_stage(state: WorkflowState, stage: str, fn: Callable[[], None]) -> None:
    state["current_stage"] = stage
    state["stage_statuses"][stage] = "running"
    fn()
    state["stage_statuses"][stage] = "completed"


def _triage(state: WorkflowState) -> None:
    triage = run_triage_agent(state["user_issue"])
    state["triage_result"] = triage
    state["device_id"] = triage["device_id"]
    state["fault_type"] = triage["fault_type"]
    state["severity"] = triage["severity"]


def _load_state(state: WorkflowState) -> None:
    state["device_state"] = load_device_state(settings.device_state_path)


def _parse_logs(state: WorkflowState) -> None:
    device_id = _require(state, "device_id")
    log_path = PROJECT_ROOT / "data" / "device_logs" / f"{device_id}.log"
    state["log_insights"] = parse_device_log(log_path)


def _device_graph(state: WorkflowState) -> None:
    state["device_graph"] = run_device_graph_agent(
        _require(state, "device_id"),
        _require(state, "fault_type"),
        _require(state, "device_state"),
    )


def _knowledge(state: WorkflowState) -> None:
    result = run_knowledge_agent(
        state["user_issue"],
        _require(state, "fault_type"),
        _require(state, "device_state"),
        _require(state, "log_insights"),
        [settings.knowledge_base_path, settings.historical_tickets_path],
    )
    state["knowledge_result"] = result
    state["retrieved_knowledge"] = result["retrieved_knowledge"]


def _gui_diagnosis(state: WorkflowState) -> None:
    actions = run_gui_diagnosis_agent(
        settings.mock_console_path,
        _require(state, "device_id"),
        _require(state, "device_state"),
    )
    state["gui_actions"].extend(actions)


def _repair(state: WorkflowState) -> None:
    state["repair_plan"] = run_repair_agent(
        _require(state, "device_state"),
        _require(state, "log_insights"),
        _require(state, "knowledge_result"),
        state["gui_actions"],
    )


def _safety_review(state: WorkflowState) -> None:
    state["safety_result"] = run_safety_reviewer_agent(_require(state, "repair_plan"))
    if not state["safety_result"].get("approved"):
        state["stage_statuses"]["gui_repair"] = "blocked"


def _gui_repair(state: WorkflowState) -> None:
    actions = run_gui_repair_agent(
        settings.mock_console_path,
        settings.device_state_path,
        _require(state, "device_id"),
        _require(state, "safety_result"),
    )
    state["gui_actions"].extend(actions)
    state["device_state"] = load_device_state(settings.device_state_path)


def _report(state: WorkflowState) -> None:
    result = run_report_agent(state, settings.output_path)
    state["user_report"] = result["user_report"]
    state["engineer_report"] = result["engineer_report"]
    state["diagnosis_trace"] = result["diagnosis_trace"]
    state["output_files"] = result["output_files"]


def _require(state: WorkflowState, key: str) -> Any:
    value = state.get(key)
    if value is None:
        raise ValueError(f"Workflow state missing required key: {key}")
    return value

