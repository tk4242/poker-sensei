import math

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
    from .. import knowledge
    return render_template("stage.html", s=s, current=current, kcards=knowledge.cards("approved", n, limit=10))


@bp.route("/learn/lesson/<lesson_id>")
def lesson(lesson_id):
    s, le = content.lesson(lesson_id)
    if not le:
        abort(404)
    diagrams = []
    if le.get("diagram"):
        for n in (8, 6):
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
                 "show_labels": True, "marks": {}} for n in (8, 6)]
    return render_template("cheatsheet.html", parts=[(t, content.render_md(b)) for t, b in parts],
                           diagrams=diagrams)


@bp.route("/tools", methods=["GET", "POST"])
def tools():
    pm = drills.pm
    res = {}
    f = request.form
    error = None

    def number(name, *, positive=False, maximum=None):
        value = float(f[name])
        if not math.isfinite(value) or value < 0 or (positive and value == 0):
            raise ValueError
        if maximum is not None and value > maximum:
            raise ValueError
        return value

    try:
        kind = f.get("kind")
        if kind == "pot":
            pot, bet = number("pot", positive=True), number("bet", positive=True)
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
            res = {"kind": kind, "spr": pm.spr(number("stack"), number("pot", positive=True))}
        elif kind == "ev":
            res = {"kind": kind, "ev": pm.ev(number("p", maximum=100) / 100, number("win"), number("lose"))}
        elif kind == "equity":
            hands = [pm.parse_cards(h) for h in f["hands"].split()]
            board = pm.parse_cards(f.get("board", "")) if f.get("board", "").strip() else []
            if not 2 <= len(hands) <= 4 or any(len(h) != 2 for h in hands) or len(board) not in (0, 3, 4, 5):
                raise ValueError
            eqs, n = pm.equity(hands, board, trials=8000)
            res = {"kind": kind, "rows": list(zip(f["hands"].split(), eqs)), "n": n}
        elif kind == "avg":
            entrants, start, remain, bb = (number(k, positive=True) for k in ("entrants", "start", "remain", "bb"))
            if not entrants.is_integer() or not remain.is_integer() or remain > entrants:
                raise ValueError
            avg = entrants * start / remain
            res = {"kind": kind, "avg": avg, "avg_bb": avg / bb}
    except (KeyError, ValueError, ZeroDivisionError):
        error = "入力を確認してください（カードは Ah Kd のように、ランク23456789TJQKA＋スートcdhs）。"
    return render_template("tools.html", res=res, error=error, form=f)


@bp.route('/learn/basics')
def basics():
    from .. import foundations
    lessons = foundations.overview()
    next_lesson = next((le for le in lessons if not le['completed']), None)
    return render_template('basics.html', lessons=lessons, next_lesson=next_lesson)


@bp.route('/learn/basics/<topic>')
def basics_lesson(topic):
    from .. import foundations
    if topic not in foundations.LESSONS:
        abort(404)
    try:
        example = foundations.scenario(int(request.args.get('size', 50)), int(request.args.get('equity', 40)))
    except (ValueError, TypeError):
        abort(400, description='練習用のサイズと勝率を選び直してください。')
    return render_template('basics_lesson.html', topic=topic, lesson=foundations.LESSONS[topic],
                           example=example, assumptions=foundations.ASSUMPTIONS, sources=foundations.SOURCES,
                           lessons=list(foundations.LESSONS),
                           prices=[foundations.scenario(s) for s in (25, 50, 75, 100, 150)])


@bp.route('/learn/basics/<topic>/practice', methods=['POST'])
def basics_practice(topic):
    from flask import redirect, url_for
    from .. import foundations, practice
    if topic not in foundations.LESSONS:
        abort(404)
    bid = practice.create_batch('practice', foundations.title(topic), foundations.questions(topic))
    return redirect(url_for('practice.batch', batch_id=bid))


@bp.route('/learn/actions')
def action_course():
    from .. import action_lessons
    lessons = action_lessons.overview()
    return render_template('action_course.html', lessons=lessons,
                           next_lesson=next((le for le in lessons if not le['completed']), None))


@bp.route('/learn/actions/<topic>')
def action_lesson(topic):
    from .. import action_lessons
    data = action_lessons.data()
    if topic not in data['lessons']:
        abort(404)
    topics = list(data['lessons'])
    index = topics.index(topic)
    next_topic = topics[index + 1] if index + 1 < len(topics) else None
    lesson = data['lessons'][topic]
    return render_template('action_lesson.html', lesson=lesson, topic=topic, topics=topics,
                           next_topic=next_topic, next_title=data['lessons'][next_topic]['short'] if next_topic else '',
                           lesson_sources=[data['sources'][key] for key in lesson['source_ids']])


@bp.route('/learn/actions/<topic>/practice', methods=['POST'])
def action_practice(topic):
    from flask import redirect, url_for
    from .. import action_lessons, practice
    if topic not in action_lessons.data()['lessons']:
        abort(404)
    bid = practice.create_batch('practice', action_lessons.title(topic), action_lessons.questions(topic))
    return redirect(url_for('practice.batch', batch_id=bid))


@bp.route('/learn/range-guide')
def range_guide():
    from ..arena import POSITIONS, FORMATS, seats
    try:
        players = int(request.args.get('players', 6))
    except (ValueError, TypeError):
        abort(400)
    fmt = request.args.get('format', 'mtt')
    if players not in POSITIONS or fmt not in FORMATS:
        abort(400)
    hero = request.args.get('position', 'BTN/SB' if players == 2 else 'BTN')
    if hero not in POSITIONS[players]:
        abort(400)
    order = POSITIONS[players]
    index = order.index(hero)
    behind = order[index+1:]
    item = dict(players=players, hero=hero, street='プリフロップ', history=['自分より前は全員フォールド'],
                pot=None, board=[], board_view=[], cards_view=[], seats=seats(players, hero, 0, folded=order[:index]))
    for seat in item['seats']:
        seat['stack'] = None
    return render_template('range_guide.html', item=item, positions=POSITIONS,
                           behind=behind, players=players, hero=hero, fmt=fmt, formats=FORMATS)
