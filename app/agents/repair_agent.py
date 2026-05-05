from __future__ import annotations

from typing import Any, Dict, List


def run_repair_agent(
    device_state: Dict[str, Any],
    log_insights: Dict[str, Any],
    knowledge_result: Dict[str, Any],
    gui_actions: List[Dict[str, Any]],
) -> Dict[str, Any]:
    camera = device_state["living_room_camera"]
    weak_wifi = camera.get("rssi", 0) < -75 or log_insights.get("weak_wifi")
    outdated_firmware = camera.get("firmware_version") != camera.get("latest_firmware")
    stream_timeout = camera.get("last_error") == "STREAM_CONNECT_TIMEOUT" or log_insights.get("error") == "STREAM_CONNECT_TIMEOUT"

    if weak_wifi and outdated_firmware and stream_timeout:
        root_cause = "outdated_firmware_with_weak_wifi"
        root_cause_text = "弱 Wi-Fi 环境叠加旧固件版本，导致远程直播流建立超时。"
    elif weak_wifi:
        root_cause = "weak_wifi_signal"
        root_cause_text = "Wi-Fi 信号弱导致直播流建立不稳定。"
    elif outdated_firmware:
        root_cause = "outdated_firmware"
        root_cause_text = "固件版本较旧，可能导致直播通道兼容性问题。"
    else:
        root_cause = "stream_channel_timeout"
        root_cause_text = "直播流通道超时，需要进一步排查云端或网络链路。"

    repair_actions = ["restart_device", "verify_stream"]
    if outdated_firmware:
        repair_actions.insert(0, "upgrade_firmware")

    recommendations = ["将摄像头移动到距离路由器更近的位置，或优化 2.4GHz Wi-Fi 信道。"]
    if outdated_firmware:
        recommendations.insert(0, f"将固件从 {camera.get('firmware_version')} 升级到 {camera.get('latest_firmware')}。")

    return {
        "root_cause": root_cause,
        "root_cause_text": root_cause_text,
        "repair_actions": repair_actions,
        "expected_result": "video_stream_restored",
        "evidence": [
            f"stream_status={camera.get('stream_status')}",
            f"error={camera.get('last_error')}",
            f"rssi={camera.get('rssi')}",
            f"firmware_version={camera.get('firmware_version')}",
            f"latest_firmware={camera.get('latest_firmware')}",
            *knowledge_result.get("evidence", []),
        ],
        "gui_findings": gui_actions,
        "recommendations": recommendations,
    }

