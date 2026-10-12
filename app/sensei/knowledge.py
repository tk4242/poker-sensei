"""自動で育つ知識ベース（任意。ANTHROPIC_API_KEY が必要）。

流れ: ① 収集（Web検索で信頼できるサイトから、出典と原文の引用つきの「知識カード」の下書きを作る）
      ② 検証（別の呼び出しで出典ページを実際に開き、主張と原文が一致するか確かめる）
      ③ 承認（本人がアプリで確認して承認したものだけが教材として表示され、問題として出題される）
      ④ 鮮度（承認から90日を超えたカードは「要再確認」。再検証できる）
料金の目安を記録し、月の上限額を超えそうなら実行しない。VPS の cron から週1回 `python -m sensei knowledge-run`。
"""
import json
import re
from datetime import timedelta

from flask import current_app

from . import coach
from .db import ex, get_setting, iso, now, q

# ロードマップのステージごとの調べるテーマ（古いものから順に回す）
TOPICS = [
    {"key": "preflop", "stage": 1, "q": "MTTのプリフロップ（オープンサイズ、3ベット、BBディフェンス、アンテ/BBAの影響）"},
    {"key": "math", "stage": 2, "q": "ポーカー数学（ポットオッズ、MDF、ブラフの損益分岐、EV、SPR）の実戦での使い方"},
    {"key": "postflop", "stage": 3, "q": "MTTのポストフロップ（Cベットのサイズ、ボードの質感、ターン・リバーの方針）"},
    {"key": "icm", "stage": 4, "q": "トーナメント特有の戦略（ICM、バブル、ファイナルテーブル、PKO、ショートスタック）"},
    {"key": "live", "stage": 5, "q": "ライブトーナメントのエクスプロイト、テル、ルールとエチケット（Poker TDA）"},
    {"key": "mental", "stage": 6, "q": "ポーカーのメンタルゲーム、ティルト対策、バンクロール管理"},
    {"key": "overseas", "stage": 7, "q": "初めての海外ライブMTT（アジア・米国・欧州の大会の選び方、ストラクチャー、税金・渡航の注意）の最新情報"},
]
LABELS = ["GTO", "EXP", "RULE", "MENTAL", "THEORY"]
STALE_DAYS = 90
MAX_CARDS = 3

COLLECT_SYSTEM = coach.SYSTEM + """
今回の仕事: 学習アプリの「知識カード」の下書きを作る。web_search で信頼できる情報源を調べ、最新で実戦に役立つ知識を最大{n}件選ぶ。
厳守:
- 1つの主張には1つの出典URLと、そのページの原文からの短い引用（英語ならそのまま）を付ける。引用できない主張は書かない。
- ソルバー（GTO）由来か、相手層への調整（エクスプロイト）か、ルール・定義か、メンタルか、戦略サイトの一般則かを label で区別する。
- 日本からのリアルマネー・オンラインポーカーや賭けたホームゲームを勧める内容は作らない。
- 最後の返答は JSON だけ（説明文やコードブロックの記号なし）で、次の形にする:
{{"cards":[{{"title":"短い見出し","summary":"初心者向けの日本語の説明（3〜5文）","why":"実戦でどう役立つか（1文）","label":"GTO|EXP|RULE|MENTAL|THEORY",
"claims":[{{"text":"主張（日本語）","url":"出典URL","quote":"原文の引用"}}],
"quiz":{{"q":"確認問題","choices":["正解","誤答1","誤答2","誤答3"],"answer":0,"explain":"解説"}}}}]}}
"""

VERIFY_SYSTEM = """あなたはポーカー教材のファクトチェッカーです。渡された知識カードの各主張について、web_fetch で出典URLを実際に開き、
原文に引用と主張の内容が本当に書かれているかを確認します。推測で「正しい」としない。開けなかった主張は ok=false。
確認問題は、正解が主張から導けて、ほかの3つの選択肢が明確に誤りかを確かめる。
返答は JSON だけ: {"verdict":"ok|fix|reject","notes":"日本語で短く","claims":[{"ok":true,"note":"短く"}],"quiz_ok":true}
verdict: すべての主張と問題が正しい→ok / 直せば使える→fix / 出典と合わない・危険→reject"""


def enabled():
    return coach.enabled()


def _price():
    c = current_app.config
    return (float(c.get("KNOWLEDGE_PRICE_IN", 4.0)), float(c.get("KNOWLEDGE_PRICE_OUT", 20.0)),
            float(c.get("KNOWLEDGE_PRICE_SEARCH", 0.01)))


def budget():
    try:
        v = get_setting("knowledge_budget_usd", None)
        return 5.0 if v in (None, "") else float(v)
    except (TypeError, ValueError):
        return 5.0


def month_cost():
    start = now().date().replace(day=1).isoformat()
    return q("SELECT COALESCE(SUM(cost_usd),0) c FROM kruns WHERE ts>=?", (start,), one=True)["c"]


def _cost(usage):
    pin, pout, psearch = _price()
    if usage is None:
        return 0.0
    tin = (getattr(usage, "input_tokens", 0) or 0) + (getattr(usage, "cache_creation_input_tokens", 0) or 0) \
        + (getattr(usage, "cache_read_input_tokens", 0) or 0)
    tout = getattr(usage, "output_tokens", 0) or 0
    stu = getattr(usage, "server_tool_use", None)
    searches = (getattr(stu, "web_search_requests", 0) or 0) if stu else 0
    return tin / 1e6 * pin + tout / 1e6 * pout + searches * psearch


def _call(system, user, tools, effort):
    """1回の独立したリクエスト（pause_turn は最大4回まで再開）。(最後のテキスト, 料金の目安)"""
    client = coach._client()
    messages = [{"role": "user", "content": user}]
    params = dict(model=current_app.config["COACH_MODEL"], max_tokens=16000, system=system, tools=tools,
                  output_config={"effort": effort}, betas=["server-side-fallback-2026-07-01"], fallbacks="default")
    resp = client.beta.messages.create(messages=messages, **params)
    cost = _cost(getattr(resp, "usage", None))
    for _ in range(4):
        if resp.stop_reason != "pause_turn":
            break
        messages = messages[:1] + [{"role": "assistant", "content": resp.content}]
        resp = client.beta.messages.create(messages=messages, **params)
        cost += _cost(getattr(resp, "usage", None))
    if resp.stop_reason == "refusal":
        raise RuntimeError("API が回答を断りました")
    # ツールの結果より後ろのテキストだけが最終回答
    texts = []
    for block in resp.content:
        if block.type == "text":
            texts.append(block.text)
        elif block.type != "text" and texts:
            texts = []
    return "".join(texts).strip(), cost


def parse_json(text):
    try:
        return json.loads(text)
    except ValueError:
        m = re.search(r"\{.*\}", text, re.S)
        if not m:
            raise ValueError("JSON がありません")
        return json.loads(m.group(0))


def clean_card(c):
    """モデルの出力を検証して整える。条件を満たさなければ None。"""
    try:
        claims = [{"text": str(x["text"])[:500], "url": str(x["url"]), "quote": str(x.get("quote", ""))[:500]}
                  for x in c.get("claims", []) if str(x.get("url", "")).startswith("https://")]
        if not claims or not c.get("title") or not c.get("summary"):
            return None
        label = c.get("label") if c.get("label") in LABELS else "THEORY"
        quiz = c.get("quiz") or None
        if quiz:
            ch = [str(x) for x in quiz.get("choices", [])]
            a = quiz.get("answer")
            if len(ch) != 4 or len(set(ch)) != 4 or not isinstance(a, int) or not 0 <= a < 4 or not quiz.get("q"):
                quiz = None
            else:
                quiz = {"q": str(quiz["q"]), "choices": ch, "answer": a, "explain": str(quiz.get("explain", ""))}
        return {"title": str(c["title"])[:120], "summary": str(c["summary"])[:1500], "why": str(c.get("why", ""))[:300],
                "label": label, "claims": claims, "quiz": quiz}
    except (KeyError, TypeError, AttributeError):
        return None


def next_topic():
    last = {r["topic"]: r["ts"] for r in q("SELECT topic, MAX(ts) ts FROM kruns WHERE kind='collect' GROUP BY topic")}
    return sorted(TOPICS, key=lambda t: last.get(t["key"], ""))[0]


def _log(kind, topic, cost, n, err=None):
    ex("INSERT INTO kruns(ts,kind,topic,cost_usd,n_cards,error) VALUES(?,?,?,?,?,?)",
       (iso(now()), kind, topic, round(cost, 4), n, err))


def collect(topic=None):
    """1テーマ分を収集→検証して保存。戻り値: (保存したカード数, エラー文字列 or None)"""
    if not enabled():
        return 0, "AI が未設定です（.env の ANTHROPIC_API_KEY）。"
    if month_cost() >= budget():
        return 0, f"今月の上限 ${budget():.2f} に達しています（設定で変更できます）。"
    t = next(x for x in TOPICS if x["key"] == topic) if topic else next_topic()
    known = [r["title"] for r in q("SELECT title FROM kcards WHERE topic=? ORDER BY id DESC LIMIT 30", (t["key"],))]
    user = (f"テーマ: {t['q']}（ロードマップ Stage {t['stage']}）\n今日: {now().date().isoformat()}\n"
            + ("すでにあるカード（重複させない）: " + " / ".join(known) + "\n" if known else "")
            + "海外トーナメントで初めてのインマネを目指す初心者〜中級者に役立つものを選んでください。")
    tools = [{"type": "web_search_20260209", "name": "web_search", "max_uses": 5,
              "allowed_domains": coach.ALLOWED_DOMAINS}]
    try:
        text, cost = _call(COLLECT_SYSTEM.format(n=MAX_CARDS), user, tools, "medium")
        cards = [c for c in (clean_card(x) for x in parse_json(text).get("cards", [])[:MAX_CARDS]) if c]
    except Exception as e:  # API・JSON どちらの失敗も記録して止める
        _log("collect", t["key"], 0, 0, f"{type(e).__name__}: {e}"[:300])
        return 0, "収集に失敗しました（記録を確認）。"
    _log("collect", t["key"], cost, len(cards))
    saved = 0
    for c in cards:
        if month_cost() >= budget():
            break
        cid = ex("""INSERT INTO kcards(created,topic,stage,title,summary,why,label,claims,quiz,status)
                    VALUES(?,?,?,?,?,?,?,?,?,'draft')""",
                 (iso(now()), t["key"], t["stage"], c["title"], c["summary"], c["why"], c["label"],
                  json.dumps(c["claims"], ensure_ascii=False), json.dumps(c["quiz"], ensure_ascii=False) if c["quiz"] else None))
        verify(cid)
        saved += 1
    return saved, None


def verify(cid):
    """出典ページを開いて検証。status を verified / needs_fix / rejected にする。"""
    card = get(cid)
    if not card or not enabled():
        return None
    tools = [{"type": "web_fetch_20260209", "name": "web_fetch", "max_uses": max(3, len(card["claims"])),
              "allowed_domains": coach.ALLOWED_DOMAINS}]
    body = json.dumps({k: card[k] for k in ("title", "summary", "label", "claims", "quiz")}, ensure_ascii=False)
    try:
        text, cost = _call(VERIFY_SYSTEM, "このカードを検証してください:\n" + body, tools, "low")
        v = parse_json(text)
    except Exception as e:
        _log("verify", card["topic"], 0, 0, f"{type(e).__name__}: {e}"[:300])
        ex("UPDATE kcards SET status='needs_fix', verify_note=? WHERE id=?", ("検証に失敗（あとで再検証）", cid))
        return "needs_fix"
    _log("verify", card["topic"], cost, 1)
    verdict = v.get("verdict")
    claims_ok = all(x.get("ok") for x in v.get("claims", [])) and len(v.get("claims", [])) == len(card["claims"])
    if verdict == "ok" and claims_ok and (card["quiz"] is None or v.get("quiz_ok")):
        status = "verified"
    elif verdict == "reject":
        status = "rejected"
    else:
        status = "needs_fix"
    keep = "approved" if card["status"] == "approved" and status == "verified" else status
    ex("UPDATE kcards SET status=?, verify_note=?, checked_at=? WHERE id=?",
       (keep, str(v.get("notes", ""))[:800], iso(now()), cid))
    return keep


def get(cid):
    r = q("SELECT * FROM kcards WHERE id=?", (cid,), one=True)
    return _row(r) if r else None


def _row(r):
    d = dict(r)
    d["claims"] = json.loads(d["claims"] or "[]")
    d["quiz"] = json.loads(d["quiz"]) if d["quiz"] else None
    ref = d["checked_at"] or d["created"]
    d["stale"] = d["status"] == "approved" and ref < iso(now() - timedelta(days=STALE_DAYS))
    return d


def cards(status=None, stage=None, limit=100):
    sql, args = "SELECT * FROM kcards WHERE 1=1", []
    if status:
        sql += " AND status=?"
        args.append(status)
    if stage is not None:
        sql += " AND stage=?"
        args.append(stage)
    return [_row(r) for r in q(sql + " ORDER BY id DESC LIMIT ?", (*args, limit))]


def set_status(cid, status):
    ex("UPDATE kcards SET status=?, approved_at=? WHERE id=?",
       (status, iso(now()) if status == "approved" else None, cid))


def quiz_items(stage=None):
    """承認済みカードの確認問題を、問題集と同じ形で返す（トレーニング・復習で出題）。"""
    out = []
    for c in cards("approved", stage):
        if not c["quiz"] or c["stale"]:
            continue
        z = c["quiz"]
        out.append({"kind": "bank", "id": f"kc{c['id']}", "key": f"kc:{c['id']}", "stage": c["stage"], "tag": "news",
                    "tags": ["news"], "q": z["q"], "choices": z["choices"], "answer": z["answer"],
                    "explain": z["explain"], "why": c["why"] or "最新の知識を実戦に結びつけるため。", "label": c["label"],
                    "source": [{"title": x["url"].split("/")[2], "url": x["url"]} for x in c["claims"]],
                    "ref": f"知識カード「{c['title']}」（承認済み・AI収集）"})
    return out
