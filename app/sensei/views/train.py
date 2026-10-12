from flask import Blueprint, abort, redirect, render_template, request, session, url_for

from .. import progress, train

bp = Blueprint("train", __name__)


def _battle(topic):
    b = session.get("battle")
    if not b or b.get("topic") != topic or b.get("over"):
        b = train.new_battle(topic)
        session["battle"] = b
    return b


@bp.route("/train")
def index():
    b = session.get("battle")
    return render_template("train.html", topics=train.TOPICS, st=train.status(), battle=b if b and not b.get("over") else None)


@bp.route("/train/<topic>")
def fight(topic):
    if topic not in train.TOPICS:
        abort(404)
    b = _battle(topic)
    qid, item = train.new_question(topic, avoid=b["recent"])
    if not qid:
        return render_template("error.html", message="このテーマの問題がまだありません。"), 404
    return render_template("battle.html", t=train.TOPICS[topic], topic=topic, b=b, qid=qid, item=item,
                           st=train.status(), msgs=[f"{train.TOPICS[topic]['monster']} Lv{b['mlv']} が あらわれた！"]
                           if b["n"] == 0 else [])


@bp.route("/train/a/<int:qid>", methods=["POST"])
def answer(qid):
    row = train.load(qid)
    if not row:
        abort(404)
    if row["answered"] is None:
        raw = request.form.get("a", "")
        chosen = int(raw) if raw.lstrip("-").isdigit() else None
        t = request.form.get("t", "")
        ms = int(t) if t.isdigit() else None
        correct = train.answer(row, chosen, ms)
        b = _battle(row["topic"])
        session["msgs"] = train.apply(b, correct, ms, row["question"]["key"])
        session["battle"] = b
    return redirect(url_for("train.result", qid=qid))


@bp.route("/train/r/<int:qid>")
def result(qid):
    row = train.load(qid)
    if not row or row["answered"] is None:
        abort(404)
    b = session.get("battle") or train.new_battle(row["topic"])
    return render_template("battle.html", t=train.TOPICS[row["topic"]], topic=row["topic"], b=b, qid=qid,
                           item=row["question"], row=row, st=train.status(), msgs=session.pop("msgs", []))


@bp.route("/train/end", methods=["POST"])
def end():
    b = session.pop("battle", None)
    if not b:
        return redirect(url_for("train.index"))
    return render_template("train_end.html", b=b, t=train.TOPICS[b["topic"]], st=train.status())


@bp.route("/quest")
def quest():
    return render_template("quest.html", qo=progress.quest_overview(), conform=progress.conform_trend())
