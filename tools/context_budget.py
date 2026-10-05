#!/usr/bin/env python3
"""毎回読み込まれるファイルのサイズを点検する（標準ライブラリのみ）。

使い方: python3 tools/context_budget.py
超過があれば終了コード1。上限はこのリポジトリの運用ルール（docs/context-design.md）。
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# (パス, 最大行数)。CLAUDE.md は公式推奨の200行以内より厳しめに設定
LIMITS = [
    ("CLAUDE.md", 100),
    ("AGENTS.md", 45),
    ("learner/active.md", 30),
    ("learner/growth.md", 150),
    ("learner/weak-points.md", 40),
]
LIMITS += [(str(p.relative_to(ROOT)), 60) for p in sorted((ROOT / ".claude/rules").glob("*.md"))]

ALWAYS_LOADED = {"CLAUDE.md", "AGENTS.md", "learner/active.md"} | {p for p, _ in LIMITS if p.startswith(".claude/rules/")}


def main():
    bad = 0
    total_bytes = 0
    for rel, limit in LIMITS:
        path = ROOT / rel
        if not path.exists():
            print(f"-- {rel}: なし")
            continue
        text = path.read_text(encoding="utf-8")
        lines = len(text.splitlines())
        size = len(text.encode("utf-8"))
        mark = "OK " if lines <= limit else "超過"
        if lines > limit:
            bad += 1
        if rel in ALWAYS_LOADED:
            total_bytes += size
        tag = "常時" if rel in ALWAYS_LOADED else "必要時"
        print(f"{mark} [{tag}] {rel}: {lines}行 / 上限{limit}行 ({size}バイト)")
    print(f"常時読み込みの合計: {total_bytes}バイト")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
