"""AIコーチ（任意）。ANTHROPIC_API_KEY を設定したときだけ有効。

- 1回ごとに独立したリクエスト（直近のやり取りは要約テキストとして渡す）。履歴の書き換え問題が起きず、トークンも節約できる。
- Web検索ツールは信頼できるドメインだけに限定し、回答に出典URLを必ず付けさせる。
"""
import json

from flask import current_app

SYSTEM = """あなたは「ポーカー先生」のヘッドコーチです。学習者（Mr古謝）を、用語も怪しい初心者から海外トーナメント（MTT）でインマネできるレベルまで育てます。

絶対ルール:
- 戦略・数字・ルール・法律の主張には、必ず出典URLを付ける。自信がない内容は web_search で確認してから答える。確認できなければ「未確認」と明言し、推測で埋めない。
- 「GTO（ソルバー基準）」と「エクスプロイト（相手の傾向に合わせた調整）」を必ずラベルで区別する。相手層の傾向は一般論・観察であり保証ではないと書く。
- 日本国内で現金を賭けるポーカー（賭けたホームゲーム）や、日本居住者が日本からリアルマネーのオンラインポーカーに参加することは違法になりうる。勧めない。練習はアミューズメント（換金なし）や換金できない国内アプリで。
- 数値を出すときは式と計算を示す（ポットオッズ = コール ÷（ベット込みポット＋コール）、MDF = ポット ÷（ポット＋ベット）など）。
- 情報源の信頼度: 一次情報（Poker TDA、法令 e-Gov、警察庁、国税庁、大会公式）＞ 実績ある戦略サイト（GTO Wizard、Upswing、Red Chip、PokerNews、PokerCoaching）＞ 個人ブログ。食い違うときは両方載せて理由を書く。

話し方:
- 日本語。親しみやすく、毎回前向きに鼓舞する。ただし褒めるために事実を曲げない。
- 結論 → 理由 → 出典 の順。専門用語は初出で「日本語（English）」と一言説明。
- 短く。長くても見出し3つ・箇条書き中心で、スマホで読める量にする。最後に「次にやること」を1つだけ示す。
"""

ALLOWED_DOMAINS = [
    "pokertda.com", "e-gov.go.jp", "npa.go.jp", "nta.go.jp", "mofa.go.jp", "irs.gov",
    "gtowizard.com", "upswingpoker.com", "redchippoker.com", "pokernews.com", "pokercoaching.com",
    "runitonce.com", "jaredtendler.com", "wikipedia.org", "wsop.com", "theasianpokertour.com",
    "worldpokertour.com", "pokerstars.com", "japanopenpoker.com", "jonathanlittlepoker.com", "pokerlistings.com",
]


def enabled():
    return bool(current_app.config.get("ANTHROPIC_API_KEY"))


def _client():
    import anthropic
    return anthropic.Anthropic(api_key=current_app.config["ANTHROPIC_API_KEY"], timeout=180.0, max_retries=2)


def ask(question, learner_summary, recent=None, mode="chat"):
    """戻り値: (回答テキスト, 出典リスト[{title,url}], エラー文字列 or None)"""
    import anthropic

    context = f"【学習者の現状（アプリの記録から自動作成）】\n{learner_summary}\n"
    if recent:
        context += "\n【直近のやり取り（要約用。古い順）】\n" + "\n".join(
            f"Q: {r['question'][:300]}\nA: {r['answer'][:500]}" for r in recent)
    task = {"chat": "次の質問に答えてください。",
            "hand": "次のハンドをストリートごとに検討してください。良かった点、改善点（GTO基準とエクスプロイトを分けて）、学ぶべき概念、計算を示してください。"}[mode]
    messages = [{"role": "user", "content": f"{context}\n{task}\n\n{question}"}]
    tools = [{"type": "web_search_20260209", "name": "web_search", "max_uses": 5,
              "allowed_domains": ALLOWED_DOMAINS}]
    params = dict(model=current_app.config["COACH_MODEL"], max_tokens=16000, system=SYSTEM, tools=tools,
                  output_config={"effort": current_app.config.get("COACH_EFFORT", "medium")},
                  betas=["server-side-fallback-2026-07-01"], fallbacks="default")
    client = _client()
    try:
        resp = client.beta.messages.create(messages=messages, **params)
        for _ in range(4):  # サーバー側ツールの上限で一時停止したら続きから再開
            if resp.stop_reason != "pause_turn":
                break
            messages = messages[:1] + [{"role": "assistant", "content": resp.content}]
            resp = client.beta.messages.create(messages=messages, **params)
    except anthropic.AuthenticationError:
        return "", [], "APIキーが無効です（.env の ANTHROPIC_API_KEY を確認）。"
    except anthropic.RateLimitError:
        return "", [], "API の利用上限に達しました。少し時間をおいてください。"
    except anthropic.APIStatusError as e:
        return "", [], f"API エラー（{e.status_code}）。時間をおいて再試行してください。"
    except anthropic.APIConnectionError:
        return "", [], "API に接続できませんでした（VPS のネットワークを確認）。"

    if resp.stop_reason == "refusal":
        return "", [], "この質問には回答できませんでした。言い方を変えて質問してください。"
    texts, cites = [], []
    seen = set()
    for block in resp.content:
        if block.type == "text":
            texts.append(block.text)
            for c in getattr(block, "citations", None) or []:
                url = getattr(c, "url", None)
                if url and url not in seen:
                    seen.add(url)
                    cites.append({"title": getattr(c, "title", None) or url, "url": url})
    answer = "".join(texts).strip()
    if resp.stop_reason == "max_tokens":
        answer += "\n\n（長すぎて途中で切れました。質問を分けてください）"
    return answer, cites, None


def citations_json(cites):
    return json.dumps(cites, ensure_ascii=False)
