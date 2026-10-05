import json

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from .. import coach, practice, summary
from ..db import ex, get_setting, iso, now, q, set_setting

bp = Blueprint("coach", __name__)

# 03-mental-training.md A-3（Tendler 公式ブログ）のウォームアップ
WARMUP = ["気が散る要素を排除した（通知オフ・スマホを離す）", "意思決定プロセスを復習した",
          "今日の戦略プラン・調整点を確認した", "ティルトが起きたとき用の「修正ロジック」を手元に用意した"]
WARMUP_SRC = "https://jaredtendler.com/building-a-winning-routine/"
SLEEP_SRC = "https://www.frontiersin.org/journals/psychiatry/articles/10.3389/fpsyt.2020.600092/full"
MHH_STEPS = ["問題（ミス）をできるだけ詳しく書く", "なぜ自分がそう考え・感じ・行動するのは「理にかなっている」のか説明する",
             "ステップ2の論理のどこが間違っているか説明する", "その誤った論理への修正（Correction）を考える",
             "その修正がなぜ正しいのか説明する"]
MHH_SRC = "https://jaredtendler.com/find-the-rocks-in-your-mind/"


def advice():
    """記録から出す、ルールベースのアドバイス（根拠つき）。"""
    out = []
    weak = practice.weak_tags()
    for w in weak[:3]:
        out.append({"title": f"「{w['name']}」の正答率が {w['acc']:.0%}（{w['n']}問）",
                    "body": "苦手つぶしドリルで集中的に。間違えた問題は復習に自動で入ります。",
                    "url": f"/practice/tag/{w['tag']}"})
    rows = q("SELECT * FROM play_sessions ORDER BY date DESC LIMIT 5")
    tilt_days = [r for r in rows if (r["tilt"] or 0) >= 3]
    if len(tilt_days) >= 2:
        out.append({"title": f"直近5回のうち {len(tilt_days)} 回でティルト3以上",
                    "body": "Cゲームのサインと修正ロジックを書いて、プレイ前に読み返しましょう（Tendler のウォームアップ）。",
                    "url": "/coach/mental", "src": WARMUP_SRC})
    long_days = [r for r in rows if (r["hours"] or 0) >= 8]
    if long_days:
        out.append({"title": "長時間のセッションがありました",
                    "body": "研究では、起床から16時間以上たって終えたセッションでティルトが高く、成績も悪化していました。終了時刻を決めてから座りましょう。",
                    "url": "/coach/mental", "src": SLEEP_SRC})
    nostreak = practice.streak(summary.quota()) == 0 and practice.totals()["n"] > 0
    if nostreak:
        out.append({"title": "ノルマが途切れています", "body": "今日は5問だけでもOK。ゼロの日を作らないのが一番の近道です。",
                    "url": "/practice"})
    if not out:
        out.append({"title": "いい流れです", "body": "このまま今日のメニューを上から順に進めましょう。", "url": "/"})
    return out


@bp.route("/coach")
def index():
    logs = q("SELECT * FROM coach_log ORDER BY id DESC LIMIT 10")
    logs = [dict(r, cites=json.loads(r["citations"] or "[]")) for r in logs]
    return render_template("coach.html", advice=advice(), ai=coach.enabled(), logs=logs,
                           summary=summary.learner_summary_text())


@bp.route("/coach/ask", methods=["POST"])
def ask():
    if not coach.enabled():
        abort(400, "AIコーチは未設定です（.env に ANTHROPIC_API_KEY を設定）。")
    question = request.form.get("question", "").strip()[:2000]
    if not question:
        return redirect(url_for("coach.index"))
    recent = [dict(r) for r in q("SELECT question, answer FROM coach_log ORDER BY id DESC LIMIT 3")][::-1]
    answer, cites, err = coach.ask(question, summary.learner_summary_text(), recent)
    if err:
        flash(err, "error")
        return redirect(url_for("coach.index"))
    ex("INSERT INTO coach_log(ts,question,answer,citations) VALUES(?,?,?,?)",
       (iso(now()), question, answer, coach.citations_json(cites)))
    return redirect(url_for("coach.index"))


@bp.route("/coach/hand/<int:hid>", methods=["POST"])
def review_hand(hid):
    from .records import hand_markdown
    h = q("SELECT * FROM hands WHERE id=?", (hid,), one=True)
    if not h:
        abort(404)
    if not coach.enabled():
        abort(400, "AIコーチは未設定です。")
    answer, cites, err = coach.ask(hand_markdown(h), summary.learner_summary_text(), mode="hand")
    if err:
        flash(err, "error")
    else:
        text = answer + ("\n\n出典:\n" + "\n".join(f"- {c['title']}: {c['url']}" for c in cites) if cites else "")
        ex("UPDATE hands SET ai_review=? WHERE id=?", (text, hid))
        flash("AIレビューが届きました。GTO とエクスプロイトの区別に注目して読んでください。", "ok")
    return redirect(url_for("records.hand_view", hid=hid))


@bp.route("/coach/mental", methods=["GET", "POST"])
def mental():
    if request.method == "POST":
        kind = request.form.get("kind")
        if kind == "signs":
            set_setting("c_game_signs", request.form.get("c_game_signs", "").strip())
            set_setting("correction", request.form.get("correction", "").strip())
            flash("Cゲームのサインと修正ロジックを保存しました。プレイ前に必ず読み返しましょう。", "ok")
        elif kind == "budget":
            set_setting("budget_plan", request.form.get("budget_plan", "").strip())
            flash("予算とバンクロール計画を保存しました。", "ok")
        elif kind in ("pre", "mhh"):
            data = {k: v for k, v in request.form.items() if k not in ("csrf", "kind")}
            data["checked"] = request.form.getlist("check")
            ex("INSERT INTO checkins(ts,kind,data) VALUES(?,?,?)", (iso(now()), kind, json.dumps(data, ensure_ascii=False)))
            if kind == "pre":
                warn = []
                try:
                    awake_end = float(data.get("awake", 0) or 0) + float(data.get("planned", 0) or 0)
                except ValueError:
                    awake_end = 0
                if awake_end >= 16:
                    warn.append(f"終了時には起床から約{awake_end:.0f}時間。16時間を超えるとティルトが増え成績も悪化した研究があります。短くするか別の日に。")
                if len(data["checked"]) < len(WARMUP):
                    warn.append("ウォームアップが全部そろっていません。座る前に残りを片づけましょう。")
                flash(" ".join(warn) if warn else "準備完了！ Aゲームで行きましょう。", "error" if warn else "ok")
            else:
                flash("メンタル・ハンドヒストリーを保存しました。書けた時点で一歩前進です。", "ok")
        return redirect(url_for("coach.mental"))
    checkins = q("SELECT * FROM checkins ORDER BY id DESC LIMIT 10")
    checkins = [dict(r, data=json.loads(r["data"])) for r in checkins]
    return render_template("mental.html", warmup=WARMUP, warmup_src=WARMUP_SRC, sleep_src=SLEEP_SRC,
                           mhh=MHH_STEPS, mhh_src=MHH_SRC, signs=get_setting("c_game_signs", ""),
                           correction=get_setting("correction", ""), budget=get_setting("budget_plan", ""),
                           checkins=checkins, show_mhh=request.args.get("mhh"))
