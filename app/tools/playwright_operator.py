from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from app.config import settings
from app.tools.device_state import load_device_state, update_device_state


def run_console_diagnosis(console_path: Path, device_id: str, device_state: Dict[str, Any]) -> List[Dict[str, Any]]:
    device = device_state[device_id]
    actions = _base_diagnosis_actions(device_id, device)

    playwright_result = _try_playwright_diagnosis(console_path)
    if playwright_result:
        actions[0]["evidence"] = playwright_result
    else:
        actions[0]["evidence"] = f"使用模拟控制台文件：{console_path}"
    return actions


def run_console_repair(
    console_path: Path,
    device_state_path: Path,
    device_id: str,
    safety_result: Dict[str, Any],
) -> List[Dict[str, Any]]:
    state = load_device_state(device_state_path)
    device = state[device_id]
    actions: List[Dict[str, Any]] = []

    if not safety_result.get("approved"):
        return [
            {
                "action": "gui_repair",
                "target": device_id,
                "result": "blocked",
                "evidence": safety_result.get("comment", "安全审查未通过。"),
                "reason": "高风险操作被阻断",
            }
        ]

    if "upgrade_firmware" in safety_result.get("requires_user_confirmation", []):
        actions.append(
            {
                "action": "simulate_user_confirmation",
                "target": device_id,
                "result": "confirmed",
                "evidence": "Demo 模式记录用户确认固件升级。",
                "reason": "固件升级需要确认后执行",
            }
        )

    playwright_result = _try_playwright_repair(console_path)
    latest_firmware = device.get("latest_firmware")

    actions.extend(
        [
            {
                "action": "upgrade_firmware",
                "target": device_id,
                "result": "firmware_upgraded",
                "evidence": f"{device.get('firmware_version')} -> {latest_firmware}",
                "reason": "旧固件在弱网环境下容易触发直播流建立超时",
            },
            {
                "action": "restart_device",
                "target": device_id,
                "result": "device_restarted",
                "evidence": "升级后完成模拟重启。",
                "reason": "重启使固件版本和网络通道状态生效",
            },
            {
                "action": "verify_stream",
                "target": device_id,
                "result": "stream_restored",
                "evidence": playwright_result or "模拟验证结果：直播状态恢复。",
                "reason": "确认修复闭环是否达成",
            },
        ]
    )

    update_device_state(
        device_state_path,
        device_id,
        {
            "firmware_version": latest_firmware,
            "stream_status": "recovered",
            "last_error": None,
        },
    )
    return actions


def _base_diagnosis_actions(device_id: str, device: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [
        {
            "action": "open_console",
            "target": "mock_device_console",
            "result": "opened",
            "evidence": "",
            "reason": "进入模拟设备控制台读取页面状态",
        },
        {
            "action": "select_device",
            "target": device_id,
            "result": "selected",
            "evidence": device.get("device_name", device_id),
            "reason": "定位用户描述中的故障设备",
        },
        {
            "action": "run_network_check",
            "target": device_id,
            "result": "wifi_signal_weak" if device.get("rssi", 0) < -75 else "wifi_signal_ok",
            "evidence": f"RSSI = {device.get('rssi')}",
            "reason": "直播加载失败需要优先排查网络质量",
        },
        {
            "action": "check_firmware",
            "target": device_id,
            "result": "new_version_available"
            if device.get("firmware_version") != device.get("latest_firmware")
            else "firmware_latest",
            "evidence": f"当前 {device.get('firmware_version')}，最新 {device.get('latest_firmware')}",
            "reason": "确认是否存在弱网直播相关固件修复",
        },
    ]


def _try_playwright_diagnosis(console_path: Path) -> str | None:
    if not settings.enable_playwright:
        return "ENABLE_PLAYWRIGHT=false，使用确定性模拟执行。"
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(console_path.resolve().as_uri())
            page.get_by_test_id("device-living_room_camera").click()
            page.get_by_test_id("network-check").click()
            page.get_by_test_id("firmware-check").click()
            status = page.get_by_test_id("operation-output").inner_text()
            browser.close()
            return f"Playwright 已操作控制台；页面输出：{status}"
    except Exception as exc:
        return f"Playwright 不可用，已使用模拟执行：{exc.__class__.__name__}"


def _try_playwright_repair(console_path: Path) -> str | None:
    if not settings.enable_playwright:
        return "ENABLE_PLAYWRIGHT=false，使用确定性模拟验证。"
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(console_path.resolve().as_uri())
            page.get_by_test_id("device-living_room_camera").click()
            page.get_by_test_id("firmware-check").click()
            page.get_by_test_id("upgrade-firmware").click()
            page.get_by_test_id("restart-device").click()
            page.get_by_test_id("verify-stream").click()
            status = page.get_by_test_id("operation-output").inner_text()
            browser.close()
            return f"Playwright 验证页面输出：{status}"
    except Exception as exc:
        return f"Playwright 不可用，已使用模拟验证：{exc.__class__.__name__}"
