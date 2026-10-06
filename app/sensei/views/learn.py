from flask import Blueprint, abort, render_template, request

from .. import content, drills, progress

bp = Blueprint("learn", __name__)


@bp.route("/learn")
def stages():
    items, current = progress.overview()
    return render_template("stages.html", stages=items, current=current)


@bp.route("/learn/stage/<int:n>")
def stage(n):
    items, current = progress.overview()
    s = next((x for x in items if x["stage"] == n), None)
    if not s:
        abort(404)
    return render_template("stage.html", s=s, current=current)


@bp.route("/learn/lesson/<lesson_id>")
def lesson(lesson_id):
    s, le = content.lesson(lesson_id)
    if not le:
        abort(404)
    diagrams = []
    if le.get("diagram"):
        for n in (9, 8, 6):
            diagrams.append({"n": n, "button": 0, "labels": [drills.seat_layout(n, 0)[i] for i in range(n)],
                             "show_labels": True, "marks": {}})
    done = progress.lessons_done().get(lesson_id)
    return render_template("lesson.html", s=s, le=le, body=content.lesson_html(le), diagrams=diagrams, done=done)


@bp.route("/library")
def library():
    return render_template("library.html", files=content.CURRICULUM_FILES)


@bp.route("/library/<name>")
def library_file(name):
    text = content.read_curriculum(name)
    if text is None:
        abort(404)
    title = dict(content.CURRICULUM_FILES)[name]
    return render_template("doc.html", title=title, name=name, body=content.render_md(text))


@bp.route("/library/sources")
def sources():
    from ..config import REPO_ROOT
    text = (REPO_ROOT / "sources" / "SOURCES.md").read_text(encoding="utf-8")
    return render_template("doc.html", title="出典台帳", name="sources/SOURCES.md", body=content.render_md(text))


@bp.route("/glossary")
def glossary():
    term = request.args.get("q", "").strip().lower()
    items = content.glossary()
    if term:
        items = [g for g in items if term in (g["term"] + g["def"] + g["ex"]).lower()]
    return render_template("glossary.html", items=items, q=term, srcs=content.source_index())


@bp.route("/cheatsheet")
def cheatsheet():
    terms = content.read_curriculum("01-terms.md")
    strat = content.read_curriculum("02-strategy.md")
    parts = [("役の強さ", content.extract_section(terms, "### 1.2")),
             ("主要公式", content.extract_section(terms, "## 4.")),
             ("初心者が最初に覚える10原則", content.extract_section(strat, "## 5."))]
    diagrams = [{"n": n, "button": 0, "labels": [drills.seat_layout(n, 0)[i] for i in range(n)],
                 "show_labels": True, "marks": {}} for n in (9, 6)]
    return render_template("cheatsheet.html", parts=[(t, content.render_md(b)) for t, b in parts],
                           diagrams=diagrams)


@bp.route("/tools", methods=["GET", "POST"])
def tools():
    pm = drills.pm
    res = {}
    f = request.form
    error = None
    try:
        kind = f.get("kind")
        if kind == "pot":
            pot, bet = float(f["pot"]), float(f["bet"])
            res = {"kind": kind, "pot_odds": pm.pot_odds(pot + bet, bet), "mdf": pm.mdf(pot, bet),
                   "alpha": pm.bluff_breakeven(pot, bet), "pot": pot, "bet": bet}
        elif kind == "outs":
            outs = int(f["outs"])
            if not 0 < outs < 46:
                raise ValueError
            res = {"kind": kind, "outs": outs, "one": pm.outs_probability(outs, 1),
                   "two": pm.outs_probability(outs, 2), "r1": pm.rule_of_2_and_4(outs, 1),
                   "r2": pm.rule_of_2_and_4(outs, 2)}
        elif kind == "spr":
            res = {"kind": kind, "spr": pm.spr(float(f["stack"]), float(f["pot"]))}
        elif kind == "ev":
            res = {"kind": kind, "ev": pm.ev(float(f["p"]) / 100, float(f["win"]), float(f["lose"]))}
        elif kind == "equity":
            hands = [pm.parse_cards(h) for h in f["hands"].split()]
            board = pm.parse_cards(f.get("board", "")) if f.get("board", "").strip() else []
            if not 2 <= len(hands) <= 4 or any(len(h) != 2 for h in hands) or len(board) not in (0, 3, 4, 5):
                raise ValueError
            eqs, n = pm.equity(hands, board, trials=8000)
            res = {"kind": kind, "rows": list(zip(f["hands"].split(), eqs)), "n": n}
        elif kind == "avg":
            entrants, start, remain, bb = (float(f[k]) for k in ("entrants", "start", "remain", "bb"))
            avg = entrants * start / remain
            res = {"kind": kind, "avg": avg, "avg_bb": avg / bb}
    except (KeyError, ValueError, ZeroDivisionError):
        error = "入力を確認してください（カードは Ah Kd のように、ランク23456789TJQKA＋スートcdhs）。"
    return render_template("tools.html", res=res, error=error, form=f)
