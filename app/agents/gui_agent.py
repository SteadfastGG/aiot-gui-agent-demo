from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from app.tools.playwright_operator import run_console_diagnosis, run_console_repair


def run_gui_diagnosis_agent(
    console_path: Path,
    device_id: str,
    device_state: Dict[str, Any],
) -> List[Dict[str, Any]]:
    return run_console_diagnosis(console_path, device_id, device_state)


def run_gui_repair_agent(
    console_path: Path,
    device_state_path: Path,
    device_id: str,
    safety_result: Dict[str, Any],
) -> List[Dict[str, Any]]:
    return run_console_repair(console_path, device_state_path, device_id, safety_result)

