"""基礎コースの計算・5問チェック・保存・入力境界。"""
import random
import unittest
from test_app import HAVE_FLASK, csrf, login, make_app


@unittest.skipUnless(HAVE_FLASK, 'Flask 未インストール')
class TestFoundations(unittest.TestCase):
    def setUp(self):
        self.app = make_app()
        self.c = self.app.test_client()
        login(self.c)

    def test_calculation_identities(self):
        from sensei import foundations as f
        for size in (25, 50, 75, 100, 150):
            for equity in (10, 20, 25, 30, 40, 60):
                s = f.scenario(size, equity)
                self.assertAlmostEqual(s['required'], 100 * size / (100 + 2 * size))
                # Independent expected final pot share minus the call cost.
                self.assertAlmostEqual(s['ev'], equity / 100 * s['total'] - size)
        self.assertEqual(f.scenario(50, 25)['ev'], 0)
        self.assertEqual(f.scenario(50, 40)['ev'], 30)
        self.assertEqual(f.scenario(100, 20)['ev'], -40)

    def test_all_lessons_and_question_variants(self):
        from sensei import foundations as f
        for topic in f.LESSONS:
            page = self.c.get('/learn/basics/' + topic)
            self.assertEqual(page.status_code, 200)
            self.assertIn('5問練習', page.text)
            self.assertIn('gtowizard.com', page.text)
            for seed in range(30):
                items = f.questions(topic, random.Random(seed))
                self.assertEqual(len(items), 5)
                self.assertEqual(len({i['key'] for i in items}), 5)
                for item in items:
                    self.assertEqual(len(set(item['choices'])), 4)
                    self.assertIn(item['answer'], range(4))
                    self.assertTrue(item['source'])
                    self.assertEqual(item['foundation'], topic)
                    self.assertNotEqual(item['label'], 'GTO')

    def test_check_grade_resume_and_review(self):
        from sensei import foundations as f, practice
        for topic in f.LESSONS:
            page = self.c.get('/learn/basics/' + topic)
            start = self.c.post('/learn/basics/' + topic + '/practice', data={'csrf': csrf(page.text)})
            self.assertEqual(start.status_code, 302)
            url = start.headers['Location']
            with self.app.app_context():
                b = practice.load_batch(int(url.rsplit('/', 1)[1]))
            data = {f'a{i}': str(q['answer']) for i, q in enumerate(b['questions'])}
            data['a0'] = '-1'
            data['csrf'] = csrf(self.c.get(url).text)
            result = self.c.post(url, data=data, follow_redirects=True)
            self.assertIn('4 / 5', result.text)
            self.assertIn('説明と計算を見直す', result.text)
            # Resubmitting does not create duplicate attempts.
            self.c.post(url, data=data)
            with self.app.app_context():
                stats = f.overview()
                own = next(x for x in stats if x['topic'] == topic)
                self.assertTrue(own['completed'])
                self.assertEqual(own['score'], 4)
                self.assertGreater(practice.due_count(), 0)
        other = self.app.test_client()
        login(other)
        self.assertIn('4テーマの直近チェックで4/5以上', other.get('/learn/basics').text)
        from sensei.db import q
        with self.app.app_context():
            self.assertEqual(q('SELECT COUNT(*) n FROM attempts', one=True)['n'], 20)

    def test_input_and_auth_boundaries(self):
        for args in ('size=0', 'size=nan', 'size=999', 'equity=-1', 'equity=33', 'equity=inf'):
            self.assertEqual(self.c.get('/learn/basics/ev?' + args).status_code, 400)
        self.assertEqual(self.c.get('/learn/basics/nope').status_code, 404)
        self.assertEqual(self.c.post('/learn/basics/ev/practice').status_code, 400)
        self.assertEqual(self.app.test_client().get('/learn/basics').status_code, 302)
        self.assertIn('+30', self.c.get('/learn/basics/ev?size=50&equity=40').text)

    def test_entry_and_csp(self):
        for path in ('/', '/learn'):
            self.assertIn('/learn/basics', self.c.get(path).text)
        page = self.c.get('/learn/basics/bet')
        self.assertNotIn('style="', page.text)
        self.assertIn("style-src 'self'", page.headers['Content-Security-Policy'])
