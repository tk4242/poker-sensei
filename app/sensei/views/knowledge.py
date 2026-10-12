import threading

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for

from .. import knowledge
from ..db import get_setting, set_setting

bp = Blueprint("knowledge", __name__)


@bp.route("/knowledge")
def index():
    stage = request.args.get("stage", type=int)
    return render_template("knowledge.html", ai=knowledge.enabled(), topics=knowledge.TOPICS,
                           pending=knowledge.cards("verified") + knowledge.cards("needs_fix"),
                           approved=knowledge.cards("approved", stage), stage=stage,
                           cost=knowledge.month_cost(), budget=knowledge.budget(),
                           running=get_setting("knowledge_running", "") == "1",
                           runs=knowledge.q("SELECT * FROM kruns ORDER BY id DESC LIMIT 8"))


def _run_in_background(app, topic):
    with app.app_context():
        try:
            knowledge.collect(topic or None)
        finally:
            set_setting("knowledge_running", "")


@bp.route("/knowledge/run", methods=["POST"])
def run():
    if not knowledge.enabled():
        abort(400, "AI が未設定です（.env の ANTHROPIC_API_KEY）。")
    if get_setting("knowledge_running", "") == "1":
        flash("いま収集中です。数分後に再読み込みしてください。", "ok")
        return redirect(url_for("knowledge.index"))
    topic = request.form.get("topic", "")
    if topic and topic not in {t["key"] for t in knowledge.TOPICS}:
        abort(400)
    set_setting("knowledge_running", "1")
    threading.Thread(target=_run_in_background, args=(current_app._get_current_object(), topic), daemon=True).start()
    flash("収集を始めました。調べて検証するまで数分かかります。終わったら承認待ちに並びます。", "ok")
    return redirect(url_for("knowledge.index"))


@bp.route("/knowledge/<int:cid>/<action>", methods=["POST"])
def act(cid, action):
    if not knowledge.get(cid):
        abort(404)
    if action == "approve":
        knowledge.set_status(cid, "approved")
        flash("承認しました。教材とトレーニング（最新の知識）に入ります。", "ok")
    elif action == "reject":
        knowledge.set_status(cid, "rejected")
        flash("却下しました。", "ok")
    elif action == "verify":
        if not knowledge.enabled():
            abort(400, "AI が未設定です。")
        status = knowledge.verify(cid)
        flash(f"再検証しました（結果: {status}）。", "ok")
    else:
        abort(404)
    return redirect(url_for("knowledge.index"))


@bp.route("/knowledge/budget", methods=["POST"])
def budget():
    try:
        v = max(0.0, min(200.0, float(request.form.get("budget", "5"))))
    except ValueError:
        v = 5.0
    set_setting("knowledge_budget_usd", v)
    flash(f"月の上限を ${v:.2f} にしました。", "ok")
    return redirect(url_for("knowledge.index"))
