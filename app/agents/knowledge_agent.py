from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable

from app.tools.rag_retriever import format_retrieved_documents, retrieve_knowledge


def run_knowledge_agent(
    user_issue: str,
    fault_type: str,
    device_state: Dict[str, Any],
    log_insights: Dict[str, Any],
    kb_paths: Iterable[Path],
) -> Dict[str, Any]:
    camera = device_state.get("living_room_camera", {})
    query = " ".join(
        [
            user_issue,
            fault_type,
            str(log_insights.get("error", "")),
            f"rssi {camera.get('rssi')}",
            f"firmware {camera.get('firmware_version')} {camera.get('latest_firmware')}",
            "固件 升级 弱网 直播 加载失败 安全",
        ]
    )
    documents = retrieve_knowledge(query, kb_paths)
    retrieved = format_retrieved_documents(documents)

    candidate_causes = []
    if camera.get("rssi", 0) < -75:
        candidate_causes.append("Wi-Fi 信号弱，RSSI 低于 -75，直播流建立容易超时。")
    if camera.get("firmware_version") != camera.get("latest_firmware"):
        candidate_causes.append("摄像头固件版本较旧，可能缺少弱网直播兼容性修复。")
    if camera.get("cloud_auth") == "normal":
        candidate_causes.append("云鉴权正常，鉴权异常不是优先根因。")
    if camera.get("privacy_mode") is False:
        candidate_causes.append("隐私模式未开启，排除隐私遮挡导致的无画面。")

    return {
        "retrieved_knowledge": retrieved,
        "documents": [doc.__dict__ for doc in documents],
        "candidate_causes": candidate_causes,
        "evidence": [
            log_insights.get("summary", ""),
            f"stream_status={camera.get('stream_status')}",
            f"last_error={camera.get('last_error')}",
        ],
        "recommended_order": [
            "run_network_check",
            "check_firmware",
            "upgrade_firmware",
            "restart_device",
            "verify_stream",
        ],
        "risk_tips": [
            "固件升级必须经过用户确认。",
            "诊断过程不访问或导出用户视频。",
        ],
    }

