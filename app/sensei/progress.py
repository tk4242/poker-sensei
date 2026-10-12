"""ステージの合格ライン判定と、次にやることの決定（ルールベースのコーチ）。"""
from . import content
from .db import get_setting, q


def record_value(kind):
    if kind == "reviewed_hands":
        return q("SELECT COUNT(*) c FROM hands WHERE TRIM(COALESCE(self_review,''))<>''", one=True)["c"]
    if kind == "sessions_with_opponents":
        return q("SELECT COUNT(*) c FROM play_sessions WHERE TRIM(COALESCE(opponents,''))<>''", one=True)["c"]
    if kind == "sessions_with_conform":
        return q("SELECT COUNT(*) c FROM play_sessions WHERE conformed IS NOT NULL", one=True)["c"]
    if kind == "domestic_itm":
        return q("SELECT COUNT(*) c FROM play_sessions WHERE itm=1 AND venue IN ('amusement','domestic_live')",
                 one=True)["c"]
    return 0


def setting_value(key):
    v = get_setting(key, "")
    if key == "c_game_signs":
        return len([x for x in (v or "").splitlines() if x.strip()])
    return 1 if (v or "").strip() else 0


def requirement_status(req):
    best = None
    if req["type"].startswith("exam"):
        row = q("SELECT MAX(score) s, MAX(passed) p, COUNT(*) n FROM exams WHERE req_id=?", (req["id"],), one=True)
        passed = bool(row["p"])
        best = row["s"]
        value = best or 0
        tries = row["n"]
    elif req["type"] == "record":
        value = record_value(req["record"])
        passed = value >= req["pass"]
        tries = None
    else:
        value = setting_value(req["setting"])
        passed = value >= req["pass"]
        tries = None
    return {"passed": passed, "value": value, "target": req["pass"], "tries": tries, "best": best}


def lessons_done():
    return {r["lesson_id"]: dict(r) for r in q("SELECT * FROM lessons_done")}


def overview():
    """全ステージの状態。current = 最初に未合格のステージ（Stage 6 は並行なので除外）。"""
    done = lessons_done()
    out = []
    current = None
    for s in content.stages():
        reqs = [dict(r, status=requirement_status(r)) for r in s["requirements"]]
        lessons = [dict(le, done=le["id"] in done) for le in s["lessons"]]
        passed = all(r["status"]["passed"] for r in reqs)
        item = {**s, "reqs": reqs, "lessons_st": lessons, "passed": passed,
                "lessons_done": sum(le["done"] for le in lessons)}
        out.append(item)
        if current is None and not passed and not s.get("always_open"):
            current = s["stage"]
    if current is None:
        current = out[-1]["stage"]
    for item in out:
        item["current"] = item["stage"] == current
        item["unlocked"] = (item["stage"] <= current or item.get("always_open")
                            or item.get("parallel_with") == current)
    return out, current


def quest_overview():
    """苦手克服クエストの各週の状態。最初の未クリアの週（「毎回」の課題を除く）が now。"""
    qd = content.quest()
    done = lessons_done()
    weeks = []
    for w in qd["weeks"]:
        weeks.append(dict(w, status=requirement_status(w["req"]), lesson_done=w["lesson"] in done))
    nxt = next((w for w in weeks if w["week"] and not w["status"]["passed"]), None)
    for w in weeks:
        w["now"] = w is nxt
    return {**qd, "weeks": weeks, "cleared": sum(w["status"]["passed"] for w in weeks), "next": nxt}


def conform_trend(n=8):
    """「周りに合わせて決めたハンドの数」の推移（古い順）。"""
    rows = q("SELECT date, conformed FROM play_sessions WHERE conformed IS NOT NULL ORDER BY date DESC, id DESC LIMIT ?",
             (n,))
    return [dict(r) for r in rows][::-1]


def next_steps(quota, due, today_n, weak):
    """今日のメニュー（上から順にやる）。"""
    stages, current = overview()
    cur = next(s for s in stages if s["stage"] == current)
    steps = []
    if due:
        steps.append({"title": f"復習 {due} 問（間違えた問題がまた出ます）", "url": "/practice/review",
                      "why": "忘れかけた頃に解き直すのが、いちばん少ない回数で定着します。"})
    for w in weak[:2]:
        steps.append({"title": f"苦手「{w['name']}」を集中練習（直近の正答率 {w['acc']:.0%}）",
                      "url": f"/practice/tag/{w['tag']}", "why": "正答率70%未満のテーマ。ここを潰すのが最短ルートです。"})
    nxt = next((le for le in cur["lessons_st"] if not le["done"]), None)
    if nxt:
        steps.append({"title": f"レッスン {nxt['id']}「{nxt['title']}」", "url": f"/learn/lesson/{nxt['id']}",
                      "why": "読んだら理解チェック（8割で合格）まで進めてください。"})
    req = next((r for r in cur["reqs"] if not r["status"]["passed"]), None)
    if req:
        url = f"/practice/exam/{req['id']}" if req["type"].startswith("exam") else "/learn"
        steps.append({"title": f"合格ライン: {req['label']}", "url": url,
                      "why": f"Stage {current} を突破する条件です。"})
    qo = quest_overview()
    if qo["next"]:
        w = qo["next"]
        steps.append({"title": f"苦手克服クエスト 第{w['week']}週「{w['title']}」: {w['req']['label']}",
                      "url": "/quest", "why": "期待値・ベットの大きさ・オッズは、周りに流されないための物差しになります。"})
    if today_n < quota:
        steps.append({"title": f"今日のノルマ あと {quota - today_n} 問", "url": "/practice",
                      "why": "毎日続けることが最優先。短くても途切れさせない。"})
    return steps, cur
