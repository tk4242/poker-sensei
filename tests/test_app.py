"""学習Webアプリ（app/）のテスト。Flask が入っていない環境ではスキップ（pip install -r app/requirements.txt）。"""
import random
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))

try:
    import flask  # noqa: F401
    HAVE_FLASK = True
except ImportError:
    HAVE_FLASK = False

PASSWORD = "correct-horse-battery"


def make_app(**kw):
    from sensei import create_app
    d = tempfile.mkdtemp()
    cfg = dict(TESTING=True, SECRET_KEY="x" * 40, APP_USER="koja", APP_PASSWORD=PASSWORD, APP_PASSWORD_HASH="",
               DB_PATH=Path(d) / "t.db", SECURE_COOKIES=False, ANTHROPIC_API_KEY="")
    cfg.update(kw)
    return create_app(**cfg)


def csrf(html):
    return re.search(r'name="csrf" value="([0-9a-f]+)"', html).group(1)


def login(client, password=PASSWORD):
    tok = csrf(client.get("/login").text)
    return client.post("/login", data={"csrf": tok, "user": "koja", "password": password})


@unittest.skipUnless(HAVE_FLASK, "Flask 未インストール")
class TestAuth(unittest.TestCase):
    def setUp(self):
        self.app = make_app()
        self.c = self.app.test_client()

    def test_login_required(self):
        r = self.c.get("/")
        self.assertEqual(r.status_code, 302)
        self.assertIn("/login", r.headers["Location"])
        self.assertEqual(self.c.get("/health").status_code, 200)

    def test_login_and_logout(self):
        self.assertEqual(login(self.c).headers["Location"], "/")
        self.assertEqual(self.c.get("/").status_code, 200)
        tok = csrf(self.c.get("/settings").text)
        self.c.post("/logout", data={"csrf": tok})
        self.assertEqual(self.c.get("/").status_code, 302)

    def test_wrong_password_and_lockout(self):
        for _ in range(5):
            self.assertEqual(login(self.c, "wrong-password-xx").status_code, 401)
        # 6回目は正しいパスワードでもロック
        self.assertEqual(login(self.c).status_code, 429)

    def test_csrf_required(self):
        login(self.c)
        r = self.c.post("/settings", data={"daily_quota": "50"})
        self.assertEqual(r.status_code, 400)

    def test_open_redirect_blocked(self):
        tok = csrf(self.c.get("/login").text)
        r = self.c.post("/login?next=//evil.example", data={"csrf": tok, "user": "koja", "password": PASSWORD})
        self.assertEqual(r.headers["Location"], "/")

    def test_password_hash(self):
        from sensei.auth import hash_password, verify_hash
        h = hash_password("another-long-password")
        self.assertNotIn("$", h)  # docker compose の .env で $ は展開されるため使わない
        self.assertTrue(verify_hash("another-long-password", h))
        self.assertFalse(verify_hash("wrong", h))
        app = make_app(APP_PASSWORD="", APP_PASSWORD_HASH=h)
        c = app.test_client()
        self.assertEqual(login(c, "another-long-password").status_code, 302)

    def test_config_check(self):
        from sensei.config import Config
        self.assertTrue(Config(SECRET_KEY="short", APP_PASSWORD="", APP_PASSWORD_HASH="").check())
        self.assertEqual(Config(SECRET_KEY="x" * 40, APP_PASSWORD="long-enough-pass").check(), [])


@unittest.skipUnless(HAVE_FLASK, "Flask 未インストール")
class TestPages(unittest.TestCase):
    def setUp(self):
        self.app = make_app()
        self.c = self.app.test_client()
        login(self.c)

    def test_all_pages(self):
        for url in ["/", "/learn", "/learn/stage/0", "/learn/stage/7", "/learn/lesson/L0-4", "/library",
                    "/library/02-strategy.md", "/library/sources", "/glossary", "/glossary?q=IP", "/cheatsheet",
                    "/tools", "/practice", "/records", "/records/session/new", "/records/hand/new", "/coach",
                    "/coach/mental", "/settings", "/export", "/export.json", "/export.md"]:
            self.assertEqual(self.c.get(url).status_code, 200, url)

    def test_library_rejects_other_files(self):
        self.assertEqual(self.c.get("/library/..%2FCLAUDE.md").status_code, 404)
        self.assertEqual(self.c.get("/library/CLAUDE.md").status_code, 404)

    def test_every_lesson_renders_its_sections(self):
        from sensei import content
        for s in content.stages():
            for le in s["lessons"]:
                html = content.lesson_html(le)
                self.assertNotIn("見つかりません", html, le["id"])

    def test_tools(self):
        tok = csrf(self.c.get("/tools").text)
        r = self.c.post("/tools", data={"csrf": tok, "kind": "pot", "pot": "100", "bet": "50"})
        self.assertIn("25.0%", r.text)   # 50 / (150+50)
        self.assertIn("66.7%", r.text)   # MDF 100/150
        r = self.c.post("/tools", data={"csrf": tok, "kind": "equity", "hands": "AhAd KsKc", "board": "2c7d9h"})
        self.assertEqual(r.status_code, 200)
        r = self.c.post("/tools", data={"csrf": tok, "kind": "equity", "hands": "AhAd AhKc"})
        self.assertIn("入力を確認", r.text)


@unittest.skipUnless(HAVE_FLASK, "Flask 未インストール")
class TestPractice(unittest.TestCase):
    def setUp(self):
        self.app = make_app()
        self.c = self.app.test_client()
        login(self.c)

    def answer_batch(self, loc, correct=True, ms=2000):
        from sensei import practice
        with self.app.app_context():
            b = practice.load_batch(int(loc.rsplit("/", 1)[1]))
        tok = csrf(self.c.get(loc).text)
        data = {"csrf": tok}
        for i, q in enumerate(b["questions"]):
            data[f"a{i}"] = str(q["answer"] if correct else (q["answer"] + 1) % len(q["choices"]))
            data[f"t{i}"] = str(ms)
        self.c.post(loc, data=data)
        with self.app.app_context():
            return practice.load_batch(b["id"])

    def test_exam_pass_unlocks_requirement(self):
        tok = csrf(self.c.get("/practice/exam/s0-positions").text)
        loc = self.c.post("/practice/exam/s0-positions", data={"csrf": tok}).headers["Location"]
        b = self.answer_batch(loc)
        self.assertTrue(b["result"]["passed"])
        self.assertIn("合格", self.c.get("/learn/stage/0").text)

    def test_wrong_answers_go_to_review(self):
        loc = self.c.get("/practice/gen/pot_odds").headers["Location"]
        b = self.answer_batch(loc, correct=False)
        self.assertEqual(b["result"]["score"], 0)
        with self.app.app_context():
            from sensei import practice
            self.assertEqual(practice.due_count(), len(b["questions"]))
        loc = self.c.get("/practice/review").headers["Location"]
        b2 = self.answer_batch(loc, correct=True)
        self.assertEqual(b2["result"]["score"], b2["result"]["total"])
        with self.app.app_context():
            from sensei import practice
            self.assertEqual(practice.due_count(), 0)  # 正解したので翌日以降へ

    def test_locked_stage_exam(self):
        # Stage 2 は Stage 1 と並行なので、Stage 0 合格前は受けられない
        r = self.c.get("/practice/exam/s2-speed")
        self.assertIn("/learn/stage/2", r.headers["Location"])

    def test_speed_exam_counts_slow_as_fail(self):
        from sensei import practice
        with self.app.app_context():
            qs = practice.build_questions({"gen": "pot_odds"}, 10)
            bid = practice.create_batch("exam", "t", qs, req_id="s2-speed")
            b = practice.load_batch(bid)
            res = practice.grade(b, [q["answer"] for q in qs], [3000] * 5 + [15000] * 5)
        self.assertEqual(res["score"], 5)
        self.assertFalse(res["passed"])
        self.assertEqual(sum(x["slow"] for x in res["items"]), 5)

    def test_dontknow_is_wrong(self):
        from sensei import practice
        loc = self.c.get("/practice/gen/hand_name").headers["Location"]
        with self.app.app_context():
            b = practice.load_batch(int(loc.rsplit("/", 1)[1]))
        data = {"csrf": csrf(self.c.get(loc).text)}
        for i in range(len(b["questions"])):
            data[f"a{i}"] = "-1"
        self.c.post(loc, data=data)
        with self.app.app_context():
            b = practice.load_batch(b["id"])
        self.assertEqual(b["result"]["score"], 0)
        self.assertTrue(all(x["dontknow"] for x in b["result"]["items"]))

    def test_lesson_completion(self):
        loc = self.c.get("/practice/lesson/L0-2").headers["Location"]
        self.answer_batch(loc)
        self.assertIn("完了", self.c.get("/learn/lesson/L0-2").text)

    def test_records_feed_requirements(self):
        tok = csrf(self.c.get("/records/session/new").text)
        self.c.post("/records/session/new", data={"csrf": tok, "venue": "amusement", "itm": "1",
                                                  "opp_types": "ニット（極端に固い）", "tilt": "1"})
        tok = csrf(self.c.get("/records/hand/new").text)
        self.c.post("/records/hand/new", data={"csrf": tok, "title": "t", "self_review": "ポットオッズを計算した"})
        with self.app.app_context():
            from sensei import progress
            self.assertEqual(progress.record_value("domestic_itm"), 1)
            self.assertEqual(progress.record_value("sessions_with_opponents"), 1)
            self.assertEqual(progress.record_value("reviewed_hands"), 1)
        self.assertIn("ハンドレビュー", self.c.get("/export").text)


class TestDrills(unittest.TestCase):
    """自動生成ドリルの答えが教材の定義どおりか（Flask 不要: markdown だけ必要）。"""

    @classmethod
    def setUpClass(cls):
        try:
            from sensei import drills
        except ImportError as e:
            raise unittest.SkipTest(str(e))
        cls.d = drills

    def test_seat_order(self):
        lay = self.d.seat_layout(9, 0)
        self.assertEqual([lay[i] for i in range(9)], ["BTN", "SB", "BB", "UTG", "UTG+1", "UTG+2", "LJ", "HJ", "CO"])
        lay = self.d.seat_layout(8, 3)
        self.assertEqual(lay[3], "BTN")
        self.assertEqual(lay[4], "SB")
        self.assertEqual(lay[2], "CO")  # ボタンの右隣
        self.assertEqual(self.d.postflop_order(9)[0], "SB")
        self.assertEqual(self.d.postflop_order(9)[-1], "BTN")

    def test_generators_are_well_formed(self):
        rng = random.Random(7)
        for name in self.d.GENERATORS:
            n = 3 if name == "equity" else 30
            for q in self.d.generate(name, n, rng):
                self.assertTrue(0 <= q["answer"] < len(q["choices"]), name)
                self.assertEqual(len(set(q["choices"])), len(q["choices"]), (name, q["choices"]))
                self.assertTrue(q["source"] and q["source"][0]["url"].startswith("http"), name)
                self.assertTrue(q["explain"] and q["why"], name)

    def test_ip_answer(self):
        rng = random.Random(3)
        for _ in range(300):
            q = self.d.gen_positions(rng)
            if "IP" in q["q"] and "どちら" in q["q"]:
                a, b = re.findall(r"。(\S+) と (\S+) の2人", q["q"])[0]
                po = self.d.postflop_order(q["diagram"]["n"])
                expect = a if po.index(a) > po.index(b) else b
                self.assertEqual(q["choices"][q["answer"]], expect)

    def test_hand_compare_matches_evaluator(self):
        rng = random.Random(11)
        pm = self.d.pm
        for _ in range(40):
            q = self.d.gen_hand_compare(rng)
            a = [c["code"] for c in q["cards"]["A"]]
            b = [c["code"] for c in q["cards"]["B"]]
            board = [c["code"] for c in q["cards"]["board"]]
            va, vb = pm.best_hand(a + board), pm.best_hand(b + board)
            want = "A の勝ち" if va > vb else "B の勝ち" if vb > va else "引き分け（チョップ）"
            self.assertEqual(q["choices"][q["answer"]], want)

    def test_bb_defense_matches_curriculum(self):
        # 教材 02 1-7: 2.25BB オープンに BB は 20.8% のエクイティでコールが合う（BBA=1BB）
        pot, call = 2.25 + 0.5 + 1 + 1, 2.25 - 1
        self.assertAlmostEqual(self.d.pm.pot_odds(pot, call), 0.208, places=3)

    def test_min_raise(self):
        rng = random.Random(5)
        for _ in range(20):
            q = self.d.gen_min_raise(rng)
            bb, open_to = [int(x.replace(",", "")) for x in re.findall(r"[\d,]+", q["q"])[:2]]
            self.assertEqual(int(q["choices"][q["answer"]].replace(",", "")), open_to + (open_to - bb))


class TestContent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            from sensei import content
        except ImportError as e:
            raise unittest.SkipTest(str(e))
        cls.c = content

    def test_bank_is_valid(self):
        self.assertEqual(self.c.validate_bank(), [])
        self.assertGreater(len(self.c.question_bank()), 100)

    def test_every_stage_has_bank_questions_for_its_exams(self):
        for s in self.c.stages():
            for r in s["requirements"]:
                if r["type"] == "exam_bank":
                    pool = self.c.bank_select(r["bank"].get("stage"), r["bank"].get("tags"))
                    self.assertGreaterEqual(len(pool), r["n"], r["id"])

    def test_extract_section(self):
        text = "# t\n## 1. a\n### 1.1 x\nbody\n### 1.2 y\nmore\n## 2. b\n"
        self.assertEqual(self.c.extract_section(text, "### 1.1"), "### 1.1 x\nbody")
        self.assertIn("### 1.2 y", self.c.extract_section(text, "## 1."))
        self.assertNotIn("## 2.", self.c.extract_section(text, "## 1."))

    def test_glossary(self):
        g = self.c.glossary()
        self.assertTrue(any(x["term"].startswith("3ベット") for x in g))


if __name__ == "__main__":
    unittest.main()


@unittest.skipUnless(HAVE_FLASK, "Flask 未インストール")
class TestCoach(unittest.TestCase):
    """AIコーチの応答処理（API は呼ばずに偽の応答で確認）。"""

    def test_ask_parses_text_and_citations(self):
        from types import SimpleNamespace as NS
        from unittest import mock

        from sensei import coach
        calls = []

        class FakeMessages:
            def create(self, **kw):
                calls.append(kw)
                if len(calls) == 1:
                    return NS(stop_reason="pause_turn", content=[NS(type="server_tool_use")])
                cite = NS(url="https://blog.gtowizard.com/mdf-alpha/", title="MDF & Alpha")
                return NS(stop_reason="end_turn", content=[NS(type="text", text="結論: 降りすぎに注意。", citations=[cite])])

        fake = NS(beta=NS(messages=FakeMessages()))
        app = make_app(ANTHROPIC_API_KEY="sk-test")
        with app.app_context(), mock.patch.object(coach, "_client", return_value=fake):
            answer, cites, err = coach.ask("MDFとは？", "- Stage 0")
        self.assertIsNone(err)
        self.assertIn("降りすぎ", answer)
        self.assertEqual(cites[0]["url"], "https://blog.gtowizard.com/mdf-alpha/")
        self.assertEqual(len(calls), 2)  # pause_turn から再開した
        self.assertEqual(calls[0]["fallbacks"], "default")
        self.assertEqual(calls[0]["tools"][0]["type"], "web_search_20260209")
        self.assertEqual(calls[1]["messages"][1]["role"], "assistant")
