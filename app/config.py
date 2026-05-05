from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _path_from_env(name: str, default: str) -> Path:
    raw_value = os.getenv(name, default)
    path = Path(raw_value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def _bool_from_env(name: str, default: bool) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    model_name: str = os.getenv("MODEL_NAME", "demo-rules")
    max_iterations: int = int(os.getenv("MAX_ITERATIONS", "3"))
    reset_state_before_run: bool = _bool_from_env("RESET_STATE_BEFORE_RUN", True)
    enable_playwright: bool = _bool_from_env("ENABLE_PLAYWRIGHT", False)
    device_state_path: Path = _path_from_env("DEVICE_STATE_PATH", "data/device_state.json")
    knowledge_base_path: Path = _path_from_env("KNOWLEDGE_BASE_PATH", "data/knowledge_base")
    historical_tickets_path: Path = _path_from_env("HISTORICAL_TICKETS_PATH", "data/historical_tickets")
    output_path: Path = _path_from_env("OUTPUT_PATH", "outputs")
    mock_console_path: Path = _path_from_env("MOCK_CONSOLE_PATH", "mock_device_console/index.html")


settings = Settings()
