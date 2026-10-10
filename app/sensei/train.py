"""いつでもトレーニング: 1問ずつすぐ答え合わせする反復練習（バトル形式）と、レベル・経験値の計算。

問題は既存のドリル（tools/poker_math.py で答えを計算）と出典つき問題集だけから出す。
記録は通常の練習と同じ attempts / srs に入るので、間違えた問題は復習にも回る。
"""
import json
import random
from datetime import timedelta

from . import content, drills, practice, progress
from .db import ex, iso, now, q

# まもの（テーマ）。sprite は static/sprites/ のオリジナルのドット絵
TOPICS = {
    "auto": {"name": "おまかせ（苦手＋復習）", "monster": "たからばこモドキ", "sprite": "mimic",
             "desc": "復習待ちと苦手なテーマを優先して出します。迷ったらここ。"},
    "ev": {"name": "期待値（EV）", "monster": "イーブイゴースト", "sprite": "ghost",
           "spec": {"gen": "ev", "bank": {"stage": 2, "tags": ["ev"]}}, "desc": "繰り返したときの平均で考える"},
    "bet": {"name": "ベットの大きさ＝値段", "monster": "ベットバット", "sprite": "bat",
            "spec": {"gen": "bet_price", "bank": {"stage": 2, "tags": ["bet-size"]}}, "desc": "サイズを見た瞬間に必要勝率"},
    "call": {"name": "コール？フォールド？", "monster": "オッズナイト", "sprite": "knight",
             "spec": {"gen": "call_decision"}, "desc": "必要勝率と自分の勝率を比べて決める"},
    "outs": {"name": "アウツと完成確率", "monster": "アウツゴブリン", "sprite": "goblin",
             "spec": {"gen": "outs", "bank": {"stage": 2, "tags": ["outs"]}}, "desc": "2と4のルールと正確な値"},
    "pot_odds": {"name": "ポットオッズ早撃ち", "monster": "ポットオッズバット", "sprite": "bat",
                 "spec": {"gen": "pot_odds"}, "desc": "10秒以内が目標（Stage 2 の合格ライン）"},
    "math": {"name": "数学ミックス", "monster": "すうしきドラゴン", "sprite": "dragon",
             "spec": {"gen": "math"}, "desc": "ポットオッズ・MDF・α・SPR・EV のまぜこぜ"},
    "hands": {"name": "役の強さ", "monster": "カードスライダー", "sprite": "goblin",
              "spec": {"gen": "hand_strength"}, "desc": "Stage 0 の合格ライン（10問中10問）"},
    "positions": {"name": "ポジション（図つき）", "monster": "ポジションナイト", "sprite": "knight",
                  "spec": {"gen": "positions"}, "desc": "席の名前と動く順番"},
    "preflop": {"name": "プリフロップ", "monster": "ブラインドオーガ", "sprite": "ogre",
                "spec": {"gen": "preflop_math", "bank": {"stage": 1}}, "desc": "3ベットサイズ・BBディフェンス・原則"},
    "icm": {"name": "ICM・バブル", "monster": "バブルドラゴン", "sprite": "dragon",
            "spec": {"gen": "icm", "bank": {"stage": 4}}, "desc": "海外MTTのインマネ直前で効く"},
    "mental": {"name": "メンタル・同調", "monster": "ドウチョウゴーレム", "sprite": "golem",
               "spec": {"bank": {"stage": 6}}, "desc": "ティルト・バンクロール・周りに流されない"},
}

PLAYER_HP = 5
MONSTER_HP = 5
CRIT_MS = 5000  # 5秒以内に正解で「かいしんのいちげき」（2ダメージ）。アプリの遊びのルール


# ---------------------------------------------------------------- レベルと称号

def exp_total():
    """経験値: 正解 10、不正解・わからない 2（挑戦したこと自体も少し評価する）＋ 昇段試験の合格 100。"""
    r = q("SELECT COUNT(*) n, COALESCE(SUM(correct),0) c FROM attempts", one=True)
    passed = q("SELECT COUNT(DISTINCT req_id) c FROM exams WHERE passed=1", one=True)["c"]
    return r["c"] * 10 + (r["n"] - r["c"]) * 2 + passed * 100


def level_of(exp):
    """レベル L に必要な累計経験値は 25×L×(L−1)。(レベル, 今のレベルでの経験値, 次までに必要な量)"""
    lv = 1
    while 25 * (lv + 1) * lv <= exp:
        lv += 1
    base = 25 * lv * (lv - 1)
    return lv, exp - base, 25 * (lv + 1) * lv - base


TITLES = ["たびびと", "みならいプレイヤー", "さんすうつかい", "ボードよみ", "トーナメントけんし",
          "よみのたつじん", "こころのたつじん", "えんせいゆうしゃ"]


def status():
    exp = exp_total()
    lv, cur, need = level_of(exp)
    stages, current = progress.overview()
    all_passed = all(s["passed"] for s in stages)
    title = "インマネゆうしゃ" if all_passed else TITLES[min(current, len(TITLES) - 1)]
    return {"exp": exp, "lv": lv, "cur": cur, "need": need, "title": title, "stage": current}


# ---------------------------------------------------------------- 出題

def _spec_item(spec, rng, avoid):
    kinds = [k for k in ("gen", "bank") if spec.get(k)]
    rng.shuffle(kinds)
    for kind in kinds:
        if kind == "gen":
            for item in drills.generate(spec["gen"], 3, rng):
                if item["key"] not in avoid:
                    return item
        else:
            for item in practice._bank_pick(spec["bank"], 6, rng):
                if item["key"] not in avoid:
                    return item
    return None


def _auto_item(rng, avoid):
    if practice.due_count() and rng.random() < 0.4:
        for item in practice.due_items(10):
            if item["key"] not in avoid:
                return item
    weak = practice.weak_tags()
    if weak and rng.random() < 0.7:
        from .views.practice import TAG_GEN
        tag = rng.choice(weak[:3])["tag"]
        spec = {}
        if content.bank_select(tags=[tag]):
            spec["bank"] = {"tags": [tag]}
        if tag in TAG_GEN:
            spec["gen"] = TAG_GEN[tag]
        item = _spec_item(spec, rng, avoid) if spec else None
        if item:
            return item
    # 今のステージのレッスンのドリルから
    stages, current = progress.overview()
    open_stages = [s for s in stages if s["unlocked"]]
    cur = next(s for s in stages if s["stage"] == current)
    pool = [le["drill"] for le in cur["lessons"]] + [le["drill"] for s in open_stages for le in s["lessons"]]
    for _ in range(4):
        item = _spec_item(rng.choice(pool), rng, avoid)
        if item:
            return item
    return None


def new_question(topic, avoid=(), rng=None):
    """出題して train_q に保存。(id, 問題) を返す。"""
    rng = rng or random.Random()
    avoid = set(avoid)
    t = TOPICS[topic]
    item = _auto_item(rng, avoid) if topic == "auto" else _spec_item(t["spec"], rng, avoid)
    if item is None:  # 避ける問題しか残っていなければ、避けずに出す
        item = _auto_item(rng, set()) if topic == "auto" else _spec_item(t["spec"], rng, set())
    if item is None:
        return None, None
    item = practice.shuffled(item, rng)
    # 答えずに放置された古い問題は掃除する
    ex("DELETE FROM train_q WHERE answered IS NULL AND created<?", (iso(now() - timedelta(days=1)),))
    qid = ex("INSERT INTO train_q(created,topic,question) VALUES(?,?,?)",
             (iso(now()), topic, json.dumps(item, ensure_ascii=False)))
    return qid, item


def load(qid):
    row = q("SELECT * FROM train_q WHERE id=?", (qid,), one=True)
    if not row:
        return None
    r = dict(row)
    r["question"] = json.loads(r["question"])
    return r


def answer(row, chosen, ms):
    """採点して記録（attempts と 間隔反復）。正解なら True。"""
    item = row["question"]
    dontknow = chosen is None or chosen < 0
    correct = (not dontknow) and chosen == item["answer"]
    ex("UPDATE train_q SET chosen=?, correct=?, elapsed_ms=?, answered=? WHERE id=?",
       (chosen, int(correct), ms, iso(now()), row["id"]))
    ex("""INSERT INTO attempts(ts,mode,kind,qkey,tag,stage,correct,dontknow,elapsed_ms,batch_id)
          VALUES(?,?,?,?,?,?,?,?,?,NULL)""",
       (iso(now()), "train", item["kind"], item["key"], item["tag"], item.get("stage"), int(correct),
        int(dontknow), ms))
    practice.update_srs(item, correct)
    return correct


# ---------------------------------------------------------------- バトルの状態（ログイン中のセッションに保存）

def new_battle(topic, level=1):
    return {"topic": topic, "php": PLAYER_HP, "mlv": level, "mhp": MONSTER_HP + min(level - 1, 3),
            "mmax": MONSTER_HP + min(level - 1, 3), "n": 0, "c": 0, "streak": 0, "best": 0, "defeated": 0,
            "recent": [], "over": False}


def apply(b, correct, ms, key):
    """1問の結果をバトルに反映して、表示するメッセージのリストを返す。"""
    t = TOPICS[b["topic"]]
    msgs = []
    b["n"] += 1
    b["recent"] = (b["recent"] + [key])[-8:]
    if correct:
        b["c"] += 1
        b["streak"] += 1
        b["best"] = max(b["best"], b["streak"])
        crit = ms is not None and ms <= CRIT_MS
        dmg = 2 if crit else 1
        if crit:
            msgs.append("かいしんの いちげき！")
        b["mhp"] = max(0, b["mhp"] - dmg)
        msgs.append(f"{t['monster']}に {dmg} の ダメージ！")
        if b["streak"] in (5, 10, 20, 30):
            msgs.append(f"{b['streak']}れんぞく せいかい！ のりにのっている！")
        if b["mhp"] == 0:
            b["defeated"] += 1
            msgs.append(f"{t['monster']}を たおした！")
            nxt = new_battle(b["topic"], b["mlv"] + 1)
            b.update(mlv=nxt["mlv"], mhp=nxt["mhp"], mmax=nxt["mmax"])
            msgs.append(f"つよくなった {t['monster']} Lv{b['mlv']} が あらわれた！")
    else:
        b["streak"] = 0
        b["php"] = max(0, b["php"] - 1)
        msgs.append(f"{t['monster']}の こうげき！ 1 の ダメージを うけた。")
        if b["php"] == 0:
            b["over"] = True
            msgs.append("ちからつきた…… でも まちがえた問題は 復習に 入った。経験値も のこっている！")
    return msgs
