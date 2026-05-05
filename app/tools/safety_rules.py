from __future__ import annotations

from typing import Any, Dict, Iterable, List


FORBIDDEN_ACTIONS = {
    "factory_reset": "恢复出厂设置禁止自动执行。",
    "export_video": "导出用户视频涉及隐私数据，禁止自动执行。",
    "disable_privacy_mode": "关闭隐私保护禁止自动执行。",
}

CONFIRMATION_REQUIRED_ACTIONS = {
    "upgrade_firmware": "固件升级需要用户确认；Demo 中使用模拟确认。",
}

AUTO_ALLOWED_ACTIONS = {
    "open_console",
    "select_device",
    "run_network_check",
    "check_firmware",
    "restart_device",
    "verify_stream",
    "simulate_user_confirmation",
}


def review_actions(actions: Iterable[str], simulated_confirmation: bool = True) -> Dict[str, Any]:
    action_list = list(dict.fromkeys(actions))
    blocked_actions: List[Dict[str, str]] = []
    requires_user_confirmation: List[str] = []
    allowed_actions: List[str] = []

    for action in action_list:
        if action in FORBIDDEN_ACTIONS:
            blocked_actions.append({"action": action, "reason": FORBIDDEN_ACTIONS[action]})
            continue
        if action in CONFIRMATION_REQUIRED_ACTIONS:
            requires_user_confirmation.append(action)
            if simulated_confirmation:
                allowed_actions.append(action)
            continue
        if action in AUTO_ALLOWED_ACTIONS:
            allowed_actions.append(action)
            continue
        blocked_actions.append({"action": action, "reason": "未知操作默认阻断。"})

    risk_level = "high" if blocked_actions else "medium" if requires_user_confirmation else "low"
    approved = not blocked_actions and (
        not requires_user_confirmation or simulated_confirmation
    )

    return {
        "approved": approved,
        "risk_level": risk_level,
        "blocked_actions": blocked_actions,
        "requires_user_confirmation": requires_user_confirmation,
        "simulated_user_confirmed": simulated_confirmation if requires_user_confirmation else False,
        "allowed_actions": allowed_actions,
        "comment": _comment(blocked_actions, requires_user_confirmation, simulated_confirmation),
    }


def _comment(
    blocked_actions: List[Dict[str, str]],
    requires_user_confirmation: List[str],
    simulated_confirmation: bool,
) -> str:
    if blocked_actions:
        reasons = "；".join(item["reason"] for item in blocked_actions)
        return f"存在禁止自动执行的操作：{reasons}"
    if requires_user_confirmation and simulated_confirmation:
        return "固件升级需要用户确认，Demo 已记录模拟确认后继续执行。"
    if requires_user_confirmation:
        return "固件升级需要用户确认，未确认前不能继续执行。"
    return "仅包含低风险诊断操作，允许自动执行。"

