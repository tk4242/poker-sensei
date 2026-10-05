#!/usr/bin/env python3
"""ポーカー計算ツール（標準ライブラリのみ）。

使い方:
  python3 tools/poker_math.py pot-odds --pot 100 --call 50
  python3 tools/poker_math.py mdf --pot 100 --bet 50
  python3 tools/poker_math.py bluff --pot 100 --bet 75
  python3 tools/poker_math.py outs --outs 9 --streets 2
  python3 tools/poker_math.py spr --stack 900 --pot 300
  python3 tools/poker_math.py ev --win-prob 0.4 --win 300 --lose 100
  python3 tools/poker_math.py equity AhKh QsQd --board 2c7dJh --trials 50000

カード表記: ランク(23456789TJQKA) + スート(cdhs)。例: Ah, Td, 7c
"""
import argparse
import itertools
import random
from collections import Counter
from math import comb

RANKS = "23456789TJQKA"
SUITS = "cdhs"
DECK = [r + s for r in RANKS for s in SUITS]


# ---------- 基本の公式 ----------

def pot_odds(pot, call):
    """コールに必要な勝率 = call / (pot + call)。pot はベット込みの現在のポット。"""
    return call / (pot + call)


def mdf(pot, bet):
    """最小防御頻度 MDF = pot / (pot + bet)。pot はベット前のポット。"""
    return pot / (pot + bet)


def bluff_breakeven(pot, bet):
    """ブラフが損益分岐になる相手のフォールド率 = bet / (pot + bet)。"""
    return bet / (pot + bet)


def outs_probability(outs, streets, unseen=None):
    """アウツが少なくとも1枚出る正確な確率。
    streets=1: 次の1枚（未知カード46枚=フロップ後のターン想定、47枚にしたい場合はunseen指定）
    streets=2: フロップからリバーまで（未知47枚から2枚）"""
    if unseen is None:
        unseen = 47 if streets == 2 else 46
    miss = comb(unseen - outs, streets) / comb(unseen, streets)
    return 1 - miss


def rule_of_2_and_4(outs, streets):
    return min(outs * (4 if streets == 2 else 2), 100) / 100


def spr(stack, pot):
    """スタック・トゥ・ポット・レシオ（有効スタック / ポット）。"""
    return stack / pot


def ev(win_prob, win, lose):
    """単純なEV = 勝率×獲得額 − (1−勝率)×損失額。"""
    return win_prob * win - (1 - win_prob) * lose


# ---------- 役の判定 ----------

def _rank_value(card):
    return RANKS.index(card[0]) + 2


def evaluate5(cards):
    """5枚の役を比較可能なタプルで返す（大きいほど強い）。"""
    values = sorted((_rank_value(c) for c in cards), reverse=True)
    suits = [c[1] for c in cards]
    counts = Counter(values)
    # 枚数が多い順 → ランクが高い順
    groups = sorted(counts.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
    ordered = [v for v, _ in groups]
    flush = len(set(suits)) == 1
    uniq = sorted(set(values), reverse=True)
    straight_high = None
    if len(uniq) == 5:
        if uniq[0] - uniq[4] == 4:
            straight_high = uniq[0]
        elif uniq == [14, 5, 4, 3, 2]:  # A-5 ホイール
            straight_high = 5
    if straight_high and flush:
        return (8, straight_high)
    if groups[0][1] == 4:
        return (7, *ordered)
    if groups[0][1] == 3 and groups[1][1] == 2:
        return (6, *ordered)
    if flush:
        return (5, *values)
    if straight_high:
        return (4, straight_high)
    if groups[0][1] == 3:
        return (3, *ordered)
    if groups[0][1] == 2 and groups[1][1] == 2:
        return (2, *ordered)
    if groups[0][1] == 2:
        return (1, *ordered)
    return (0, *values)


def best_hand(cards):
    return max(evaluate5(c) for c in itertools.combinations(cards, 5))


HAND_NAMES = ["ハイカード", "ワンペア", "ツーペア", "スリーカード", "ストレート",
              "フラッシュ", "フルハウス", "フォーカード", "ストレートフラッシュ"]


# ---------- エクイティ ----------

def parse_cards(text):
    text = text.replace(" ", "")
    cards = [text[i:i + 2] for i in range(0, len(text), 2)]
    for c in cards:
        if c not in DECK:
            raise ValueError(f"不正なカード: {c}")
    return cards


def equity(hands, board=(), trials=20000, seed=None):
    """各ハンドのエクイティ（引き分けは等分）。残りが少なければ全探索、多ければモンテカルロ。"""
    used = [c for h in hands for c in h] + list(board)
    if len(set(used)) != len(used):
        raise ValueError("カードが重複しています")
    deck = [c for c in DECK if c not in used]
    need = 5 - len(board)
    shares = [0.0] * len(hands)

    def score(runout):
        full = list(board) + list(runout)
        vals = [best_hand(list(h) + full) for h in hands]
        top = max(vals)
        winners = [i for i, v in enumerate(vals) if v == top]
        for i in winners:
            shares[i] += 1 / len(winners)

    if comb(len(deck), need) <= trials:
        runouts = list(itertools.combinations(deck, need))
        for r in runouts:
            score(r)
        n = len(runouts)
    else:
        rng = random.Random(seed)
        for _ in range(trials):
            score(rng.sample(deck, need))
        n = trials
    return [s / n for s in shares], n


# ---------- CLI ----------

def main():
    p = argparse.ArgumentParser(description="ポーカー計算ツール")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("pot-odds", help="コールに必要な勝率")
    a.add_argument("--pot", type=float, required=True, help="相手のベット込みの現在のポット")
    a.add_argument("--call", type=float, required=True)
    a = sub.add_parser("mdf", help="最小防御頻度")
    a.add_argument("--pot", type=float, required=True, help="ベット前のポット")
    a.add_argument("--bet", type=float, required=True)
    a = sub.add_parser("bluff", help="ブラフの損益分岐フォールド率")
    a.add_argument("--pot", type=float, required=True, help="ベット前のポット")
    a.add_argument("--bet", type=float, required=True)
    a = sub.add_parser("outs", help="アウツから完成確率")
    a.add_argument("--outs", type=int, required=True)
    a.add_argument("--streets", type=int, choices=[1, 2], default=1)
    a = sub.add_parser("spr", help="SPR")
    a.add_argument("--stack", type=float, required=True)
    a.add_argument("--pot", type=float, required=True)
    a = sub.add_parser("ev", help="単純なEV")
    a.add_argument("--win-prob", type=float, required=True)
    a.add_argument("--win", type=float, required=True)
    a.add_argument("--lose", type=float, required=True)
    a = sub.add_parser("equity", help="ハンド同士のエクイティ")
    a.add_argument("hands", nargs="+", help="例: AhKh QsQd")
    a.add_argument("--board", default="")
    a.add_argument("--trials", type=int, default=20000)
    a.add_argument("--seed", type=int)
    args = p.parse_args()

    if args.cmd == "pot-odds":
        print(f"必要勝率: {pot_odds(args.pot, args.call):.1%}")
    elif args.cmd == "mdf":
        print(f"MDF: {mdf(args.pot, args.bet):.1%}")
    elif args.cmd == "bluff":
        print(f"ブラフ損益分岐フォールド率: {bluff_breakeven(args.pot, args.bet):.1%}")
    elif args.cmd == "outs":
        exact = outs_probability(args.outs, args.streets)
        approx = rule_of_2_and_4(args.outs, args.streets)
        print(f"正確な確率: {exact:.1%} / 2と4のルール近似: {approx:.0%} (差 {approx - exact:+.1%})")
    elif args.cmd == "spr":
        print(f"SPR: {spr(args.stack, args.pot):.2f}")
    elif args.cmd == "ev":
        print(f"EV: {ev(args.win_prob, args.win, args.lose):+.2f}")
    elif args.cmd == "equity":
        hands = [parse_cards(h) for h in args.hands]
        board = parse_cards(args.board) if args.board else []
        eqs, n = equity(hands, board, args.trials, args.seed)
        for h, e in zip(args.hands, eqs):
            print(f"{h}: {e:.1%}")
        print(f"（試行/列挙数: {n}）")


if __name__ == "__main__":
    main()
