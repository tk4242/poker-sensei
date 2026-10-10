"""トレーニング（バトル形式の反復練習）・苦手克服クエスト・同調の記録のテスト。Flask がなければスキップ。"""
import json
import re
import sqlite3
import tempfile
import unittest
from pathlib import Path

from test_app import HAVE_FLASK, csrf, login, make_app


@unittest.skipUnless(HAVE_FLASK, "Flask 未インストール")
class TestTrain(unittest.TestCase):
    def setUp(self):
        self.app = make_app()
        self.c = self.app.test_client()
        login(self.c)

    def db(self):
        con = sqlite3.connect(self.app.config["DB_PATH"])
        con.row_factory = sqlite3.Row
        return con

    def open_question(self, topic="ev"):
        r = self.c.get(f"/train/{topic}")
        self.assertEqual(r.status_code, 200, topic)
        qid = int(re.search(r'action="/train/a/(\d+)"', r.text).group(1))
        item = json.loads(self.db().execute("SELECT question FROM train_q WHERE id=?", (qid,)).fetchone()[0])
        return r, qid, item

    def answer(self, qid, a, ms="1000"):
        with self.c.session_transaction() as s:
            tok = s["csrf"]
        return self.c.post(f"/train/a/{qid}", data={"csrf": tok, "a": str(a), "t": ms})

    def test_pages(self):
        for url in ["/train", "/quest", "/coach/mental", "/records/session/new", "/"]:
            self.assertEqual(self.c.get(url).status_code, 200, url)
        self.assertIn("数字カード", self.c.get("/coach/mental").text)
        self.assertIn('name="conformed"', self.c.get("/records/session/new").text)
        self.assertIn("苦手克服クエスト", self.c.get("/").text)

    def test_every_topic_has_questions(self):
        from sensei import train
        for topic in train.TOPICS:
            if topic == "news":  # 承認済みの知識カードがあるときだけ出る（test_app_knowledge で確認）
                continue
            r, qid, item = self.open_question(topic)
            self.assertIn(item["q"][:10], r.text.replace("&#39;", "'").replace("&amp;", "&").replace("&lt;", "<"))

    def test_correct_answer_damages_monster_and_records(self):
        r, qid, item = self.open_question("ev")
        self.assertIn("あらわれた", r.text)
        res = self.answer(qid, item["answer"], ms="900")
        self.assertEqual(res.headers["Location"], f"/train/r/{qid}")
        page = self.c.get(f"/train/r/{qid}").text
        self.assertIn("せいかい", page)
        self.assertIn("かいしん", page)  # 5秒以内の正解
        self.assertIn(item["why"][:10], page)
        with self.c.session_transaction() as s:
            self.assertEqual(s["battle"]["mhp"], 3)
            self.assertEqual(s["battle"]["c"], 1)
        row = self.db().execute("SELECT mode, correct FROM attempts").fetchall()
        self.assertEqual([tuple(x) for x in row], [("train", 1)])

    def test_double_submit_counts_once(self):
        _, qid, item = self.open_question("bet")
        self.answer(qid, item["answer"])
        self.answer(qid, (item["answer"] + 1) % 4)
        self.assertEqual(self.db().execute("SELECT COUNT(*) FROM attempts").fetchone()[0], 1)

    def test_wrong_answers_end_battle_and_go_to_review(self):
        for _ in range(5):
            _, qid, item = self.open_question("call")
            self.answer(qid, (item["answer"] + 1) % 4, ms="20000")
        page = self.c.get(f"/train/r/{qid}").text
        self.assertIn("ちからつきた", page)
        self.assertGreater(self.db().execute("SELECT COUNT(*) FROM srs").fetchone()[0], 0)
        end = self.c.post("/train/end", data={"csrf": csrf(page)})
        self.assertIn("0 / 5", end.text)

    def test_dont_know(self):
        _, qid, _ = self.open_question("outs")
        self.answer(qid, -1)
        self.assertIn("わからない", self.c.get(f"/train/r/{qid}").text)
        row = self.db().execute("SELECT correct, dontknow FROM attempts").fetchone()
        self.assertEqual(tuple(row), (0, 1))

    def test_unknown_topic_404(self):
        self.assertEqual(self.c.get("/train/nope").status_code, 404)


@unittest.skipUnless(HAVE_FLASK, "Flask 未インストール")
class TestLevelsAndQuest(unittest.TestCase):
    def test_level_curve(self):
        from sensei.train import level_of
        self.assertEqual(level_of(0), (1, 0, 50))
        self.assertEqual(level_of(49), (1, 49, 50))
        self.assertEqual(level_of(50), (2, 0, 100))
        self.assertEqual(level_of(149), (2, 99, 100))
        self.assertEqual(level_of(150), (3, 0, 150))

    def test_quest_exam_and_records(self):
        app = make_app()
        c = app.test_client()
        login(c)
        page = c.get("/practice/exam/q-w2")
        self.assertEqual(page.status_code, 200)
        self.assertIn("10 秒以内", page.text)
        r = c.post("/practice/exam/q-w2", data={"csrf": csrf(page.text)})
        self.assertIn("/practice/b/", r.headers["Location"])
        # 同調の記録 → クエストの「毎回」の課題が数えられる。3回以上ならメンタルへ
        tok = csrf(c.get("/records/session/new").text)
        r = c.post("/records/session/new", data={"csrf": tok, "venue": "amusement", "conformed": "4"})
        self.assertIn("/coach/mental", r.headers["Location"])
        with app.app_context():
            from sensei import progress
            self.assertEqual(progress.record_value("sessions_with_conform"), 1)
            qo = progress.quest_overview()
            self.assertEqual(qo["next"]["week"], 1)
            self.assertEqual(progress.conform_trend()[0]["conformed"], 4)
        self.assertIn("合わせた", c.get("/records").text)

    def test_stage2_has_05_lessons(self):
        from sensei import content
        s2 = content.stage(2)
        self.assertIn("L2-6", [le["id"] for le in s2["lessons"]])
        self.assertIn("s2-decision", [r["id"] for r in s2["requirements"]])
        _, le = content.lesson("L6-6")
        self.assertTrue(content.lesson_html(le).count("<h") > 0)
        self.assertNotIn("見つかりません", content.lesson_html(le))
        for w in content.quest()["weeks"]:
            self.assertIsNotNone(content.requirement(w["req"]["id"])[1])
            _, le = content.lesson(w["lesson"])
            self.assertIsNotNone(le)


@unittest.skipUnless(HAVE_FLASK, "Flask 未インストール")
class TestMigration(unittest.TestCase):
    def test_old_db_gets_new_column(self):
        from sensei import db
        path = Path(tempfile.mkdtemp()) / "old.db"
        con = sqlite3.connect(path)
        con.execute("CREATE TABLE play_sessions(id INTEGER PRIMARY KEY, date TEXT)")
        con.commit()
        con.close()
        db.init_db(path)
        cols = {r[1] for r in sqlite3.connect(path).execute("PRAGMA table_info(play_sessions)")}
        self.assertIn("conformed", cols)
        db.init_db(path)  # 2回目も壊れない


@unittest.skipUnless(HAVE_FLASK, "Flask 未インストール")
class TestAssets(unittest.TestCase):
    def test_static_assets(self):
        app = make_app()
        c = app.test_client()
        for name in ["fonts/DotGothic16.woff2", "fonts/OFL-DotGothic16.txt", "bg.svg", "field.svg",
                     "sprites/hero.svg", "sprites/sensei.svg"]:
            r = c.get(f"/static/{name}")
            self.assertEqual(r.status_code, 200, name)
            r.close()
        from sensei import train
        root = Path(app.static_folder) / "sprites"
        for t in train.TOPICS.values():
            self.assertTrue((root / f"{t['sprite']}.svg").exists(), t["sprite"])

    def test_no_inline_styles(self):
        """CSP（style-src 'self'）で崩れないよう、テンプレートに style 属性を書かない。"""
        root = Path(make_app().template_folder)
        for p in root.glob("*.html"):
            self.assertNotIn('style="', p.read_text(encoding="utf-8"), p.name)
