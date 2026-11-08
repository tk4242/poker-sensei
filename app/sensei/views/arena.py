from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from .. import arena

bp = Blueprint('arena', __name__, url_prefix='/table')


@bp.route('')
def index():
    fmt = request.args.get('format', 'mtt')
    if fmt not in arena.FORMATS:
        abort(404)
    return render_template('arena.html', fmt=fmt, formats=arena.FORMATS, positions=arena.POSITIONS,
                           stats=arena.stats(fmt), modes=arena.MODES, recent=arena.recent_runs(fmt))


@bp.route('/start', methods=['POST'])
def start():
    try:
        cfg = arena.config_from(request.form)
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('arena.index'))
    rid = arena.create_run(cfg)
    return redirect(url_for('arena.play', run_id=rid))


@bp.route('/run/<int:run_id>')
def play(run_id):
    run = arena.load_run(run_id)
    if not run:
        abort(404)
    try:
        index = int(request.args.get('q', len(run['answers'])))
    except ValueError:
        abort(400)
    if not 0 <= index <= min(len(run['answers']), len(run['questions'])):
        abort(400)
    if index == len(run['questions']):
        return render_template('arena_result.html', run=run, formats=arena.FORMATS,
                               score=sum(a['correct'] for a in run['answers']))
    result = run['answers'][index] if index < len(run['answers']) else None
    return render_template('arena_play.html', run=run, item=run['questions'][index], index=index,
                           result=result, formats=arena.FORMATS)


@bp.route('/run/<int:run_id>/answer', methods=['POST'])
def answer(run_id):
    try:
        index, chosen = int(request.form.get('index', '')), int(request.form.get('choice', ''))
        arena.answer(run_id, index, chosen)
    except ValueError:
        abort(400, '回答を選び直してください。')
    return redirect(url_for('arena.play', run_id=run_id, q=index))


@bp.route('/run/<int:run_id>/retry', methods=['POST'])
def retry(run_id):
    run = arena.load_run(run_id)
    if not run:
        abort(404)
    wrong = [it for it, a in zip(run['questions'], run['answers']) if not a['correct']]
    if run['config']['players'] not in arena.POSITIONS:
        flash('新しい卓は最大8人です。人数を選んで始めてください。', 'error')
        return redirect(url_for('arena.index', format=run['config']['format']))
    rid = arena.create_run(run['config'], wrong or None)
    return redirect(url_for('arena.play', run_id=rid))


@bp.route('/ranges')
def ranges():
    fmt = request.args.get('format', 'mtt')
    position = request.args.get('position', 'BTN/SB')
    try:
        stack = int(request.args.get('stack', 8))
    except ValueError:
        abort(400)
    if fmt not in arena.FORMATS or position not in arena.POSITIONS[2] or stack not in (5, 8, 10):
        abort(400)
    fs = arena.frequencies(stack, position)
    hand = request.args.get('hand', 'AKs')
    if hand not in fs:
        abort(400)
    cells = [dict(hand=h, freq=fs[h], cat=arena.category(fs[h])) for h in arena.hand_names()]
    share = sum(fs[h]*(6 if len(h) == 2 else 4 if h.endswith('s') else 12) for h in fs)/1326
    return render_template('arena_ranges.html', fmt=fmt, formats=arena.FORMATS, stack=stack,
                           position=position, cells=cells, hand=hand, freq=fs[hand], share=share,
                           action='オールイン' if position == 'BTN/SB' else 'コール', source=arena.HRC)
