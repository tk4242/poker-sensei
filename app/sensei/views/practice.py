from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from .. import content, drills, practice, progress
from ..db import get_setting

bp = Blueprint("practice", __name__)

TAG_GEN = {"hands": "hand_strength", "positions": "positions", "math": "math", "icm": "icm",
           "preflop": "preflop_math", "rules": "min_raise", "overseas": "structure"}


def batch_size():
    return int(get_setting("batch_size", practice.BATCH_SIZE) or practice.BATCH_SIZE)


def start(mode, title, spec, n=None, req_id=None, lesson_id=None):
    qs = practice.build_questions(spec, n or batch_size())
    if not qs:
        flash("この範囲の問題はまだありません。", "error")
        return redirect(url_for("practice.menu"))
    bid = practice.create_batch(mode, title, qs, req_id=req_id, lesson_id=lesson_id)
    return redirect(url_for("practice.batch", batch_id=bid))


@bp.route("/practice")
def menu():
    bank = content.question_bank()
    by_stage = {}
    for item in bank.values():
        by_stage[item["stage"]] = by_stage.get(item["stage"], 0) + 1
    tags = {}
    for item in bank.values():
        tags[item["tag"]] = tags.get(item["tag"], 0) + 1
    stages, current = progress.overview()
    return render_template("practice.html", gens=drills.GENERATORS, by_stage=by_stage, stages=stages,
                           tags=sorted(tags.items()), due=practice.due_count(), current=current,
                           stats={s["tag"]: s for s in practice.tag_stats()})


@bp.route("/practice/review")
def review():
    if not practice.due_count():
        flash("いま復習する問題はありません。新しい問題に進みましょう！", "ok")
        return redirect(url_for("practice.menu"))
    return start("review", "復習", {"review": True})


@bp.route("/practice/gen/<name>")
def gen(name):
    if name not in drills.GENERATORS:
        abort(404)
    return start("practice", drills.GENERATORS[name][1], {"gen": name})


@bp.route("/practice/bank/<int:stage>")
def bank(stage):
    s = content.stage(stage)
    if not s:
        abort(404)
    return start("practice", f"Stage {stage} {s['title']}", {"bank": {"stage": stage}})


@bp.route("/practice/tag/<tag>")
def tag(tag):
    spec = {}
    if content.bank_select(tags=[tag]):
        spec["bank"] = {"tags": [tag]}
    if tag in TAG_GEN:
        spec["gen"] = TAG_GEN[tag]
    if not spec:
        abort(404)
    return start("practice", f"苦手つぶし: {content.TAG_JP.get(tag, tag)}", spec)


@bp.route("/practice/lesson/<lesson_id>")
def lesson(lesson_id):
    _, le = content.lesson(lesson_id)
    if not le:
        abort(404)
    return start("lesson", f"理解チェック: {le['title']}", le["drill"], n=5, lesson_id=lesson_id)


@bp.route("/practice/exam/<req_id>", methods=["GET", "POST"])
def exam(req_id):
    s, req = content.requirement(req_id)
    if not req or not req["type"].startswith("exam"):
        abort(404)
    stages, current = progress.overview()
    st = next(x for x in stages if x["stage"] == s["stage"])
    if not st["unlocked"]:
        flash(f"先に Stage {current} を合格しましょう。順番に積み上げるのが最短です。", "error")
        return redirect(url_for("learn.stage", n=s["stage"]))
    if request.method == "POST":
        spec = {"gen": req["gen"]} if req["type"] == "exam_gen" else {"bank": req["bank"], "exam": True}
        return start("exam", f"昇段試験: {req['label']}", spec, n=req["n"], req_id=req_id)
    status = progress.requirement_status(req)
    return render_template("exam_intro.html", s=s, req=req, status=status)


@bp.route("/practice/b/<int:batch_id>", methods=["GET", "POST"])
def batch(batch_id):
    b = practice.load_batch(batch_id)
    if not b:
        abort(404)
    if request.method == "POST" and not b["graded"]:
        answers, times = [], []
        for i in range(len(b["questions"])):
            raw = request.form.get(f"a{i}", "")
            answers.append(int(raw) if raw.lstrip("-").isdigit() else None)
            t = request.form.get(f"t{i}", "")
            times.append(int(t) if t.isdigit() else None)
        practice.grade(b, answers, times)
        return redirect(url_for("practice.batch", batch_id=batch_id))
    _, req = content.requirement(b["req_id"]) if b["req_id"] else (None, None)
    if b["graded"]:
        return render_template("results.html", b=b, req=req, pairs=list(zip(b["questions"], b["result"]["items"])))
    return render_template("quiz.html", b=b, limit=(req or {}).get("time_limit_s", 0))
