"""自動で育つ知識ベース（API は呼ばず、偽の応答で確認）。Flask がなければスキップ。"""
import json
import re
import unittest
from types import SimpleNamespace as NS
from unittest import mock

from test_app import HAVE_FLASK, login, make_app

CARD = {"title": "BBAではBBが広く守る", "summary": "BBアンテでは…", "why": "守る範囲が分かる", "label": "GTO",
        "claims": [{"text": "BBAでは必要エクイティが下がる", "url": "https://blog.gtowizard.com/x/", "quote": "lower equity"}],
        "quiz": {"q": "BBAでBBの必要エクイティは？", "choices": ["下がる", "上がる", "変わらない", "ゼロ"], "answer": 0,
                 "explain": "ポットが大きくなるため"}}


def fake_client(replies, calls):
    class Messages:
        def create(self, **kw):
            calls.append(kw)
            text = replies[min(len(calls) - 1, len(replies) - 1)]
            return NS(stop_reason="end_turn", usage=NS(input_tokens=1000, output_tokens=500,
                                                       server_tool_use=NS(web_search_requests=2)),
                      content=[NS(type="server_tool_use"), NS(type="text", text=text)])
    return NS(beta=NS(messages=Messages()))


@unittest.skipUnless(HAVE_FLASK, "Flask 未インストール")
class TestKnowledge(unittest.TestCase):
    def setUp(self):
        self.app = make_app(ANTHROPIC_API_KEY="sk-test")

    def run_collect(self, verify_reply):
        from sensei import coach, knowledge
        calls = []
        fake = fake_client([json.dumps({"cards": [CARD, {"title": "出典なし", "summary": "x", "claims": []}]}),
                            json.dumps(verify_reply)], calls)
        with self.app.app_context(), mock.patch.object(coach, "_client", return_value=fake):
            n, err = knowledge.collect("preflop")
            cards = knowledge.cards()
        return n, err, cards, calls

    def test_collect_verify_approve_and_train(self):
        n, err, cards, calls = self.run_collect({"verdict": "ok", "notes": "一致", "claims": [{"ok": True}], "quiz_ok": True})
        self.assertIsNone(err)
        self.assertEqual(n, 1)  # 出典のないカードは捨てる
        self.assertEqual(cards[0]["status"], "verified")
        self.assertEqual(calls[0]["tools"][0]["type"], "web_search_20260209")
        self.assertEqual(calls[1]["tools"][0]["type"], "web_fetch_20260209")
        self.assertEqual(calls[1]["output_config"], {"effort": "low"})
        c = self.app.test_client()
        login(c)
        page = c.get("/knowledge").text
        self.assertIn("BBAではBBが広く守る", page)
        with c.session_transaction() as s:
            tok = s["csrf"]
        c.post(f"/knowledge/{cards[0]['id']}/approve", data={"csrf": tok})
        self.assertIn("BBAではBBが広く守る", c.get("/learn/stage/1").text)
        r = c.get("/train/news")
        self.assertEqual(r.status_code, 200)
        self.assertIn("BBAでBBの必要エクイティは？", r.text)
        with self.app.app_context():
            from sensei import knowledge
            self.assertGreater(knowledge.month_cost(), 0)

    def test_verify_failures(self):
        _, _, cards, _ = self.run_collect({"verdict": "ok", "claims": [{"ok": False}], "quiz_ok": True})
        self.assertEqual(cards[0]["status"], "needs_fix")
        self.setUp()
        _, _, cards, _ = self.run_collect({"verdict": "reject", "claims": [{"ok": False}]})
        self.assertEqual(cards[0]["status"], "rejected")

    def test_budget_stops_runs(self):
        from sensei import coach, knowledge
        from sensei.db import set_setting
        with self.app.app_context(), mock.patch.object(coach, "_client") as m:
            set_setting("knowledge_budget_usd", 0)
            n, err = knowledge.collect()
            self.assertEqual(n, 0)
            self.assertIn("上限", err)
            m.assert_not_called()

    def test_bad_json_is_logged(self):
        from sensei import coach, knowledge
        fake = fake_client(["すみません、JSONではありません"], [])
        with self.app.app_context(), mock.patch.object(coach, "_client", return_value=fake):
            n, err = knowledge.collect()
            self.assertEqual(n, 0)
            self.assertTrue(knowledge.q("SELECT error FROM kruns", one=True)["error"])

    def test_clean_card(self):
        from sensei.knowledge import clean_card, parse_json
        bad = dict(CARD, quiz={"q": "x", "choices": ["a", "a", "b", "c"], "answer": 0})
        self.assertIsNone(clean_card(bad)["quiz"])
        self.assertIsNone(clean_card(dict(CARD, claims=[{"text": "t", "url": "http://insecure"}])))
        self.assertEqual(clean_card(dict(CARD, label="???"))["label"], "THEORY")
        self.assertEqual(parse_json('前置き {"cards": []} 後書き'), {"cards": []})

    def test_page_without_ai(self):
        app = make_app()
        c = app.test_client()
        login(c)
        page = c.get("/knowledge").text
        self.assertIn("AI が未設定です", page)
        self.assertIsNone(re.search(r'action="/knowledge/run"', page))
