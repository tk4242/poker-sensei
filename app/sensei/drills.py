"""自動生成ドリル。答えはすべて tools/poker_math.py の関数で計算する（手で書いた数字を使わない）。

各関数は共通形式の問題 dict を返す:
  key, kind="gen", gen, stage, tag, q, choices, answer, explain, why, label, source, ref, diagram?, cards?
"""
import hashlib
import json
import random
import sys
from itertools import combinations

from .config import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "tools"))
import poker_math as pm  # noqa: E402

SUIT_SYM = {"s": "♠", "h": "♥", "d": "♦", "c": "♣"}
RANK_JP = {"T": "10"}

SRC = {
    "rules": {"title": "Wikipedia: Texas hold 'em", "url": "https://en.wikipedia.org/wiki/Texas_hold_%27em"},
    "hands": {"title": "Wikipedia: List of poker hands", "url": "https://en.wikipedia.org/wiki/List_of_poker_hands"},
    "positions": {"title": "Poker.org: Poker table positions cheat sheet",
                  "url": "https://www.poker.org/poker-cheat-sheets/poker-table-positions-cheat-sheet-aN4rp4C1NZmu/"},
    "positions2": {"title": "PokerCoaching: Poker Positions", "url": "https://pokercoaching.com/blog/poker-positions/"},
    "glossary": {"title": "Wikipedia: Glossary of poker terms", "url": "https://en.wikipedia.org/wiki/Glossary_of_poker_terms"},
    "tda": {"title": "Poker TDA Rules 2026 (Rule 45)", "url": "https://www.pokertda.com/view-poker-tda-rules/"},
    "potodds": {"title": "Wikipedia: Pot odds", "url": "https://en.wikipedia.org/wiki/Pot_odds"},
    "mdf": {"title": "GTO Wizard: MDF & Alpha", "url": "https://blog.gtowizard.com/mdf-alpha/"},
    "spr": {"title": "GTO Wizard: Stack-to-pot ratio", "url": "https://blog.gtowizard.com/stack-to-pot-ratio/"},
    "outs": {"title": "PokerSkill: Rule of 2 and 4", "url": "https://www.pokerskill.com/poker-glossary/rule-of-2-and-4/"},
    "bf": {"title": "GTO Wizard: What is the Bubble Factor", "url": "https://blog.gtowizard.com/what-is-the-bubble-factor-in-poker-tournaments/"},
    "bbdef": {"title": "Upswing Poker: Poker Tournament Tips", "url": "https://upswingpoker.com/poker-tournament-tips-strategy-mtt/"},
    "3bet": {"title": "Upswing Poker: Bet Sizing Tips", "url": "https://upswingpoker.com/bet-size-strategy-tips-rules/"},
    "3bet2": {"title": "PokerCoaching: Preflop Bet Sizing Guide",
              "url": "https://pokercoaching.com/blog/preflop-strategy-guide-the-ultimate-guide-to-preflop-bet-sizing/"},
}


def card_view(c):
    return {"rank": RANK_JP.get(c[0], c[0]), "suit": SUIT_SYM[c[1]], "red": c[1] in "hd", "code": c}


def cards_text(cards):
    return " ".join(RANK_JP.get(c[0], c[0]) + SUIT_SYM[c[1]] for c in cards)


def make_key(gen, payload):
    h = hashlib.sha1(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:12]
    return f"gen:{gen}:{h}"


def finish(gen, stage, tag, q, choices, correct, explain, why, label, source, ref, rng, **extra):
    """choices の中の correct を正解にして共通形式にまとめる（シャッフルは出題時）。"""
    assert correct in choices and len(set(choices)) == len(choices), (gen, choices, correct)
    item = {
        "kind": "gen", "gen": gen, "stage": stage, "tag": tag, "q": q, "choices": list(choices),
        "answer": choices.index(correct), "explain": explain, "why": why, "label": label,
        "source": source if isinstance(source, list) else [source], "ref": ref,
    }
    item.update(extra)
    item["key"] = make_key(gen, {"q": q, "choices": sorted(choices), "diagram": extra.get("diagram"),
                                 "cards": extra.get("cards")})
    return item


def pct(x, digits=1):
    return f"{x * 100:.{digits}f}%"


def pct_choices(correct, candidates, rng, digits=1, gap=None):
    """正解の％と、紛らわしい誤答候補（よくある計算ミス）から4択を作る。近すぎる候補は捨てる。"""
    gap = gap if gap is not None else (0.02 if digits else 0.05)
    out = [correct]
    for c in candidates:
        if 0 < c < 1 and all(abs(c - o) >= gap for o in out):
            out.append(c)
        if len(out) == 4:
            break
    step = 0.1
    while len(out) < 4:
        for sign in (1, -1):
            c = correct + sign * step
            if 0 < c < 1 and all(abs(c - o) >= gap for o in out) and len(out) < 4:
                out.append(c)
        step += 0.07
    labels = [pct(v, digits) for v in out]
    return labels, labels[0]


# ---------------------------------------------------------------- 役の強さ

def _best5(cards):
    """最良の5枚を、枚数の多いランク → 高いランクの順に並べて返す（読みやすさのため）。"""
    best = max(combinations(cards, 5), key=pm.evaluate5)
    counts = {}
    for c in best:
        counts[c[0]] = counts.get(c[0], 0) + 1
    return sorted(best, key=lambda c: (counts[c[0]], pm.RANKS.index(c[0])), reverse=True)


def _deal(rng, n):
    return rng.sample(pm.DECK, n)


def gen_hand_compare(rng):
    """2人の手札＋ボードで、どちらが勝つか。半分は同じ役どうし（キッカー勝負）にする。"""
    want_same = rng.random() < 0.5
    for _ in range(400):
        cards = _deal(rng, 9)
        a, b, board = cards[:2], cards[2:4], cards[4:]
        va, vb = pm.best_hand(a + board), pm.best_hand(b + board)
        if (va[0] == vb[0]) == want_same and max(va[0], vb[0]) >= 1:
            break
    na, nb = pm.HAND_NAMES[va[0]], pm.HAND_NAMES[vb[0]]
    ba, bb = _best5(a + board), _best5(b + board)
    if va > vb:
        correct = "A の勝ち"
    elif vb > va:
        correct = "B の勝ち"
    else:
        correct = "引き分け（チョップ）"
    if va[0] == vb[0] and va != vb:
        why_line = f"どちらも{na}なので、役を作るカードのランク → キッカー（kicker）の順に比べます。"
    elif va == vb:
        why_line = "最良の5枚の強さがまったく同じなので引き分け。スート（マーク）に強弱はありません。"
    else:
        why_line = f"{na if va > vb else nb} は {nb if va > vb else na} より強い役です。"
    explain = (f"A の最良5枚: {cards_text(ba)}（{na}）。B の最良5枚: {cards_text(bb)}（{nb}）。{why_line}"
               "手札2枚＋ボード5枚の7枚から、いちばん強い5枚で比べます。")
    return finish("hand_compare", 0, "hands", "どちらが勝つ？（ボードは5枚すべて公開済み）",
                  ["A の勝ち", "B の勝ち", "引き分け（チョップ）"], correct, explain,
                  "ショーダウンで勝ち負けを即座に判定できないと、ベットやコールの判断が始められません。",
                  "RULE", SRC["hands"], "curriculum/01-terms.md 1.2", rng,
                  cards={"A": [card_view(c) for c in a], "B": [card_view(c) for c in b],
                         "board": [card_view(c) for c in board]})


def _seven_with_category(rng, cat):
    if cat == 8:  # ストレートフラッシュは乱数ではほぼ出ないので組み立てる
        suit = rng.choice(pm.SUITS)
        top = rng.randint(3, 12)  # インデックス。3 = 5ハイ（ホイール）
        ranks = [pm.RANKS[(top - i) % 13] if top - i >= 0 else "A" for i in range(5)]
        if top == 3:
            ranks = ["5", "4", "3", "2", "A"]
        sf = [r + suit for r in ranks]
        rest = rng.sample([c for c in pm.DECK if c not in sf], 2)
        cards = sf + rest
        if pm.best_hand(cards)[0] == 8:
            rng.shuffle(cards)
            return cards
    if cat == 7:
        r = rng.choice(pm.RANKS)
        quad = [r + s for s in pm.SUITS]
        cards = quad + rng.sample([c for c in pm.DECK if c not in quad], 3)
        rng.shuffle(cards)
        return cards
    for _ in range(5000):
        cards = _deal(rng, 7)
        if pm.best_hand(cards)[0] == cat:
            return cards
    return None


def gen_hand_name(rng):
    cat = rng.choice(range(9))
    cards = _seven_with_category(rng, cat) or _deal(rng, 7)
    cat = pm.best_hand(cards)[0]
    hole, board = cards[:2], cards[2:]
    correct = pm.HAND_NAMES[cat]
    near = [i for i in range(9) if i != cat]
    near.sort(key=lambda i: (abs(i - cat), rng.random()))
    choices = [correct] + [pm.HAND_NAMES[i] for i in near[:3]]
    best = _best5(cards)
    explain = f"最良の5枚は {cards_text(best)} で「{correct}」。"
    if cat == 4 and pm.evaluate5(best)[1] == 5:
        explain += "A-2-3-4-5 はホイール（wheel）と呼ばれる最も弱いストレートです。"
    if cat == 8 and pm.evaluate5(best)[1] == 14:
        explain += "A ハイのストレートフラッシュがロイヤルフラッシュです（独立した役ではありません）。"
    explain += "役の強さ（強い順）: ストレートフラッシュ > フォーカード > フルハウス > フラッシュ > ストレート > スリーカード > ツーペア > ワンペア > ハイカード。"
    return finish("hand_name", 0, "hands", "手札とボードの7枚で、いちばん強い役は？", choices, correct, explain,
                  "自分の役を正確に数えられないと、強い手を弱く打ったり、負けている手で払い続けたりします。",
                  "RULE", SRC["hands"], "curriculum/01-terms.md 1.2", rng,
                  cards={"hole": [card_view(c) for c in hole], "board": [card_view(c) for c in board]})


def gen_hand_rank(rng):
    cats = rng.sample(range(9), 4)
    names = [pm.HAND_NAMES[i] for i in cats]
    strongest = pm.HAND_NAMES[max(cats)]
    explain = ("強い順: ストレートフラッシュ > フォーカード > フルハウス > フラッシュ > ストレート > "
               "スリーカード > ツーペア > ワンペア > ハイカード。")
    return finish("hand_rank", 0, "hands", "次のうち、いちばん強い役は？", names, strongest, explain,
                  "役の序列はすべての判断の土台。迷わず言えるまで反復します。",
                  "RULE", SRC["hands"], "curriculum/01-terms.md 1.2", rng)


def gen_hand_strength(rng):
    return rng.choice([gen_hand_compare, gen_hand_compare, gen_hand_name, gen_hand_rank])(rng)


# ---------------------------------------------------------------- ポジション

PREFLOP_ORDER = {
    9: ["UTG", "UTG+1", "UTG+2", "LJ", "HJ", "CO", "BTN", "SB", "BB"],
    8: ["UTG", "UTG+1", "LJ", "HJ", "CO", "BTN", "SB", "BB"],
    # 6-max の最初の席は「LJ」と「UTG」の表記ゆれがある【要確認】ので、その席は出題しない
    6: ["LJ/UTG", "HJ", "CO", "BTN", "SB", "BB"],
}
AMBIGUOUS = {"LJ/UTG"}
SECTION = {"UTG": "アーリー（EP）", "UTG+1": "アーリー（EP）", "UTG+2": "アーリー（EP）",
           "LJ": "ミドル（MP）", "HJ": "ミドル（MP）", "CO": "レイト（LP）", "BTN": "レイト（LP）",
           "SB": "ブラインド", "BB": "ブラインド"}


def seat_layout(n, button_seat):
    """席番号（画面下から時計回り）→ ポジション名。"""
    order = PREFLOP_ORDER[n]
    clockwise_from_btn = ["BTN", "SB", "BB"] + order[:-3]
    return {(button_seat + i) % n: name for i, name in enumerate(clockwise_from_btn)}


def postflop_order(n):
    order = PREFLOP_ORDER[n]
    return ["SB", "BB"] + order[:-3] + ["BTN"]


def _order_text(n):
    return " → ".join(["BTN", "SB", "BB"] + PREFLOP_ORDER[n][:-3])


def gen_positions(rng):
    n = rng.choice([9, 9, 8, 6])
    button = rng.randrange(n)
    layout = seat_layout(n, button)
    names = [layout[i] for i in range(n)]
    usable = [x for x in names if x not in AMBIGUOUS]
    kind = rng.choice(["name", "name", "which", "first_pre", "last_pre", "first_post", "last_post",
                       "ip", "ip", "neighbor", "section"])
    if n == 6 and kind in ("first_pre", "section"):
        kind = "name"
    order_line = f"{n}人卓の時計回りの並び: {_order_text(n)}（BTN の左隣が SB、その左が BB）。"
    diagram = {"type": "table", "n": n, "button": button, "labels": names, "show_labels": False,
               "marks": {}, "reveal": True}
    why = "ポジションで「誰が後に動けるか」が決まり、参加できるハンドの広さもベットの打ち方も変わります。"
    src = [SRC["positions"], SRC["glossary"]]
    ref = "curriculum/01-terms.md 1.4"

    def others(correct, pool=None, k=3):
        pool = [x for x in (pool or usable) if x != correct]
        return rng.sample(pool, min(k, len(pool)))

    if kind == "name":
        seat = rng.choice([i for i in range(n) if names[i] not in AMBIGUOUS and names[i] != "BTN"])
        correct = names[seat]
        diagram["marks"] = {str(seat): "★"}
        q = f"{n}人卓。D（ディーラーボタン）の位置から数えて、★の席のポジションは？"
        choices = [correct] + others(correct)
        explain = order_line
    elif kind == "which":
        target = rng.choice([x for x in usable if x != "BTN"])
        seats = [i for i in range(n) if names[i] != "BTN"]
        picks = [names.index(target)] + rng.sample([i for i in seats if names[i] != target], 3)
        rng.shuffle(picks)
        letters = "ABCD"
        diagram["marks"] = {str(s): letters[i] for i, s in enumerate(picks)}
        correct = letters[picks.index(names.index(target))]
        q = f"{n}人卓。{target} はどの席？"
        choices = list(letters)
        explain = order_line
    elif kind in ("first_pre", "last_pre"):
        order = PREFLOP_ORDER[n]
        correct = order[0] if kind == "first_pre" else "BB"
        q = f"{n}人卓・全員参加。プリフロップで{'最初' if kind == 'first_pre' else '最後'}に行動するのは？"
        choices = [correct] + others(correct, ["SB", "BB", "BTN", "UTG", "CO"])
        explain = ("プリフロップは BB の左隣（UTG）から時計回りに行動し、ブラインドを払っている SB・BB が最後になります"
                   "（最後は BB）。" + order_line)
        src = [SRC["rules"]] + src
    elif kind in ("first_post", "last_post"):
        correct = "SB" if kind == "first_post" else "BTN"
        q = f"{n}人卓・全員がフロップに進んだ。フロップ以降で{'最初' if kind == 'first_post' else '最後'}に行動するのは？"
        choices = [correct] + others(correct, ["SB", "BB", "BTN", "UTG", "CO"] if n != 6 else ["SB", "BB", "BTN", "CO", "HJ"])
        explain = ("フロップ以降はボタンの左隣（残っている中で最初の人、通常 SB）から時計回り。"
                   "だから BTN が最後に動けて有利です。")
        src = [SRC["rules"]] + src
    elif kind == "ip":
        po = postflop_order(n)
        a, b = rng.sample(usable, 2)
        ip = a if po.index(a) > po.index(b) else b
        q = f"{n}人卓。{a} と {b} の2人でフロップへ。IP（インポジション＝後に動ける側）はどちら？"
        choices = [a, b, "どちらでもない（毎回変わる）", "ボードによって変わる"]
        correct = ip
        explain = (f"フロップ以降の行動順: {' → '.join(x for x in po if x not in AMBIGUOUS)}。"
                   f"後に動ける {ip} が IP、先に動く側が OOP（アウトオブポジション）。合言葉は「後に動けるのが IP」。")
    elif kind == "neighbor":
        options = [("BTN の左隣（時計回りで次の席）", "SB"), ("BTN の右隣", "CO"), ("SB の左隣", "BB")]
        if n != 6:
            options.append(("BB の左隣", PREFLOP_ORDER[n][0]))
        label, correct = rng.choice(options)
        q = f"{n}人卓。{label}の席は？"
        choices = [correct] + others(correct, [x for x in ["SB", "BB", "CO", "HJ", "BTN", "UTG"] if x in usable])
        explain = order_line + "CO（カットオフ）はボタンの右隣＝ボタンの1つ前に動く席です。"
        diagram["show_labels"] = False
    else:  # section（9人卓・8人卓）
        target = rng.choice([x for x in usable])
        correct = SECTION[target]
        q = f"{n}人卓。{target} はどの区分？"
        choices = ["アーリー（EP）", "ミドル（MP）", "レイト（LP）", "ブラインド"]
        explain = ("区分の目安: アーリー＝UTG〜UTG+2、ミドル＝LJ・HJ、レイト＝CO・BTN、ブラインド＝SB・BB（PokerCoaching）。"
                   "HJ をレイトに数える資料もあります（Poker.org）が、ここでは教材の区分に合わせています。")
        diagram = None
        src = [SRC["positions2"]]
    return finish("positions", 0, "positions", q, choices, correct, explain, why, "RULE", src, ref, rng,
                  diagram=diagram)


# ---------------------------------------------------------------- 数学

def _pot_and_bet(rng):
    pot = rng.choice(range(40, 401, 10))
    frac = rng.choice([0.25, 1 / 3, 0.5, 2 / 3, 0.75, 1.0, 1.5])
    bet = max(5, int(round(pot * frac / 5.0)) * 5)
    return pot, bet


def gen_pot_odds(rng):
    pot, bet = _pot_and_bet(rng)
    need = pm.pot_odds(pot + bet, bet)
    labels, correct = pct_choices(need, [bet / (pot + bet), bet / pot, pot / (pot + bet)], rng)
    explain = (f"必要勝率 = コール額 ÷（相手のベット込みのポット＋コール額）= {bet} ÷ ({pot}+{bet}+{bet}) = {pct(need)}。"
               "よくある間違いは自分のコール額を分母に足し忘れること。")
    return finish("pot_odds", 2, "math", f"ポット {pot} に相手が {bet} をベット。コールに必要な勝率（ポットオッズ）は？",
                  labels, correct, explain,
                  "「自分の勝率がこれを超えればコールは得」という判断の物差しです（インプライドオッズ等を除く）。",
                  "RULE", SRC["potodds"], "curriculum/01-terms.md 4.1", rng)


def gen_mdf(rng):
    pot, bet = _pot_and_bet(rng)
    v = pm.mdf(pot, bet)
    labels, correct = pct_choices(v, [bet / (pot + bet), pm.pot_odds(pot + bet, bet), 1 - pm.pot_odds(pot + bet, bet)], rng)
    explain = (f"MDF = ポット ÷（ポット＋ベット）= {pot} ÷ ({pot}+{bet}) = {pct(v)}。"
               "相手のブラフを損益ゼロにするために続ける（コール/レイズ）最低頻度。"
               "ただし相手のブラフが少ないなら守りすぎる必要はなく、OOP では GTO でも MDF より降りることが多い。")
    return finish("mdf", 2, "math", f"ポット {pot} に相手が {bet} をベット。MDF（最小防御頻度）は？", labels, correct,
                  explain, "ベットにどれくらいの割合で降りてよいかの目安になり、降りすぎ（搾取される側）を防ぎます。",
                  "RULE", SRC["mdf"], "curriculum/01-terms.md 4.2", rng)


def gen_alpha(rng):
    pot, bet = _pot_and_bet(rng)
    v = pm.bluff_breakeven(pot, bet)
    labels, correct = pct_choices(v, [pm.mdf(pot, bet), pm.pot_odds(pot + bet, bet), bet / pot], rng)
    explain = (f"必要フォールド率（α）= ベット ÷（ポット＋ベット）= {bet} ÷ ({pot}+{bet}) = {pct(v)}。"
               "相手がこれより多く降りるなら、そのブラフは（それだけで）利益になります。α = 1 − MDF。")
    return finish("alpha", 2, "math", f"ポット {pot} に {bet} のブラフ。損益分岐になる相手のフォールド率は？",
                  labels, correct, explain, "ブラフが得か損かを、相手がどれだけ降りるかで判断できるようになります。",
                  "RULE", SRC["mdf"], "curriculum/01-terms.md 4.3", rng)


DRAWS = [("フラッシュドロー（同じスート4枚）", 9), ("オープンエンド・ストレートドロー（OESD）", 8),
         ("ガットショット（中抜けストレートドロー）", 4)]


def gen_outs(rng):
    if rng.random() < 0.35:
        name, outs = rng.choice(DRAWS)
        correct = f"{outs}枚"
        choices = [correct] + [f"{x}枚" for x in rng.sample([x for x in (4, 6, 8, 9, 12, 15) if x != outs], 3)]
        return finish("outs", 2, "math", f"{name}のアウツ（来れば完成するカード）は何枚？", choices, correct,
                      "フラッシュドローは同スート13枚−見えている4枚＝9枚。OESD は両端の4枚×2＝8枚、ガットショットは4枚。",
                      "アウツを数えられると、2と4のルールで完成確率を素早く見積もれます。", "RULE",
                      SRC["glossary"], "curriculum/01-terms.md 2.3", rng)
    outs = rng.choice([4, 6, 8, 9, 12, 15])
    streets = rng.choice([1, 2])
    exact = pm.outs_probability(outs, streets)
    approx = pm.rule_of_2_and_4(outs, streets)
    labels, correct = pct_choices(exact, [exact + 0.12, exact - 0.1, exact * 2 if streets == 1 else exact / 2], rng,
                                  digits=0, gap=0.06)
    when = "ターンで、リバーの1枚で" if streets == 1 else "フロップで、ターンとリバーの2枚（オールインでリバーまで見られる）で"
    explain = (f"正確な確率は {pct(exact)}（未知のカード {46 if streets == 1 else 47} 枚から計算）。"
               f"2と4のルールでは {outs}×{2 if streets == 1 else 4} ≒ {approx:.0%}。"
               "×4 はアウツが多いと過大評価になります（15アウツで約6ポイント）。"
               "相手がベットしてくる場面では、通常は次の1枚分のオッズしか保証されません。")
    return finish("outs", 2, "math", f"アウツ {outs} 枚。{when}完成する確率はおよそ？", labels, correct, explain,
                  "ドローで追いかける価値があるかを、ポットオッズと比べて判断するのに使います。",
                  "RULE", SRC["outs"], "curriculum/01-terms.md 4.5", rng)


def gen_spr(rng):
    pot = rng.choice(range(100, 1001, 50))
    stack = pot * rng.choice([0.5, 1, 1.5, 2, 3, 4, 5, 8, 10])
    stack = int(round(stack / 50.0)) * 50 or 50
    v = pm.spr(stack, pot)
    fmt = lambda x: f"{x:.1f}"  # noqa: E731
    cands = [pot / stack, v * 2, v / 2, v + 1, v + 2]
    out = [fmt(v)]
    for c in cands:
        if fmt(c) not in out and abs(c - v) > 0.25:
            out.append(fmt(c))
        if len(out) == 4:
            break
    explain = (f"SPR = エフェクティブスタック ÷ ポット = {stack} ÷ {pot} = {fmt(v)}。"
               "SPR が低いほどトップペアでもスタックオフしやすく、SPR 4 を超えるとワンペアでのスタックオフは危うくなります。")
    return finish("spr", 2, "math", f"フロップのポット {pot}、エフェクティブスタック {stack}。SPR は？",
                  out, fmt(v), explain, "フロップの時点で「この手でどこまで行くか」を決める物差しになります。",
                  "GTO", SRC["spr"], "curriculum/02-strategy.md 2-6", rng)


def gen_bb_count(rng):
    bb = rng.choice([200, 400, 600, 1000, 1500, 2000, 3000, 5000])
    mult = rng.choice([5, 8, 10, 12, 15, 18, 20, 25, 30, 40, 50])
    stack = bb * mult
    correct = f"{mult}BB"
    pool = sorted({m for m in (mult // 2, mult * 2, mult + 5, mult - 3, mult * 3, mult + 10) if m > 0 and m != mult})
    choices = [correct] + [f"{x}BB" for x in rng.sample(pool, 3)]
    return finish("bb_count", 2, "tournament", f"スタック {stack:,} 点、ブラインドは {bb // 2:,}/{bb:,}。何BB？",
                  choices, correct, f"{stack:,} ÷ {bb:,} = {mult}BB。MTT ではスタックを BB 単位で考えます。",
                  "戦略の目安（オープンサイズ、ショーブの判断など）はすべて BB 数で決まるので、瞬時に換算できるようにします。",
                  "RULE", SRC["glossary"], "curriculum/01-terms.md 2.6", rng)


def gen_min_raise(rng):
    bb = rng.choice([100, 200, 400, 1000])
    open_to = bb * rng.choice([2, 2.5, 3, 4])
    open_to = int(open_to)
    raise_by = open_to - bb
    correct_v = open_to + raise_by
    vals = [correct_v, open_to * 2, open_to + bb, open_to * 3]
    vals = list(dict.fromkeys(vals))
    while len(vals) < 4:
        vals.append(vals[-1] + bb)
    choices = [f"{v:,}" for v in vals]
    explain = (f"最小レイズは「そのラウンドで最大のフルのベット/レイズの上乗せ額」以上を上乗せ（TDA Rule 45）。"
               f"上乗せは {open_to:,}−{bb:,}={raise_by:,} なので、最低 {open_to:,}+{raise_by:,}={correct_v:,}。")
    return finish("min_raise", 0, "rules", f"BB={bb:,}。UTG が {open_to:,} にレイズ。次にレイズするときの最小額（合計）は？",
                  choices, f"{correct_v:,}", explain, "ライブ大会で額を間違えると訂正されます。ルールどおりに迷わず出せるように。",
                  "RULE", SRC["tda"], "curriculum/01-terms.md 1.1", rng)


def gen_ev(rng):
    p = rng.choice([0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.6])
    win = rng.choice([100, 150, 200, 300, 400, 500])
    lose = rng.choice([50, 100, 150, 200])
    v = pm.ev(p, win, lose)
    vals = [v, p * win, p * win + (1 - p) * lose, -v if v != 0 else 10.0]
    out = []
    for x in vals:
        s = f"{x:+.0f}"
        if s not in out:
            out.append(s)
    while len(out) < 4:
        out.append(f"{v + 25 * len(out):+.0f}")
    explain = f"EV = 勝率×獲得額 − 負ける確率×損失額 = {p}×{win} − {1 - p:.2f}×{lose} = {v:+.0f}。"
    return finish("ev", 2, "math", f"勝率 {p:.0%} で、勝てば +{win}、負ければ −{lose}。この行動の EV（期待値）は？",
                  out, f"{v:+.0f}", explain, "1回の結果ではなく「繰り返したときの平均」で判断する習慣の土台です。",
                  "RULE", SRC["glossary"], "curriculum/01-terms.md 2.4", rng)


def gen_math(rng):
    return rng.choice([gen_pot_odds, gen_pot_odds, gen_mdf, gen_alpha, gen_outs, gen_spr, gen_ev])(rng)


# ---------------------------------------------------------------- プリフロップ（Stage 1）

def gen_bb_defense(rng):
    open_to = rng.choice([2.0, 2.1, 2.2, 2.25, 2.3, 2.5, 3.0])
    pot = open_to + 0.5 + 1 + 1  # オープン＋SB＋BB＋BBA（=1BB）
    call = open_to - 1
    need = pm.pot_odds(pot, call)
    no_ante = pm.pot_odds(open_to + 1.5, call)
    labels, correct = pct_choices(need, [no_ante, call / pot, open_to / (pot + call)], rng, gap=0.015)
    explain = (f"BBA（1BB）の構造で、ほかの全員が降りた場合: ポット = オープン{open_to} + SB0.5 + BB1 + アンティ1 = {pot:g}BB、"
               f"コール額 = {open_to:g}−1 = {call:g}BB。必要勝率 = {call:g} ÷ ({pot:g}+{call:g}) = {pct(need)}。"
               "BB は安く参加できるので広く守れます（ただし大きいオープンには締める）。")
    return finish("bb_defense", 1, "preflop", f"BBA（BBアンティ=1BB）の大会。BTN が {open_to:g}BB にオープン、SB はフォールド。"
                  "BB のあなたがコールするのに必要な勝率は？", labels, correct, explain,
                  "BB のディフェンス範囲を決める出発点。アンティがあると必要勝率が下がることを数字で体感します。",
                  "RULE", SRC["bbdef"], "curriculum/02-strategy.md 1-7", rng)


def gen_3bet_size(rng):
    open_to = rng.choice([2.0, 2.2, 2.5, 3.0])
    ip = rng.random() < 0.5
    mult = 3 if ip else 4
    correct = f"約{open_to * mult:g}BB"
    vals = [open_to * m for m in (2, 3, 4, 5)]
    choices = [f"約{v:g}BB" for v in vals]
    explain = (f"一般則は 3ベットを IP でオープンの約3倍、OOP で約4倍。{'IP' if ip else 'OOP'} なので "
               f"{open_to:g}×{mult} = {open_to * mult:g}BB。ソルバー例も 50bb で IP 約3.2倍・OOP 約4.3倍（30bb では OOP 約3.9倍）で概ね一致。"
               )
    return finish("3bet_size", 1, "preflop",
                  f"相手が {open_to:g}BB にオープン。あなたは {'IP（相手より後に動ける）' if ip else 'OOP（ブラインドなど、先に動く）'}"
                  "。一般則に沿った 3ベットのサイズは？", choices, correct, explain,
                  "サイズを毎回迷わず決められると、判断の時間をハンドの読みに使えます。",
                  "GTO", [SRC["3bet"], SRC["3bet2"]], "curriculum/02-strategy.md 1-3", rng)


def gen_preflop_math(rng):
    return rng.choice([gen_bb_defense, gen_3bet_size])(rng)


# ---------------------------------------------------------------- トーナメント（Stage 4・7）

def gen_icm(rng):
    bf = rng.choice([1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.8, 2.0])
    v = bf / (bf + 1)
    labels, correct = pct_choices(v, [0.5, 1 / bf, bf / (bf + 2)], rng, digits=0, gap=0.03)
    explain = (f"必要勝率 = BF ÷（BF＋1）= {bf} ÷ {bf + 1:.1f} = {pct(v)}（等スタックのオールイン、デッドマネーなしの単純化）。"
               "チップEV なら 50% でよい場面でも、ICM の下ではこれだけ必要になります。")
    return finish("icm", 4, "icm", f"バブルファクター（BF）が {bf} の状況で、等しいスタックの相手のオールインにコールする。必要な勝率は？",
                  labels, correct, explain, "バブル付近で「チップの計算では得でも賞金では損」なコールを避けるために使います。",
                  "GTO", SRC["bf"], "curriculum/01-terms.md 4.6", rng)


def gen_structure(rng):
    entrants = rng.choice([120, 180, 250, 400, 600, 1000])
    start = rng.choice([20000, 25000, 30000, 40000, 50000])
    remaining = rng.choice([x for x in (20, 30, 40, 60, 80, 100, 150) if x < entrants])
    bb = rng.choice([1000, 2000, 3000, 4000, 5000, 6000])
    avg_bb = entrants * start / remaining / bb
    fmt = lambda x: f"約{x:.0f}BB"  # noqa: E731
    out = [fmt(avg_bb)]
    for c in (avg_bb * 2, avg_bb / 2, start / bb, entrants * start / bb / 100):
        if fmt(c) not in out and abs(c - avg_bb) > 3:
            out.append(fmt(c))
        if len(out) == 4:
            break
    while len(out) < 4:
        out.append(fmt(avg_bb + 10 * len(out)))
    explain = (f"総チップ = {entrants}人×{start:,} = {entrants * start:,}。平均スタック = 総チップ ÷ 残り{remaining}人 = "
               f"{entrants * start / remaining:,.0f}。BB {bb:,} で割ると {avg_bb:.1f}BB（リエントリー・アドオンなしの前提）。")
    return finish("structure", 7, "overseas", f"参加 {entrants} 人・開始スタック {start:,}・残り {remaining} 人・BB {bb:,}。平均スタックは？",
                  out, fmt(avg_bb), explain, "ストラクチャー表を読み、自分が平均より浅いか深いかで戦い方を変えるために使います。",
                  "RULE", SRC["glossary"], "curriculum/00-roadmap.md Stage 7", rng)


# ---------------------------------------------------------------- エクイティ感覚

def _rand_hand(rng, used):
    return rng.sample([c for c in pm.DECK if c not in used], 2)


def gen_equity(rng, trials=1500):
    flop = rng.random() < 0.5
    cards = _deal(rng, 7 if flop else 4)
    a, b = cards[:2], cards[2:4]
    board = cards[4:] if flop else []
    eqs, n = pm.equity([a, b], board, trials=trials, seed=rng.randrange(1 << 30))
    v = eqs[0]
    labels, correct = pct_choices(round(v * 20) / 20, [v + 0.2, v - 0.2, v + 0.4, v - 0.4], rng, digits=0, gap=0.15)
    how = (f"ターン・リバーの全 {n} 通りを数えた正確な値" if flop else f"{n} 回のランダム試行による近似（誤差 ±2〜3% 程度）")
    explain = f"A のエクイティは {pct(v)}、B は {pct(eqs[1])}（引き分けは半分ずつ）。{how}。"
    q = "A のエクイティ（ショーダウンまで行ったときの取り分）はおよそ？" + ("（フロップ済み）" if flop else "（プリフロップ）")
    return finish("equity", 2, "math", q, labels, correct, explain,
                  "「自分の手はどれくらい勝っているか」の感覚が、ポットオッズと比べるときの材料になります。",
                  "RULE", {"title": "tools/poker_math.py equity（自前の計算）",
                           "url": "https://en.wikipedia.org/wiki/Texas_hold_%27em"},
                  "curriculum/01-terms.md 2.4", rng,
                  cards={"A": [card_view(c) for c in a], "B": [card_view(c) for c in b],
                         "board": [card_view(c) for c in board]})


GENERATORS = {
    "hand_strength": (gen_hand_strength, "役の強さ", 0),
    "hand_compare": (gen_hand_compare, "どっちが勝つ？", 0),
    "hand_name": (gen_hand_name, "役の名前", 0),
    "positions": (gen_positions, "ポジション（図つき）", 0),
    "min_raise": (gen_min_raise, "最小レイズ額", 0),
    "bb_count": (gen_bb_count, "BB換算", 2),
    "preflop_math": (gen_preflop_math, "BBディフェンス・3ベットサイズ", 1),
    "math": (gen_math, "ポーカー数学ミックス", 2),
    "pot_odds": (gen_pot_odds, "ポットオッズ（10秒）", 2),
    "mdf": (gen_mdf, "MDF", 2),
    "alpha": (gen_alpha, "ブラフの損益分岐", 2),
    "outs": (gen_outs, "アウツと完成確率", 2),
    "spr": (gen_spr, "SPR", 2),
    "equity": (gen_equity, "エクイティ感覚", 2),
    "icm": (gen_icm, "ICM（バブルファクター）", 4),
    "structure": (gen_structure, "平均スタック（ストラクチャー）", 7),
}


def generate(name, n, rng=None):
    rng = rng or random.Random()
    fn = GENERATORS[name][0]
    out, keys = [], set()
    for _ in range(n * 6):
        item = fn(rng)
        if item["key"] in keys:
            continue
        keys.add(item["key"])
        out.append(item)
        if len(out) == n:
            break
    return out
