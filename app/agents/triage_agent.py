from __future__ import annotations

from typing import Any, Dict


def run_triage_agent(user_issue: str) -> Dict[str, Any]:
    normalized = user_issue.lower()
    device_id = "living_room_camera"
    fault_type = "video_stream_unavailable"

    if "路由器" in user_issue or "router" in normalized:
        device_id = "home_router"
        fault_type = "network_quality_issue"
    if "摄像头" in user_issue or "camera" in normalized:
        device_id = "living_room_camera"
    if any(keyword in user_issue for keyword in ["直播", "画面", "远程查看", "加载失败"]):
        fault_type = "video_stream_unavailable"

    return {
        "device_id": device_id,
        "fault_type": fault_type,
        "severity": "medium",
        "symptoms": [
            "device_online",
            "remote_stream_loading_failed",
            "app_reports_online",
        ],
        "possible_causes": [
            "weak_wifi_signal",
            "outdated_firmware",
            "cloud_auth_issue",
            "stream_channel_timeout",
            "privacy_mode_enabled",
        ],
        "next_agents": [
            "device_graph_agent",
            "knowledge_agent",
            "gui_agent",
            "repair_agent",
            "safety_reviewer_agent",
            "report_agent",
        ],
    }

