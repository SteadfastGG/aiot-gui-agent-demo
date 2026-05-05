from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


@dataclass(frozen=True)
class RetrievedDocument:
    path: str
    score: int
    title: str
    snippet: str


def retrieve_knowledge(query: str, kb_paths: Iterable[Path], limit: int = 4) -> List[RetrievedDocument]:
    tokens = _tokenize(query)
    documents: List[RetrievedDocument] = []

    for kb_path in kb_paths:
        if not kb_path.exists():
            continue
        for file_path in kb_path.rglob("*.md"):
            content = file_path.read_text(encoding="utf-8")
            haystack = content.lower()
            score = sum(3 for token in tokens if token and token in haystack)
            score += _domain_bonus(content, query)
            if score <= 0:
                continue
            documents.append(
                RetrievedDocument(
                    path=str(file_path),
                    score=score,
                    title=_extract_title(content, file_path),
                    snippet=_make_snippet(content, tokens),
                )
            )

    return sorted(documents, key=lambda item: item.score, reverse=True)[:limit]


def format_retrieved_documents(documents: List[RetrievedDocument]) -> str:
    if not documents:
        return "未检索到相关知识。"
    blocks = []
    for index, doc in enumerate(documents, start=1):
        blocks.append(
            f"## 命中文档 {index}: {doc.title}\n\n"
            f"- 路径：`{doc.path}`\n"
            f"- 分数：{doc.score}\n\n"
            f"{doc.snippet}"
        )
    return "\n\n".join(blocks)


def _tokenize(query: str) -> List[str]:
    base_tokens = re.findall(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]{2,}", query.lower())
    domain_tokens = [
        "摄像头",
        "直播",
        "加载",
        "失败",
        "固件",
        "wifi",
        "wi-fi",
        "rssi",
        "STREAM_CONNECT_TIMEOUT".lower(),
        "弱网",
        "云鉴权",
        "隐私",
        "升级",
        "重启",
    ]
    return list(dict.fromkeys(base_tokens + domain_tokens))


def _domain_bonus(content: str, query: str) -> int:
    content_lower = content.lower()
    bonus = 0
    if "stream_connect_timeout" in query.lower() and "stream_connect_timeout" in content_lower:
        bonus += 8
    if "固件" in content and "固件" in query:
        bonus += 3
    if "rssi" in content_lower:
        bonus += 2
    if "隐私" in content and ("安全" in query or "升级" in query):
        bonus += 2
    return bonus


def _extract_title(content: str, file_path: Path) -> str:
    for line in content.splitlines():
        if line.startswith("# "):
            return line.removeprefix("# ").strip()
    return file_path.stem


def _make_snippet(content: str, tokens: List[str], max_chars: int = 420) -> str:
    normalized = content.strip()
    if len(normalized) <= max_chars:
        return normalized
    lower = normalized.lower()
    first_hit = min((lower.find(token) for token in tokens if token and token in lower), default=0)
    start = max(first_hit - 80, 0)
    end = min(start + max_chars, len(normalized))
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(normalized) else ""
    return prefix + normalized[start:end].strip() + suffix

