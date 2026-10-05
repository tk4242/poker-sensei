"""出題・採点・間隔反復（SRS）・成績の集計。"""
import json
import random
from datetime import timedelta

from . import content, drills
from .db import days_ago, ex, iso, now, q, today

# 箱ごとの次回までの日数（間違えたら箱0＝すぐ復習。正解で1つ上の箱へ）
INTERVALS = [0, 1, 3, 7, 14, 30]
BATCH_SIZE = 5


def shuffled(item, rng):
    """選択肢をシャッフルし、answer を付け替えたコピーを返す。"""
    item = dict(item)
    order = list(range(len(item["choices"])))
    if not item.get("keep_order"):
        rng.shuffle(order)
    item["choices"] = [item["choices"][i] for i in order]
    item["answer"] = order.index(item["answer"])
    return item


def _bank_pick(sel, n, rng, prefer_weak=True):
    pool = content.bank_select(sel.get("stage"), sel.get("tags"))
    if not pool:
        return []
    # 正答率の低い問題・未出題を優先（同じ問題ばかりにならないよう乱数も混ぜる）
    stats = {r["qkey"]: (r["c"], r["n"]) for r in q(
        "SELECT qkey, SUM(correct) c, COUNT(*) n FROM attempts WHERE kind='bank' GROUP BY qkey")}

    def score(item):
        c, t = stats.get(item["key"], (0, 0))
        acc = c / t if t else -1  # 未出題は最優先
        return (acc if prefer_weak else 0) + rng.random() * 0.6

    pool.sort(key=score)
    return pool[:n]


def build_questions(spec, n, rng=None):
    """spec: {"gen": 名前} / {"bank": {...}} / 両方（半々）/ {"review": True}"""
    rng = rng or random.Random()
    items = []
    if spec.get("review"):
        items = due_items(n)
    elif spec.get("gen") and spec.get("bank"):
        k = n // 2
        items = drills.generate(spec["gen"], n - k, rng) + _bank_pick(spec["bank"], k, rng)
        if len(items) < n:
            items += drills.generate(spec["gen"], n - len(items), rng)
    elif spec.get("gen"):
        items = drills.generate(spec["gen"], n, rng)
    elif spec.get("bank"):
        items = _bank_pick(spec["bank"], n, rng, prefer_weak=not spec.get("exam"))
    rng.shuffle(items)
    return [shuffled(it, rng) for it in items]


def create_batch(mode, title, questions, req_id=None, lesson_id=None):
    return ex("INSERT INTO batches(created,mode,title,req_id,lesson_id,questions) VALUES(?,?,?,?,?,?)",
              (iso(now()), mode, title, req_id, lesson_id, json.dumps(questions, ensure_ascii=False)))


def load_batch(batch_id):
    row = q("SELECT * FROM batches WHERE id=?", (batch_id,), one=True)
    if not row:
        return None
    b = dict(row)
    b["questions"] = json.loads(b["questions"])
    b["result"] = json.loads(b["result"]) if b["result"] else None
    return b


def update_srs(item, correct):
    row = q("SELECT * FROM srs WHERE qkey=?", (item["key"],), one=True)
    t = now()
    if row is None:
        if correct and item["kind"] == "gen":
            return  # 自動生成で一発正解の問題は覚える必要なし（同じ問題は二度と出ないため）
        box, lapses = (1 if correct else 0), (0 if correct else 1)
    else:
        box = min(row["box"] + 1, len(INTERVALS) - 1) if correct else 0
        lapses = row["lapses"] + (0 if correct else 1)
    if item["kind"] == "gen" and correct and box >= 3:
        ex("DELETE FROM srs WHERE qkey=?", (item["key"],))  # 3回続けて正解したら卒業
        return
    due = t + timedelta(days=INTERVALS[box]) if correct else t
    snapshot = json.dumps(item, ensure_ascii=False)
    ex("""INSERT INTO srs(qkey,kind,tag,box,due,last,lapses,snapshot) VALUES(?,?,?,?,?,?,?,?)
          ON CONFLICT(qkey) DO UPDATE SET box=excluded.box, due=excluded.due, last=excluded.last,
          lapses=excluded.lapses, snapshot=excluded.snapshot""",
       (item["key"], item["kind"], item["tag"], box, iso(due), iso(t), lapses, snapshot))


def due_count():
    return q("SELECT COUNT(*) c FROM srs WHERE due<=?", (iso(now()),), one=True)["c"]


def due_items(n):
    rows = q("SELECT snapshot FROM srs WHERE due<=? ORDER BY box, due LIMIT ?", (iso(now()), n))
    out = []
    bank = content.question_bank()
    for r in rows:
        item = json.loads(r["snapshot"])
        if item["kind"] == "bank" and item["id"] in bank:
            item = bank[item["id"]]  # 問題集が直されていたら最新版で出す
        out.append(item)
    return out


def grade(batch, answers, times):
    """answers: [選んだ添字 or -1(わからない) or None]、times: [ミリ秒]。結果 dict を返し DB に記録。"""
    _, req = content.requirement(batch["req_id"]) if batch["req_id"] else (None, None)
    limit_ms = (req or {}).get("time_limit_s", 0) * 1000
    results = []
    score = 0
    for i, item in enumerate(batch["questions"]):
        a = answers[i] if i < len(answers) else None
        ms = times[i] if i < len(times) else None
        dontknow = a is None or a < 0
        correct = (not dontknow) and a == item["answer"]
        slow = bool(limit_ms and correct and (ms is None or ms > limit_ms))
        ok = correct and not slow
        score += ok
        results.append({"chosen": a, "correct": correct, "ok": ok, "slow": slow, "dontknow": dontknow, "ms": ms})
        ex("""INSERT INTO attempts(ts,mode,kind,qkey,tag,stage,correct,dontknow,elapsed_ms,batch_id)
              VALUES(?,?,?,?,?,?,?,?,?,?)""",
           (iso(now()), batch["mode"], item["kind"], item["key"], item["tag"], item.get("stage"),
            int(ok), int(dontknow), ms, batch["id"]))
        update_srs(item, ok)
    total = len(batch["questions"])
    passed = None
    if batch["mode"] == "exam" and req:
        passed = score >= req["pass"]
        ex("INSERT INTO exams(ts,req_id,score,total,passed) VALUES(?,?,?,?,?)",
           (iso(now()), req["id"], score, total, int(passed)))
    if batch["mode"] == "lesson" and batch["lesson_id"] and total and score / total >= 0.8:
        ex("""INSERT INTO lessons_done(lesson_id,ts,score,total) VALUES(?,?,?,?)
              ON CONFLICT(lesson_id) DO UPDATE SET ts=excluded.ts, score=excluded.score, total=excluded.total""",
           (batch["lesson_id"], iso(now()), score, total))
    result = {"items": results, "score": score, "total": total, "passed": passed}
    ex("UPDATE batches SET graded=1, result=? WHERE id=?", (json.dumps(result, ensure_ascii=False), batch["id"]))
    return result


# ---------------------------------------------------------------- 集計

def tag_stats(days=30):
    rows = q("""SELECT tag, SUM(correct) c, COUNT(*) n FROM attempts WHERE ts>=? GROUP BY tag ORDER BY tag""",
             (days_ago(days),))
    out = []
    for r in rows:
        out.append({"tag": r["tag"], "name": content.TAG_JP.get(r["tag"], r["tag"]), "c": r["c"], "n": r["n"],
                    "acc": r["c"] / r["n"] if r["n"] else 0})
    return out


def weak_tags(min_n=5, threshold=0.7):
    return sorted([t for t in tag_stats() if t["n"] >= min_n and t["acc"] < threshold], key=lambda t: t["acc"])


def today_count():
    return q("SELECT COUNT(*) c FROM attempts WHERE ts>=?", (today(),), one=True)["c"]


def daily_counts(days=14):
    rows = q("SELECT substr(ts,1,10) d, COUNT(*) n, SUM(correct) c FROM attempts WHERE ts>=? GROUP BY d ORDER BY d",
             (days_ago(days),))
    return [dict(r) for r in rows]


def streak(quota):
    """ノルマ（quota 問）を達成した日が今日（または昨日）から何日続いているか。"""
    rows = q("SELECT substr(ts,1,10) d, COUNT(*) n FROM attempts GROUP BY d")
    done = {r["d"] for r in rows if r["n"] >= quota}
    day = now().date()
    if day.isoformat() not in done:
        day -= timedelta(days=1)
    n = 0
    while day.isoformat() in done:
        n += 1
        day -= timedelta(days=1)
    return n


def totals():
    r = q("SELECT COUNT(*) n, SUM(correct) c FROM attempts", one=True)
    return {"n": r["n"] or 0, "c": r["c"] or 0}
