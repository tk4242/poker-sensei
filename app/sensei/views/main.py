from flask import Blueprint, Response, flash, redirect, render_template, request, url_for

from .. import content, practice, progress, summary, train
from ..db import get_setting, set_setting

bp = Blueprint("main", __name__)


def cheer(today_n, quota, streak, recent_acc):
    """事実だけで励ます一言（数字を盛らない）。"""
    if today_n >= quota:
        return f"今日のノルマ {quota} 問クリア！ この積み重ねが海外MTTのインマネにつながります。"
    if streak >= 2:
        return f"{streak}日連続でノルマ達成中。今日もつなげましょう！"
    if recent_acc is not None and recent_acc >= 0.8:
        return f"直近の正答率 {recent_acc:.0%}。いい調子です、このまま合格ラインを取りにいきましょう。"
    if today_n:
        return f"今日はもう {today_n} 問。あと {quota - today_n} 問でノルマ達成です！"
    return "今日の1問目から始めましょう。最初の5問がいちばん大事です。"


@bp.route("/health")
def health():
    return {"ok": True}


@bp.route("/")
def home():
    quota = summary.quota()
    due = practice.due_count()
    today_n = practice.today_count()
    weak = practice.weak_tags()
    steps, cur = progress.next_steps(quota, due, today_n, weak)
    days = practice.daily_counts(14)
    recent = [d for d in days][-3:]
    rn = sum(d["n"] for d in recent)
    recent_acc = (sum(d["c"] for d in recent) / rn) if rn else None
    streak = practice.streak(quota)
    handover = content.extract_section(content.learner_file("active.md"), "## 再発防止")
    return render_template("home.html", quota=quota, due=due, today_n=today_n, steps=steps, cur=cur,
                           streak=streak, days=days, weak=weak, totals=practice.totals(),
                           cheer=cheer(today_n, quota, streak, recent_acc), st=train.status(),
                           qo=progress.quest_overview(),
                           handover=content.render_md(handover) if handover else "")


@bp.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        try:
            quota = max(5, min(200, int(request.form.get("daily_quota", 30))))
        except ValueError:
            quota = 30
        set_setting("daily_quota", quota)
        set_setting("batch_size", max(3, min(20, int(request.form.get("batch_size", 5) or 5))))
        flash("保存しました。", "ok")
        return redirect(url_for("main.settings"))
    return render_template("settings.html", quota=summary.quota(), batch_size=get_setting("batch_size", 5))


@bp.route("/export")
def export_page():
    return render_template("export.html", md=summary.export_markdown())


@bp.route("/export.json")
def export_json():
    return Response(summary.export_json(), mimetype="application/json",
                    headers={"Content-Disposition": "attachment; filename=poker-sensei-data.json"})


@bp.route("/export.md")
def export_md():
    return Response(summary.export_markdown(), mimetype="text/markdown; charset=utf-8",
                    headers={"Content-Disposition": "attachment; filename=poker-sensei-summary.md"})
