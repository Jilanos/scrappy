from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_profile(path: str | Path) -> dict[str, Any]:
    profile_path = Path(path)
    raw = profile_path.read_text(encoding="utf-8")
    if profile_path.suffix.lower() == ".json":
        return json.loads(raw)
    return _parse_simple_yaml(raw)


def _parse_simple_yaml(raw: str) -> dict[str, Any]:
    """Parse the small YAML subset used by examples/profile.yaml.

    This intentionally supports only nested mappings and string lists. It keeps
    the MVP dependency-free while leaving room to switch to PyYAML later.
    """

    root: dict[str, Any] = {}
    stack: list[tuple[int, Any]] = [(-1, root)]

    lines = raw.splitlines()
    for line_index, original_line in enumerate(lines):
        line = original_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()

        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]

        if stripped.startswith("- "):
            if not isinstance(parent, list):
                raise ValueError(f"List item without list parent: {original_line}")
            parent.append(_clean_scalar(stripped[2:]))
            continue

        if ":" not in stripped:
            raise ValueError(f"Unsupported YAML line: {original_line}")

        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()

        if value:
            parent[key] = _clean_scalar(value)
            continue

        next_container: list[str] | dict[str, Any]
        next_container = [] if _next_significant_line_is_list(lines, line_index, indent) else {}
        parent[key] = next_container
        stack.append((indent, next_container))

    return _normalize_empty_mappings(root)


def _normalize_empty_mappings(value: Any) -> Any:
    if isinstance(value, dict):
        for key, child in list(value.items()):
            value[key] = _normalize_empty_mappings(child)
        return value
    if isinstance(value, list):
        return [_normalize_empty_mappings(item) for item in value]
    return value


def _clean_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _next_significant_line_is_list(lines: list[str], current_index: int, current_indent: int) -> bool:
    for next_line in lines[current_index + 1 :]:
        stripped_line = next_line.split("#", 1)[0].rstrip()
        if not stripped_line.strip():
            continue
        indent = len(stripped_line) - len(stripped_line.lstrip(" "))
        if indent <= current_indent:
            return False
        return stripped_line.strip().startswith("- ")
    return False


def profile_terms(profile: dict[str, Any], section: str, key: str) -> list[str]:
    section_value = profile.get(section, {})
    if not isinstance(section_value, dict):
        return []
    values = section_value.get(key, [])
    if isinstance(values, list):
        return [str(item) for item in values]
    if values:
        return [str(values)]
    return []
