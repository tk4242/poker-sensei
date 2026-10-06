from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from .. import practice, summary
from ..db import ex, iso, now, q, today

bp = Blueprint("records", __name__)

VENUES = {
    "amusement": "国内アミューズメント（換金なし）",
    "domestic_live": "国内の大会（JOPT 等の合法な大会）",
    "home_free": "ホームゲーム（お金を賭けない）",
    "app": "アプリ（換金なし）",
    "overseas_live": "海外のライブ大会",
}
TILT_TYPES = ["Running Bad（不運の連続）", "Injustice（不公平感・バッドビート）", "Hate-Losing（負けること自体が嫌）",
              "Mistake（自分のミスへの怒り）", "Entitlement（自分の方が上手いのに）", "Revenge（特定相手への報復）",
              "Desperation（取り返そうと焦る）"]
OPP_TYPES = ["ルース・パッシブ（よくコール）", "タイト・パッシブ（固い・受け身）", "ルース・アグレッシブ（よく打つ）",
             "タイト・アグレッシブ（固い・攻撃的）", "コーリングステーション", "ニット（極端に固い）", "不明"]


def num(v, cast=float):
    try:
        return cast(v) if v not in (None, "") else None
    except ValueError:
        return None


@bp.route("/records")
def index():
    sessions = q("SELECT * FROM play_sessions ORDER BY date DESC, id DESC LIMIT 50")
    hands = q("SELECT * FROM hands ORDER BY date DESC, id DESC LIMIT 50")
    study = q("SELECT * FROM study_log ORDER BY date DESC, id DESC LIMIT 20")
    minutes = q("SELECT COALESCE(SUM(minutes),0) m FROM study_log WHERE date>=?", (today()[:8] + "01",), one=True)["m"]
    return render_template("records.html", sessions=sessions, hands=hands, study=study, venues=VENUES,
                           ss=summary.session_stats(), tags=practice.tag_stats(90), days=practice.daily_counts(30),
                           study_month=minutes, totals=practice.totals())


@bp.route("/records/session/new", methods=["GET", "POST"])
@bp.route("/records/session/<int:sid>", methods=["GET", "POST"])
def session_form(sid=None):
    row = q("SELECT * FROM play_sessions WHERE id=?", (sid,), one=True) if sid else None
    if sid and not row:
        abort(404)
    if request.method == "POST":
        f = request.form
        if f.get("venue") not in VENUES:
            abort(400, "場所の種類を選んでください。")
        vals = (f.get("date") or today(), f["venue"], f.get("event", "").strip(), num(f.get("buyin")),
                f.get("currency", "JPY"), num(f.get("entries"), int), num(f.get("finish"), int),
                1 if f.get("itm") else 0, num(f.get("prize")), num(f.get("hours")), num(f.get("condition"), int),
                num(f.get("tilt"), int) or 0, "、".join(f.getlist("tilt_types")),
                "、".join(f.getlist("opp_types")) + ((" / " + f["opponents"].strip()) if f.get("opponents", "").strip() else ""),
                f.get("good", "").strip(), f.get("improve", "").strip(), f.get("notes", "").strip())
        if sid:
            ex("""UPDATE play_sessions SET date=?,venue=?,event=?,buyin=?,currency=?,entries=?,finish=?,itm=?,prize=?,
                  hours=?,condition=?,tilt=?,tilt_types=?,opponents=?,good=?,improve=?,notes=? WHERE id=?""", vals + (sid,))
        else:
            sid = ex("""INSERT INTO play_sessions(date,venue,event,buyin,currency,entries,finish,itm,prize,hours,condition,
                        tilt,tilt_types,opponents,good,improve,notes,created) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                     vals + (iso(now()),))
        tilt = num(f.get("tilt"), int) or 0
        if tilt >= 3:
            flash("ティルトが強めの日でした。メンタル・ハンドヒストリー（5ステップ）を書いておくと次に活きます。", "ok")
            return redirect(url_for("coach.mental", mhh=1))
        flash("記録しました。おつかれさまでした！ 判断の質で振り返れたら今日は勝ちです。", "ok")
        return redirect(url_for("records.index"))
    return render_template("session_form.html", row=row, venues=VENUES, tilt_types=TILT_TYPES, opp_types=OPP_TYPES,
                           today=today())


@bp.route("/records/hand/new", methods=["GET", "POST"])
@bp.route("/records/hand/<int:hid>", methods=["GET", "POST"])
def hand_form(hid=None):
    row = q("SELECT * FROM hands WHERE id=?", (hid,), one=True) if hid else None
    if hid and not row:
        abort(404)
    fields = ["date", "title", "event", "phase", "blinds", "eff_bb", "hero_pos", "hero_cards", "villain", "preflop",
              "flop", "turn", "river", "result", "self_review", "question"]
    if request.method == "POST":
        f = request.form
        vals = [f.get(k, "").strip() for k in fields]
        vals[0] = vals[0] or today()
        vals[1] = vals[1] or "無題のハンド"
        vals[5] = num(vals[5])
        if hid:
            ex(f"UPDATE hands SET {', '.join(k + '=?' for k in fields)} WHERE id=?", vals + [hid])
        else:
            hid = ex(f"INSERT INTO hands({', '.join(fields)}, created) VALUES({', '.join('?' * (len(fields) + 1))})",
                     vals + [iso(now())])
        flash("ハンドを保存しました。", "ok")
        return redirect(url_for("records.hand_view", hid=hid))
    return render_template("hand_form.html", row=row, today=today())


def hand_markdown(h):
    """hands/TEMPLATE.md の形（チャットの /hand-review に貼れる）。"""
    return f"""# ハンドレビュー: {h['title']}（{h['date']}）

## 状況
- 大会/種別: {h['event'] or ''}
- 段階（序盤/バブル付近/ITM後/FT）: {h['phase'] or ''}
- ブラインド/アンテ: {h['blinds'] or ''}
- 有効スタック（BB）: {h['eff_bb'] or ''}
- 自分のポジション / ハンド: {h['hero_pos'] or ''} / {h['hero_cards'] or ''}
- 相手のポジション / 印象: {h['villain'] or ''}

## アクション
- プリフロップ: {h['preflop'] or ''}
- フロップ: {h['flop'] or ''}
- ターン: {h['turn'] or ''}
- リバー: {h['river'] or ''}
- 結果: {h['result'] or ''}

## 自己レビュー
{h['self_review'] or ''}

## 聞きたいこと
{h['question'] or ''}
"""


@bp.route("/records/hand/<int:hid>/view")
def hand_view(hid):
    h = q("SELECT * FROM hands WHERE id=?", (hid,), one=True)
    if not h:
        abort(404)
    from .. import coach
    return render_template("hand_view.html", h=h, md=hand_markdown(h), ai=coach.enabled())


@bp.route("/records/delete/<kind>/<int:rid>", methods=["POST"])
def delete(kind, rid):
    table = {"session": "play_sessions", "hand": "hands", "study": "study_log"}.get(kind)
    if not table:
        abort(404)
    ex(f"DELETE FROM {table} WHERE id=?", (rid,))
    flash("削除しました。", "ok")
    return redirect(url_for("records.index"))


@bp.route("/records/study", methods=["POST"])
def study():
    f = request.form
    minutes = num(f.get("minutes"), int)
    if not minutes or minutes <= 0:
        abort(400, "分数を入れてください。")
    ex("INSERT INTO study_log(date,minutes,topic,note) VALUES(?,?,?,?)",
       (f.get("date") or today(), minutes, f.get("topic", "").strip(), f.get("note", "").strip()))
    flash(f"{minutes}分の勉強を記録しました。積み上げ、えらい！", "ok")
    return redirect(url_for("records.index"))
