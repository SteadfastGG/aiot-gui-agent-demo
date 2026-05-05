from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def write_text_report(output_dir: Path, filename: str, content: str) -> str:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename
    output_path.write_text(content, encoding="utf-8")
    return str(output_path)


def write_json_report(output_dir: Path, filename: str, payload: Dict[str, Any]) -> str:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(output_path)


def render_action_log(actions: list[Dict[str, Any]]) -> str:
    lines = ["# GUI 操作日志", ""]
    for index, action in enumerate(actions, start=1):
        result = action.get("result", "unknown")
        evidence = action.get("evidence", "")
        reason = action.get("reason", "")
        lines.append(
            f"{index}. `{action.get('action')}` -> {result}"
            + (f"；证据：{evidence}" if evidence else "")
            + (f"；原因：{reason}" if reason else "")
        )
    return "\n".join(lines) + "\n"

