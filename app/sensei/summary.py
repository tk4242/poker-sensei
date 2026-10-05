"""学習者の状態の要約（AIコーチへの文脈、チャットのClaudeへの引き継ぎ用 Markdown）。"""
import json

from . import practice, progress
from .db import get_setting, q, today


def quota():
    return int(get_setting("daily_quota", 30) or 30)


def session_stats():
    rows = q("SELECT * FROM play_sessions ORDER BY date DESC")
    n = len(rows)
    itm = sum(1 for r in rows if r["itm"])
    hours = sum(r["hours"] or 0 for r in rows)
    tilt = [r["tilt"] for r in rows if r["tilt"] is not None]
    return {"n": n, "itm": itm, "itm_rate": itm / n if n else 0, "hours": hours,
            "avg_tilt": sum(tilt) / len(tilt) if tilt else None, "recent": [dict(r) for r in rows[:5]]}


def learner_summary_text():
    stages, current = progress.overview()
    cur = next(s for s in stages if s["stage"] == current)
    t = practice.totals()
    lines = [f"- 日付: {today()}",
             f"- 現在地: Stage {current}「{cur['title']}」 レッスン {cur['lessons_done']}/{len(cur['lessons_st'])} 完了",
             "- 合格ライン: " + " / ".join(f"{r['label']}={'合格' if r['status']['passed'] else '未'}" for r in cur["reqs"]),
             f"- 累計 {t['n']} 問・正答率 {t['c'] / t['n']:.0%}" if t["n"] else "- まだ問題を解いていない"]
    stats = practice.tag_stats()
    if stats:
        lines.append("- テーマ別（直近30日）: " + "、".join(f"{s['name']} {s['acc']:.0%}（{s['n']}問）" for s in stats))
    weak = practice.weak_tags()
    if weak:
        lines.append("- 苦手: " + "、".join(w["name"] for w in weak))
    ss = session_stats()
    if ss["n"]:
        lines.append(f"- 実戦: {ss['n']}回、ITM {ss['itm']}回（{ss['itm_rate']:.0%}）、平均ティルト {ss['avg_tilt'] or 0:.1f}/5")
    signs = get_setting("c_game_signs", "")
    if signs:
        lines.append("- Cゲームのサイン: " + " / ".join(x.strip() for x in signs.splitlines() if x.strip()))
    return "\n".join(lines)


def export_markdown():
    """チャットの Claude（/session-log、/hand-review、growth-tracker）に貼るための要約。"""
    out = ["# ポーカー先生アプリからの引き継ぎ（" + today() + "）", "", "## 学習の状態", learner_summary_text(), ""]
    stages, _ = progress.overview()
    out.append("## 合格ライン")
    for s in stages:
        marks = "、".join(f"{'✅' if r['status']['passed'] else '⬜'} {r['label']}" for r in s["reqs"])
        out.append(f"- Stage {s['stage']} {s['title']}: {marks}")
    out += ["", "## 直近のセッション記録"]
    for r in q("SELECT * FROM play_sessions ORDER BY date DESC LIMIT 10"):
        out.append(f"- {r['date']} {r['venue']} {r['event'] or ''} 順位 {r['finish'] or '-'}/{r['entries'] or '-'} "
                   f"ITM {'○' if r['itm'] else '×'} 体調 {r['condition'] or '-'} ティルト {r['tilt'] or 0} "
                   f"相手: {r['opponents'] or '-'} 良かった: {r['good'] or '-'} 改善: {r['improve'] or '-'}")
    out += ["", "## レビュー待ちのハンド"]
    for h in q("SELECT * FROM hands WHERE COALESCE(ai_review,'')='' ORDER BY date DESC LIMIT 5"):
        out.append(f"- {h['date']} {h['title']}（{h['hero_pos']} {h['hero_cards']}、{h['eff_bb'] or '-'}BB）"
                   f" 質問: {h['question'] or '-'}")
    return "\n".join(out) + "\n"


def export_json():
    tables = ["attempts", "srs", "exams", "lessons_done", "play_sessions", "hands", "checkins", "study_log",
              "coach_log", "settings"]
    return json.dumps({t: [dict(r) for r in q(f"SELECT * FROM {t}")] for t in tables}, ensure_ascii=False, indent=1)
