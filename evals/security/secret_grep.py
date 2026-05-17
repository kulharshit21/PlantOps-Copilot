from __future__ import annotations

import re
from pathlib import Path


PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(r"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}"),
]

SKIP_PARTS = {".git", "node_modules", ".next", ".pytest_cache", "__pycache__"}


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    findings: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file() or any(part in SKIP_PARTS for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in PATTERNS:
            if pattern.search(text):
                findings.append(str(path.relative_to(root)))
                break

    if findings:
        print("FAIL: possible secrets found")
        for finding in findings:
            print(f" - {finding}")
        return 1
    print("PASS: no obvious key-shaped secrets found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
