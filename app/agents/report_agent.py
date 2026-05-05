from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from app.tools.report_writer import render_action_log, write_json_report, write_text_report


def run_report_agent(state: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
    user_report = _build_user_report(state)
    engineer_report = _build_engineer_report(state)
    diagnosis_trace = _build_diagnosis_trace(state)
    action_log = render_action_log(state.get("gui_actions", []))

    output_files = {
        "user_report": write_text_report(output_dir, "user_report.md", user_report),
        "engineer_report": write_text_report(output_dir, "engineer_report.md", engineer_report),
        "diagnosis_trace": write_text_report(output_dir, "diagnosis_trace.md", diagnosis_trace),
        "gui_action_log": write_text_report(output_dir, "gui_action_log.md", action_log),
        "workflow_state": write_json_report(output_dir, "workflow_state.json", state),
    }
    return {
        "user_report": user_report,
        "engineer_report": engineer_report,
        "diagnosis_trace": diagnosis_trace,
        "output_files": output_files,
    }


def _build_user_report(state: Dict[str, Any]) -> str:
    repair_plan = state["repair_plan"]
    safety_result = state["safety_result"]
    final_device = state["device_state"]["living_room_camera"]
    lines = [
        "# 设备诊断结果",
        "",
        "已完成对客厅摄像头的自动诊断与模拟修复。",
        "",
        "## 问题原因",
        "",
        repair_plan["root_cause_text"],
        "",
        "## 已执行操作",
        "",
        "- 完成网络检测",
        "- 完成固件检查",
    ]
    if "upgrade_firmware" in repair_plan["repair_actions"]:
        lines.append("- 在模拟用户确认后完成固件升级")
    lines.extend(
        [
            "- 完成设备重启",
            "- 完成直播状态验证",
            "",
            "## 当前结果",
            "",
            f"- 直播状态：{final_device.get('stream_status')}",
            f"- 当前固件：{final_device.get('firmware_version')}",
            f"- 安全审查：{safety_result.get('comment')}",
            "",
            "## 建议",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in repair_plan.get("recommendations", []))
    return "\n".join(lines) + "\n"


def _build_engineer_report(state: Dict[str, Any]) -> str:
    repair_plan = state["repair_plan"]
    log_insights = state["log_insights"]
    device_graph = state["device_graph"]
    safety_result = state["safety_result"]
    device = state["device_state"]["living_room_camera"]
    gui_actions: List[Dict[str, Any]] = state.get("gui_actions", [])

    lines = [
        "# 工程师诊断报告",
        "",
        "## 故障类型",
        "",
        str(state.get("fault_type")),
        "",
        "## 关键证据",
        "",
        f"- stream_status = {device.get('stream_status')}",
        f"- last_error = {log_insights.get('error')}",
        f"- rssi = {log_insights.get('rssi')}",
        f"- firmware_version = {log_insights.get('firmware_version')}",
        f"- latest_firmware = {log_insights.get('latest_firmware')}",
        f"- cloud_auth = {log_insights.get('cloud_auth')}",
        "",
        "## 根因判断",
        "",
        repair_plan["root_cause_text"],
        "",
        "## 设备关系风险链路",
        "",
        ", ".join(device_graph.get("risk_links", [])) or "未发现明确风险链路",
        "",
        "## GUI 操作链路",
        "",
    ]
    lines.extend(
        f"{index}. `{action.get('action')}` -> {action.get('result')} ({action.get('evidence')})"
        for index, action in enumerate(gui_actions, start=1)
    )
    lines.extend(
        [
            "",
            "## 安全审查",
            "",
            f"- approved = {safety_result.get('approved')}",
            f"- risk_level = {safety_result.get('risk_level')}",
            f"- requires_user_confirmation = {safety_result.get('requires_user_confirmation')}",
            f"- comment = {safety_result.get('comment')}",
            "",
            "## Mermaid 关系图",
            "",
            "```mermaid",
            device_graph.get("mermaid", ""),
            "```",
        ]
    )
    return "\n".join(lines) + "\n"


def _build_diagnosis_trace(state: Dict[str, Any]) -> str:
    stage_statuses = state.get("stage_statuses", {})
    lines = [
        "# 诊断执行链路",
        "",
        f"- 任务 ID：{state.get('task_id')}",
        f"- 用户问题：{state.get('user_issue')}",
        f"- 设备 ID：{state.get('device_id')}",
        f"- 故障类型：{state.get('fault_type')}",
        "",
        "## Agent 状态",
        "",
    ]
    lines.extend(f"- {stage}: {status}" for stage, status in stage_statuses.items())
    lines.extend(
        [
            "",
            "## 分诊结果",
            "",
            f"```json\n{state.get('triage_result')}\n```",
            "",
            "## 日志摘要",
            "",
            state.get("log_insights", {}).get("summary", ""),
            "",
            "## 知识检索",
            "",
            state.get("retrieved_knowledge", ""),
        ]
    )
    return "\n".join(lines) + "\n"

