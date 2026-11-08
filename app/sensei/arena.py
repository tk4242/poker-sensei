"""卓上の練習。ソルバー頻度と、ルール/計算の教材を混同しない。"""
import json
import math
import random
from functools import lru_cache

from .config import CONTENT_DIR
from . import drills
from .db import ex, get_db, iso, now, q

RANKS = 'AKQJT98765432'
POSITIONS = {
    2: ['BTN/SB', 'BB'],
    6: ['UTG', 'HJ', 'CO', 'BTN', 'SB', 'BB'],
    8: ['UTG', 'UTG+1', 'LJ', 'HJ', 'CO', 'BTN', 'SB', 'BB'],
    9: ['UTG', 'UTG+1', 'UTG+2', 'LJ', 'HJ', 'CO', 'BTN', 'SB', 'BB'],
}
FORMATS = {'mtt': 'トーナメント', 'cash': 'リングゲーム'}
MODES = {'positions': '席と動く順番', 'range': 'GTOレンジ暗記', 'flop': 'フロップのコール判断'}
HRC = {'title': 'HoldemResources：HU equilibrium / Raw Data', 'url': 'https://www.holdemresources.net/hune'}
ODDS = {'title': 'GTO Wizard：Pot Odds', 'url': 'https://blog.gtowizard.com/what-are-pot-odds-in-poker/'}


@lru_cache(maxsize=1)
def range_data():
    return json.loads((CONTENT_DIR / 'ranges/hrc-hu.json').read_text())


def hand_names():
    return [a+b if i == j else a+b+'s' if i < j else b+a+'o'
            for i, a in enumerate(RANKS) for j, b in enumerate(RANKS)]


def hand_cards(hand):
    return [hand[0]+'s', hand[1]+('s' if hand.endswith('s') else 'h')]


def category(freq):
    # 純粋戦略を勝手に閾値で丸めない。わずかな混合も混合として教える。
    return 0 if freq == 0 else 1 if freq == 1 else 2


def frequencies(stack, position):
    return range_data()['stacks'][str(stack)]['push' if position == 'BTN/SB' else 'call']


def post_order(players):
    return ['BB', 'BTN/SB'] if players == 2 else ['SB', 'BB'] + POSITIONS[players][:-2]


def seats(players, hero, stack, investments=None, folded=()):
    order = POSITIONS[players]
    order = order[order.index(hero):] + order[:order.index(hero)]
    investments = investments or {}
    out = []
    for i, pos in enumerate(order):
        angle = math.radians(90 + i*360/players)
        out.append(dict(pos=pos, hero=i == 0, x=round(210+157*math.cos(angle), 1),
                        y=round(215+155*math.sin(angle), 1),
                        stack=round(stack-investments.get(pos, 0), 2),
                        bet=investments.get(pos, 0), folded=pos in folded,
                        button=pos in ('BTN', 'BTN/SB')))
    return out


def config_from(form):
    mode, fmt = form.get('mode', 'positions'), form.get('format', 'mtt')
    try:
        players, stack = int(form.get('players', 6)), int(form.get('stack', 8))
    except (TypeError, ValueError):
        raise ValueError('人数とスタックを選んでください。')
    if mode not in MODES or fmt not in FORMATS or players not in POSITIONS or stack not in (5, 8, 10):
        raise ValueError('選択できる条件から選んでください。')
    if mode == 'range' and players != 2:
        raise ValueError('この人数の検証済みレンジは未収録です。HU（2人）を選んでください。')
    pos = form.get('position', 'random')
    if pos != 'random' and pos not in POSITIONS[players]:
        raise ValueError('人数に合うポジションを選んでください。')
    return dict(mode=mode, format=fmt, players=players, stack=stack, position=pos)


def question(cfg, rng):
    n, mode = cfg['players'], cfg['mode']
    hero = rng.choice(POSITIONS[n]) if cfg['position'] == 'random' else cfg['position']
    item = dict(mode=mode, format=cfg['format'], players=n, hero=hero, board=[],
                cards=[], street='プリフロップ', label='ルール練習', sources=[drills.SRC['positions2'], drills.SRC['tda']],
                condition='NLHE・アンティなし', history=[], hint='', frequencies=None)
    if mode == 'range':
        stack = cfg['stack']
        fs = frequencies(stack, hero)
        hand = rng.choice(hand_names())
        freq = fs[hand]
        action = 'オールイン' if hero == 'BTN/SB' else 'コール'
        inv = {'BTN/SB': .5 if hero == 'BTN/SB' else stack, 'BB': 1}
        item.update(cards=hand_cards(hand), hand=hand, pot=sum(inv.values()),
                    seats=seats(n, hero, stack, inv), label='GTO・限定モデル', sources=[HRC],
                    condition=f'HRC公開HUモデル / {stack}bb（ブラインド前）/ 通常のMTT・リング全体の解ではない',
                    history=['SB 0.5bb・BB 1bb'] + ([] if hero == 'BTN/SB' else [f'BTN/SB {stack}bb オールイン']),
                    prompt=f'{hand} はこの解でどう使う？', choices=['フォールドのみ', action+'のみ', '両方を使い分ける'],
                    answer=category(freq), frequencies={'action': action, 'value': freq},
                    hint='このモデルではSBはオールインかフォールド、BBはコールかフォールドだけを選びます。',
                    explain=f'{hand}：{action} {freq*100:.2f}%、フォールド {(1-freq)*100:.2f}%。'
                            '混合戦略は同じハンドで複数の行動を使い分けます。頻度は勝率ではありません。'
                            'リンプや小さいレイズを含む通常のゲーム全体の解ではありません。')
    elif mode == 'positions':
        pre = rng.choice([True, False])
        order = POSITIONS[n] if pre else post_order(n)
        # 最初の席だけでなく、各席の次の手番を繰り返し学ぶ。
        next_pos = order[(order.index(hero)+1) % n]
        is_last = order.index(hero) == n-1
        choices = list(POSITIONS[n]) + ['この巡目の最後']
        answer = 'この巡目の最後' if is_last else next_pos
        task = rng.choice(['next', 'first', 'last'])
        prompt = f'全員が残り、レイズなし。{hero} の次に行動するのは？'
        if task != 'next':
            answer = order[0] if task == 'first' else order[-1]
            prompt = '全員が残り、レイズなし。この巡目で' + ('最初' if task == 'first' else '最後') + 'に行動する席は？'
        item.update(street='プリフロップ' if pre else 'フロップ',
                    board=[] if pre else ['Ks', '7d', '2c'],
                    seats=seats(n, hero, 30), pot=None,
                    prompt=prompt,
                    choices=choices, answer=choices.index(answer),
                    condition='行動順だけの図解・チップ移動は省略',
                    hint='プリフロップとフロップでは、行動の出発点が変わります。',
                    history=['全員が残っている場合の行動順'],
                    explain='行動順：'+' → '.join(order)+'。この問題では再レイズなどによる手番の戻りはありません。'
                            + ('2人卓ではボタンがSBを兼ね、プリフロップは先、フロップ以降は後に行動します。' if n == 2 else '6人卓の最初の席はUTG（LJとも表記）です。' if n == 6 else ''))
    else:
        # 既知の相手の2枚を使い全ランアウトを列挙した教材。レンジ対レンジのGTO解ではない。
        sample = rng.choice(flop_examples())
        hero = 'BTN/SB' if n == 2 else 'BTN'
        bet = rng.choice([3, 6, 9])
        pot = 6 if n == 2 else 6.5
        eq = sample['equity']
        need = drills.pm.pot_odds(pot+bet, bet)
        ev = eq*(pot+2*bet)-bet
        folded = [p for p in POSITIONS[n] if p not in (hero, 'BB')]
        item.update(hero=hero, street='フロップ', label='計算練習・GTO解ではない',
                    cards=sample['hero'], board=sample['board'], villain=sample['villain'],
                    pot=pot+bet, seats=seats(n, hero, 3+bet, {hero: 3, 'BB': 3+bet, **({'SB': .5} if n != 2 else {})}, folded),
                    sources=[ODDS], condition='相手の手札が既知 / 追加ベットなし / レーキ・ICMなし',
                    history=([f'BTNまでフォールド → BTN 合計3bbへレイズ → SBフォールド → BBコール（SBの0.5bbもポットへ）'] if n != 2 else [f'{hero} 合計3bbへレイズ → BB コール']) + [ f'フロップ前ポット {pot}bb → BB {bet}bb オールイン'],
                    prompt=f'あと {bet}bb。コールとフォールド、チップEVが高いのは？',
                    choices=['フォールド', f'コール {bet}bb'], answer=int(ev > 0),
                    hint=f'この手札対決のエクイティ（引き分けは折半）は {eq*100:.2f}%。'
                         'コール額 ÷ コール後のポットと比べましょう。',
                    explain=f'必要エクイティ（引き分けの取り分も含む） {bet} ÷ ({pot}+{bet}+{bet}) = {need*100:.2f}%。'
                            f'エクイティ {eq*100:.2f}%、コールEV {ev:+.2f}bb（フォールドEV 0）。'
                            f'残り2枚の全{sample["runouts"]}通りを計算。相手のレンジが不明な実戦では、この数値をそのまま使えません。')
    item['villain_view'] = [drills.card_view(c) for c in item.get('villain', [])]
    item['cards_view'] = [drills.card_view(c) for c in item['cards']]
    item['board_view'] = [drills.card_view(c) for c in item['board']]
    item['key'] = drills.make_key('arena', item)
    return item


@lru_cache(maxsize=1)
def flop_examples():
    return json.loads((CONTENT_DIR/'ranges/flop-examples.json').read_text())


def create_run(cfg, questions=None):
    rng = random.Random()
    if questions is None:
        questions = []
        seen = set()
        for _ in range(100):
            item = question(cfg, rng)
            if item['key'] not in seen:
                questions.append(item)
                seen.add(item['key'])
            if len(questions) == 5:
                break
    return ex('INSERT INTO arena_runs(created,config,questions,answers) VALUES(?,?,?,?)',
              (iso(now()), json.dumps(cfg), json.dumps(questions, ensure_ascii=False), '[]'))


def load_run(run_id):
    row = q('SELECT * FROM arena_runs WHERE id=?', (run_id,), one=True)
    if not row:
        return None
    return {**dict(row), **{k: json.loads(row[k]) for k in ('config', 'questions', 'answers')}}


def answer(run_id, index, chosen):
    # 二重タップ・別タブ・戻る→再送信でも成績を重複記録しない。
    con = get_db()
    try:
        con.execute('BEGIN IMMEDIATE')
        row = load_run(run_id)
        if not row or not 0 <= index < len(row['questions']):
            raise ValueError('問題が見つかりません。')
        if index > len(row['answers']):
            raise ValueError('順番に回答してください。')
        item = row['questions'][index]
        if not 0 <= chosen < len(item['choices']):
            raise ValueError('回答を選んでください。')
        if index == len(row['answers']):
            correct = chosen == item['answer']
            row['answers'].append(dict(chosen=chosen, correct=correct))
            con.execute('UPDATE arena_runs SET answers=? WHERE id=?', (json.dumps(row['answers']), run_id))
            tag = 'positions' if item['mode'] == 'positions' else 'preflop' if item['mode'] == 'range' else 'math'
            con.execute('INSERT INTO attempts(ts,mode,kind,qkey,tag,stage,correct) VALUES(?,?,?,?,?,?,?)',
                        (iso(now()), 'arena-'+row['config']['format'], 'gen', item['key'], tag, 0 if tag == 'positions' else 2, int(correct)))
        con.commit()
    except Exception:
        con.rollback()
        raise


def stats(fmt):
    return dict(q('SELECT COUNT(*) n, COALESCE(SUM(correct),0) c FROM attempts WHERE mode=?',
                  ('arena-'+fmt,), one=True))


def recent_runs(fmt):
    rows = q('SELECT * FROM arena_runs ORDER BY id DESC LIMIT 30')
    out = []
    for row in rows:
        cfg = json.loads(row['config'])
        if cfg['format'] != fmt:
            continue
        answers = json.loads(row['answers'])
        total = len(json.loads(row['questions']))
        out.append(dict(id=row['id'], title=MODES[cfg['mode']], answered=len(answers), total=total,
                        correct=sum(a['correct'] for a in answers), complete=len(answers)==total))
        if len(out) == 5:
            break
    return out
