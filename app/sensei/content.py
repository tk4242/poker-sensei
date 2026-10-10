"""教材・問題集の読み込み。本文は curriculum/ の Markdown をそのまま使う（アプリ側で書き換えない）。"""
import json
import re
from functools import lru_cache

import markdown as md

from .config import CONTENT_DIR, CURRICULUM_DIR, REPO_ROOT

CURRICULUM_FILES = [
    ("00-roadmap.md", "ロードマップ"),
    ("01-terms.md", "用語・ルール"),
    ("02-strategy.md", "戦略（サイズと状況別アクション）"),
    ("03-mental-training.md", "メンタルとトレーニング"),
    ("04-japan-and-overseas.md", "日本と海外（法律・大会・税金）"),
    ("05-numbers-and-confidence.md", "苦手克服（期待値・ベットの大きさ・オッズ・周りに流されない）"),
]

FIRST_TAGS = ["terms", "positions", "rules", "preflop", "math", "postflop", "tournament", "icm",
              "exploit", "live", "mental", "bankroll", "legal", "overseas", "hands"]
TAG_JP = {
    "terms": "用語", "positions": "ポジション", "rules": "ルール", "preflop": "プリフロップ", "math": "数学",
    "postflop": "ポストフロップ", "tournament": "トーナメント", "icm": "ICM", "exploit": "エクスプロイト",
    "live": "ライブ", "mental": "メンタル", "bankroll": "バンクロール", "legal": "法律", "overseas": "海外",
    "hands": "役の強さ", "news": "最新の知識",
}
LABEL_JP = {"GTO": "GTO（ソルバー基準）", "EXP": "エクスプロイト（相手層への調整）", "RULE": "ルール・定義",
            "MENTAL": "メンタル", "THEORY": "一般則（戦略サイトの目安。ソルバー出力ではない）"}


@lru_cache(maxsize=1)
def _stages_file():
    return json.loads((CONTENT_DIR / "stages.json").read_text(encoding="utf-8"))


def stages():
    return _stages_file()["stages"]


def quest():
    """苦手克服クエスト（curriculum/05 の4週間プラン）。"""
    return _stages_file()["quest"]


def stage(n):
    for s in stages():
        if s["stage"] == n:
            return s
    return None


def lesson(lesson_id):
    for s in stages():
        for le in s["lessons"]:
            if le["id"] == lesson_id:
                return s, le
    return None, None


def requirement(req_id):
    """(ステージ, 合格ライン)。クエストの課題はステージに属さないので (None, 課題)。"""
    for s in stages():
        for r in s["requirements"]:
            if r["id"] == req_id:
                return s, r
    for w in quest()["weeks"]:
        if w["req"]["id"] == req_id:
            return None, w["req"]
    return None, None


@lru_cache(maxsize=1)
def question_bank():
    """app/content/questions/*.json をすべて読み込み、id → 問題 の dict を返す。"""
    bank = {}
    for path in sorted((CONTENT_DIR / "questions").glob("*.json")):
        for item in json.loads(path.read_text(encoding="utf-8")):
            item = dict(item)
            item["kind"] = "bank"
            item["key"] = "bank:" + item["id"]
            item["tag"] = item["tags"][0]
            bank[item["id"]] = item
    return bank


def bank_select(stage=None, tags=None):
    out = []
    for item in question_bank().values():
        if stage is not None and item["stage"] != stage:
            continue
        if tags and not set(tags) & set(item["tags"]):
            continue
        out.append(item)
    return out


def validate_bank():
    """問題集の形式チェック。問題があれば文字列のリストを返す（テストと起動時に使う）。"""
    problems = []
    seen = set()
    for path in sorted((CONTENT_DIR / "questions").glob("*.json")):
        for i, item in enumerate(json.loads(path.read_text(encoding="utf-8"))):
            where = f"{path.name}[{i}] {item.get('id')}"
            for field in ("id", "stage", "tags", "q", "choices", "answer", "explain", "why", "label", "source", "ref"):
                if field not in item:
                    problems.append(f"{where}: {field} がない")
            if item.get("id") in seen:
                problems.append(f"{where}: id が重複")
            seen.add(item.get("id"))
            ch = item.get("choices", [])
            if len(ch) != 4 or len(set(ch)) != 4:
                problems.append(f"{where}: 選択肢は重複なしの4つ")
            if not isinstance(item.get("answer"), int) or not 0 <= item["answer"] < len(ch):
                problems.append(f"{where}: answer が範囲外")
            if item.get("tags") and item["tags"][0] not in FIRST_TAGS:
                problems.append(f"{where}: 1つ目のタグ {item['tags'][0]} が未知")
            if item.get("label") not in LABEL_JP:
                problems.append(f"{where}: label が未知")
            src = item.get("source") or []
            if not src or not all(s.get("url", "").startswith("http") for s in src):
                problems.append(f"{where}: source に URL がない")
    return problems


# ---------------------------------------------------------------- Markdown

def _md():
    return md.Markdown(extensions=["tables", "fenced_code", "toc", "sane_lists"],
                       extension_configs={"toc": {"permalink": False}})


def render_md(text):
    # 教材は自分たちのリポジトリのファイルだけ。生の HTML は使っていないが念のため無効化する
    text = text.replace("<", "&lt;")
    # GitHub と同じく、段落の直後の箇条書きも箇条書きとして扱う（Python-Markdown は空行が必要）
    lines, prev = [], ""
    for line in text.splitlines():
        is_item = re.match(r"^\s*([-*]|\d+\.) ", line) is not None
        prev_text = prev.strip() and not re.match(r"^\s*([-*]|\d+\.) |^\s*[|#>]", prev)
        if is_item and prev_text and not line.startswith(" "):
            lines.append("")
        lines.append(line)
        prev = line
    html = _md().convert("\n".join(lines))
    # 外部リンクは新しいタブで
    return re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" target="_blank" rel="noopener noreferrer"', html)


def read_curriculum(name):
    allowed = {f for f, _ in CURRICULUM_FILES}
    if name not in allowed:
        return None
    return (CURRICULUM_DIR / name).read_text(encoding="utf-8")


def extract_section(text, heading_prefix):
    """'### 1.4' のような見出しの先頭一致で節を取り出す（同じか上位の見出しまで）。"""
    lines = text.splitlines()
    level = len(heading_prefix.split(" ")[0])
    start = None
    for i, line in enumerate(lines):
        if start is None:
            if line.startswith(heading_prefix):
                start = i
            continue
        m = re.match(r"^(#+) ", line)
        if m and len(m.group(1)) <= level:
            return "\n".join(lines[start:i]).strip()
    return "\n".join(lines[start:]).strip() if start is not None else ""


def lesson_html(le):
    parts = []
    for fname, head in le["sections"]:
        text = read_curriculum(fname)
        sec = extract_section(text, head) if text else ""
        if sec:
            parts.append(render_md(sec) + f'<p class="from">出典元の教材: <a href="/library/{fname}">{fname}</a></p>')
        else:
            parts.append(f"<p class='warn'>教材の節 {head}（{fname}）が見つかりません。</p>")
    return "\n".join(parts)


# ---------------------------------------------------------------- 用語集

def glossary():
    """01-terms.md の表から用語集を作る。[(分類, 用語, 定義, 例)]"""
    text = read_curriculum("01-terms.md")
    out = []
    category = ""
    for line in text.splitlines():
        if line.startswith("### 2.") or line.startswith("## 3."):
            category = re.sub(r"^#+\s*[\d.]*\s*", "", line).strip()
            continue
        if line.startswith("## 4") or line.startswith("## 出典"):
            category = ""
        if not category or not line.startswith("|") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells[0] in ("用語", "日本語"):
            continue
        if "スラング" in category or "日本" in category:
            term, defin, ex = f"{cells[0]}（{cells[1]}）", cells[2] if len(cells) > 2 else "", ""
        else:
            term, defin = cells[0], cells[1] if len(cells) > 1 else ""
            ex = cells[2] if len(cells) > 2 and not cells[2].startswith("[S") else ""
        out.append({"category": category, "term": term, "def": defin, "ex": ex})
    return out


SOURCE_LINKS = {}


def source_index():
    """01-terms.md の [S#] → URL 対応表（用語集の出典リンク用）。"""
    if SOURCE_LINKS:
        return SOURCE_LINKS
    text = read_curriculum("01-terms.md")
    for m in re.finditer(r"- \[(S\d+)\] (.+?) — (https?://\S+)", text):
        SOURCE_LINKS[m.group(1)] = {"title": m.group(2), "url": m.group(3)}
    return SOURCE_LINKS


def learner_file(name):
    path = REPO_ROOT / "learner" / name
    return path.read_text(encoding="utf-8") if path.exists() else ""
