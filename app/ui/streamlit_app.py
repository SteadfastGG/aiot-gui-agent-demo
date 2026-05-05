from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.graph.workflow import run_diagnosis_workflow  # noqa: E402
from app.tools.device_state import load_device_state  # noqa: E402
from app.config import settings  # noqa: E402


DEFAULT_ISSUE = "客厅摄像头今天突然无法远程查看画面，米家 App 显示设备在线，但打开直播时一直加载失败。"


st.set_page_config(
    page_title="AIoT GUI Agent Demo",
    page_icon="",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container { padding-top: 1.4rem; }
    .metric-card {
        border: 1px solid #d9dee7;
        border-radius: 6px;
        padding: 12px 14px;
        background: #ffffff;
    }
    .small-muted { color: #667085; font-size: 13px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("AIoT GUI Agent Demo")

left, right = st.columns([0.68, 0.32], gap="large")

with left:
    user_issue = st.text_area("设备故障描述", value=DEFAULT_ISSUE, height=120)
    run_clicked = st.button("Run AIoT Support Agent", type="primary", use_container_width=False)

with right:
    initial_state = load_device_state(settings.device_state_path)
    camera = initial_state["living_room_camera"]
    st.markdown("#### 当前模拟设备")
    st.write(
        {
            "设备": camera["device_name"],
            "在线": camera["online"],
            "直播状态": camera["stream_status"],
            "固件": camera["firmware_version"],
            "RSSI": camera["rssi"],
            "错误码": camera["last_error"],
        }
    )

if "workflow_state" not in st.session_state:
    st.session_state.workflow_state = None

if run_clicked:
    with st.spinner("Agent workflow is running..."):
        st.session_state.workflow_state = run_diagnosis_workflow(user_issue)

state = st.session_state.workflow_state

if state:
    status_cols = st.columns(5)
    status_items = list(state["stage_statuses"].items())
    for index, (stage, status) in enumerate(status_items):
        with status_cols[index % 5]:
            st.markdown(
                f"<div class='metric-card'><b>{stage}</b><br><span class='small-muted'>{status}</span></div>",
                unsafe_allow_html=True,
            )

    st.divider()

    tab_overview, tab_graph, tab_gui, tab_safety, tab_reports, tab_raw = st.tabs(
        ["Overview", "Device Graph", "GUI Actions", "Safety", "Reports", "Raw State"]
    )

    with tab_overview:
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Task", state["task_id"])
        col_b.metric("Fault", state["fault_type"])
        col_c.metric("Status", state["status"])
        st.markdown("#### 分诊结果")
        st.json(state["triage_result"])
        st.markdown("#### 日志摘要")
        st.info(state["log_insights"]["summary"])
        st.markdown("#### 根因判断")
        st.write(state["repair_plan"]["root_cause_text"])

    with tab_graph:
        st.markdown("#### 设备链路")
        st.code("米家 App -> 云鉴权服务 -> 客厅摄像头 -> 家庭路由器 -> 外部网络")
        st.markdown("#### 风险链路")
        st.write(state["device_graph"]["risk_links"])
        st.markdown("#### Mermaid")
        st.code(state["device_graph"]["mermaid"], language="mermaid")

    with tab_gui:
        st.markdown("#### 自动操作记录")
        st.dataframe(state["gui_actions"], use_container_width=True, hide_index=True)

    with tab_safety:
        st.markdown("#### 安全审查结果")
        st.json(state["safety_result"])

    with tab_reports:
        report_a, report_b, report_c = st.tabs(["用户报告", "工程师报告", "诊断链路"])
        with report_a:
            st.markdown(state["user_report"])
        with report_b:
            st.markdown(state["engineer_report"])
        with report_c:
            st.markdown(state["diagnosis_trace"])

    with tab_raw:
        st.json(state)

