from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Dict


DEFAULT_DEVICE_STATE: Dict[str, Dict[str, Any]] = {
    "living_room_camera": {
        "device_name": "客厅摄像头",
        "online": True,
        "stream_status": "failed",
        "firmware_version": "2.0.3",
        "latest_firmware": "2.1.5",
        "wifi_signal": "weak",
        "rssi": -78,
        "cloud_auth": "normal",
        "last_error": "STREAM_CONNECT_TIMEOUT",
        "privacy_mode": False,
    },
    "home_router": {
        "device_name": "家庭路由器",
        "online": True,
        "security_mode": "normal",
        "signal_quality": "medium",
        "blocked_ports": [],
    },
    "mi_home_app": {
        "device_name": "米家 App",
        "login_status": "normal",
        "permission_status": "normal",
    },
    "cloud_auth_service": {
        "device_name": "云鉴权服务",
        "status": "normal",
        "last_check": "2026-05-05 10:22:13",
    },
}


def reset_device_state(path: Path) -> Dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    state = copy.deepcopy(DEFAULT_DEVICE_STATE)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return state


def load_device_state(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return reset_device_state(path)
    return json.loads(path.read_text(encoding="utf-8"))


def save_device_state(path: Path, state: Dict[str, Any]) -> Dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return state


def update_device_state(path: Path, device_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    state = load_device_state(path)
    if device_id not in state:
        raise KeyError(f"Unknown device_id: {device_id}")
    state[device_id].update(updates)
    return save_device_state(path, state)


def get_device(state: Dict[str, Any], device_id: str) -> Dict[str, Any]:
    if device_id not in state:
        raise KeyError(f"Unknown device_id: {device_id}")
    return state[device_id]
