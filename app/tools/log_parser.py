from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict


KV_PATTERN = re.compile(r"(\w+)=([^\s]+)")
TIMESTAMP_PATTERN = re.compile(r"^\[(?P<timestamp>[^\]]+)\]")


def parse_device_log(log_path: Path) -> Dict[str, Any]:
    if not log_path.exists():
        return {
            "log_path": str(log_path),
            "events": [],
            "error": None,
            "rssi": None,
            "firmware_version": None,
            "latest_firmware": None,
            "cloud_auth": None,
            "privacy_mode": None,
            "summary": "设备日志文件不存在。",
        }

    events = []
    insights: Dict[str, Any] = {
        "log_path": str(log_path),
        "events": events,
        "error": None,
        "rssi": None,
        "firmware_version": None,
        "latest_firmware": None,
        "cloud_auth": None,
        "privacy_mode": None,
    }

    for line in log_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        timestamp_match = TIMESTAMP_PATTERN.search(line)
        kv_pairs = dict(KV_PATTERN.findall(line))
        event = {
            "timestamp": timestamp_match.group("timestamp") if timestamp_match else None,
            "raw": line,
            "fields": kv_pairs,
        }
        events.append(event)

        if "error" in kv_pairs:
            insights["error"] = kv_pairs["error"]
        if "rssi" in kv_pairs:
            try:
                insights["rssi"] = int(kv_pairs["rssi"])
            except ValueError:
                insights["rssi"] = kv_pairs["rssi"]
        if "firmware_version" in kv_pairs:
            insights["firmware_version"] = kv_pairs["firmware_version"]
        if "latest" in kv_pairs:
            insights["latest_firmware"] = kv_pairs["latest"]
        if "cloud_auth" in kv_pairs:
            insights["cloud_auth"] = kv_pairs["cloud_auth"]
        if "privacy_mode" in kv_pairs:
            insights["privacy_mode"] = kv_pairs["privacy_mode"].lower() == "true"

    weak_wifi = isinstance(insights.get("rssi"), int) and insights["rssi"] < -75
    outdated_firmware = (
        insights.get("firmware_version") is not None
        and insights.get("latest_firmware") is not None
        and insights["firmware_version"] != insights["latest_firmware"]
    )
    insights["weak_wifi"] = weak_wifi
    insights["outdated_firmware"] = outdated_firmware
    insights["summary"] = _summarize(insights)
    return insights


def _summarize(insights: Dict[str, Any]) -> str:
    parts = []
    if insights.get("error"):
        parts.append(f"发现错误码 {insights['error']}")
    if insights.get("weak_wifi"):
        parts.append(f"RSSI={insights['rssi']}，属于弱 Wi-Fi 信号")
    if insights.get("outdated_firmware"):
        parts.append(
            f"固件版本 {insights['firmware_version']} 低于最新版本 {insights['latest_firmware']}"
        )
    if insights.get("cloud_auth") == "normal":
        parts.append("云鉴权状态正常")
    if insights.get("privacy_mode") is False:
        parts.append("隐私模式未开启")
    return "；".join(parts) + "。" if parts else "日志未发现明确异常。"

