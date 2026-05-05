from __future__ import annotations

import uuid
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.config import settings
from app.graph.workflow import run_diagnosis_workflow
from app.tools.device_state import load_device_state, reset_device_state


app = FastAPI(
    title="AIoT GUI Agent Demo API",
    version="0.1.0",
    description="A runnable demo for AIoT device diagnosis and simulated GUI repair.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://127.0.0.1", "http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TASKS: Dict[str, Dict[str, Any]] = {}


class CreateTaskRequest(BaseModel):
    user_issue: str = Field(..., min_length=4)


class TaskSummary(BaseModel):
    task_id: str
    status: str
    current_stage: str
    device_id: str | None = None
    fault_type: str | None = None


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> Dict[str, str]:
    return {"status": "ready"}


@app.post("/diagnosis/tasks", response_model=TaskSummary)
def create_task(payload: CreateTaskRequest) -> TaskSummary:
    task_id = f"task_{uuid.uuid4().hex[:8]}"
    TASKS[task_id] = {
        "task_id": task_id,
        "user_issue": payload.user_issue,
        "status": "created",
        "current_stage": "created",
    }
    return TaskSummary(**TASKS[task_id])


@app.post("/diagnosis/tasks/{task_id}/run", response_model=TaskSummary)
def run_task(task_id: str) -> TaskSummary:
    task = TASKS.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    state = run_diagnosis_workflow(task["user_issue"], task_id=task_id)
    TASKS[task_id] = state
    return _summary_from_state(state)


@app.post("/diagnosis/run")
def run_task_direct(payload: CreateTaskRequest) -> Dict[str, Any]:
    task_id = f"task_{uuid.uuid4().hex[:8]}"
    state = run_diagnosis_workflow(payload.user_issue, task_id=task_id)
    TASKS[task_id] = state
    return state


@app.get("/diagnosis/tasks/{task_id}")
def get_task(task_id: str) -> Dict[str, Any]:
    task = TASKS.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.get("/diagnosis/tasks/{task_id}/reports")
def get_reports(task_id: str) -> Dict[str, Any]:
    task = TASKS.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.get("status") != "completed":
        raise HTTPException(status_code=409, detail="Task is not completed")
    return {
        "task_id": task_id,
        "user_report": task.get("user_report"),
        "engineer_report": task.get("engineer_report"),
        "diagnosis_trace": task.get("diagnosis_trace"),
        "output_files": task.get("output_files", {}),
    }


@app.get("/device-state")
def get_device_state() -> Dict[str, Any]:
    return load_device_state(settings.device_state_path)


@app.post("/device-state/reset")
def reset_state() -> Dict[str, Any]:
    return reset_device_state(settings.device_state_path)


def _summary_from_state(state: Dict[str, Any]) -> TaskSummary:
    return TaskSummary(
        task_id=state["task_id"],
        status=state["status"],
        current_stage=state["current_stage"],
        device_id=state.get("device_id"),
        fault_type=state.get("fault_type"),
    )

