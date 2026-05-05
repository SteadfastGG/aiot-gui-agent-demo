from __future__ import annotations

from typing import Any, Dict


def run_device_graph_agent(device_id: str, fault_type: str, device_state: Dict[str, Any]) -> Dict[str, Any]:
    camera = device_state.get("living_room_camera", {})
    router = device_state.get("home_router", {})
    risk_links = []

    if camera.get("rssi", 0) < -75:
        risk_links.append("camera_to_router_signal")
    if camera.get("stream_status") == "failed":
        risk_links.append("camera_to_cloud_stream")
    if router.get("blocked_ports"):
        risk_links.append("router_video_ports")

    mermaid = "\n".join(
        [
            "graph TD",
            "A[米家 App] --> B[云鉴权服务]",
            "B --> C[客厅摄像头]",
            "C --> D[家庭路由器]",
            "D --> E[外部网络]",
            "C -. 弱信号 .-> D",
            "C -. 直播流超时 .-> B",
        ]
    )

    return {
        "root_device": device_id,
        "fault_type": fault_type,
        "related_nodes": [
            "mi_home_app",
            "cloud_auth_service",
            "living_room_camera",
            "home_router",
            "external_network",
        ],
        "critical_path": [
            "mi_home_app",
            "cloud_auth_service",
            "living_room_camera",
            "home_router",
            "external_network",
        ],
        "risk_links": risk_links,
        "mermaid": mermaid,
        "summary": "风险集中在摄像头到路由器的弱信号链路，以及摄像头到云端的视频流建立链路。",
    }

