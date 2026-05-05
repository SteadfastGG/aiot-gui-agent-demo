# AIoT GUI Agent Demo

基于多 Agent 工作流的 AIoT 智能硬件售后诊断 Demo。当前版本使用可复现的规则 Agent 跑通闭环，保留 Prompt 模板，后续可以把各 Agent 节点替换为真实 LLM 调用。

## 功能

- 解析用户故障描述，识别设备和故障类型。
- 读取模拟设备状态 JSON。
- 解析设备日志，提取错误码、RSSI、固件版本和云鉴权状态。
- 检索 Markdown 知识库和历史工单。
- 生成设备依赖关系和风险链路。
- 使用 Playwright 操作模拟设备控制台；浏览器环境不可用时自动回退到模拟执行。
- 对固件升级、隐私访问等动作进行安全审查。
- 更新模拟设备状态并生成用户报告、工程师报告和 GUI 操作日志。

## 目录

```text
app/
  agents/              Agent 节点
  graph/               工作流状态和编排
  tools/               状态读写、日志解析、知识检索、GUI 操作、安全规则、报告写入
  prompts/             后续接入 LLM 时使用的 Prompt 模板
  ui/streamlit_app.py  Streamlit 演示页
mock_device_console/   Playwright 可操作的模拟设备控制台
data/                  模拟设备状态、日志、知识库、历史工单
outputs/               运行后生成的报告
```

## 快速启动

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

如果需要真实 Playwright 浏览器操作：

```bash
playwright install
```

然后在 `.env` 中设置：

```env
ENABLE_PLAYWRIGHT=true
```

默认 `ENABLE_PLAYWRIGHT=false`，工作流会使用确定性模拟执行，适合课堂演示、比赛答辩和没有浏览器权限的环境。

启动 FastAPI：

```bash
uvicorn app.main:app --reload --port 8000
```

启动 Streamlit：

```bash
streamlit run app/ui/streamlit_app.py
```

打开模拟设备控制台：

```text
mock_device_console/index.html
```

## API

创建任务：

```http
POST /diagnosis/tasks
```

```json
{
  "user_issue": "客厅摄像头今天突然无法远程查看画面，米家 App 显示设备在线，但打开直播时一直加载失败。"
}
```

执行任务：

```http
POST /diagnosis/tasks/{task_id}/run
```

直接运行：

```http
POST /diagnosis/run
```

查询报告：

```http
GET /diagnosis/tasks/{task_id}/reports
```

## 本地工作流验证

```bash
python -c "from app.graph.workflow import run_diagnosis_workflow; s=run_diagnosis_workflow('客厅摄像头无法远程查看画面，App 显示在线但直播一直加载失败。'); print(s['status']); print(s['repair_plan']['root_cause'])"
```

成功后会在 `outputs/` 下生成：

- `user_report.md`
- `engineer_report.md`
- `diagnosis_trace.md`
- `gui_action_log.md`
- `workflow_state.json`

## 当前边界

- 不接入真实米家设备。
- 不访问真实摄像头视频。
- 不执行真实固件升级。
- 不接入真实售后工单系统。
- 当前规则 Agent 是可演示闭环，LLM 接入点保留在 `app/agents/` 和 `app/prompts/`。
