"""卓の誤答をホームから再開し、最新の回答で解消する回帰検証。"""
import unittest
from test_app import make_app, login, csrf, HAVE_FLASK
if HAVE_FLASK:
    from sensei import arena, practice
    from sensei.db import q


@unittest.skipUnless(HAVE_FLASK, 'Flask 未インストール')
class ArenaReviewTests(unittest.TestCase):
    def setUp(self):
        self.app = make_app()
        self.c = self.app.test_client()
        login(self.c)
        self.cfg = dict(mode='range', format='mtt', players=2, stack=8, position='BB')

    def test_home_review_then_existing_retry_clears_queue(self):
        with self.app.app_context():
            rid = arena.create_run(self.cfg)
            item = arena.load_run(rid)['questions'][0]
            arena.answer(rid, 0, (item['answer'] + 1) % len(item['choices']))
            self.assertEqual(arena.review_count(), 1)
            self.assertEqual(practice.due_count(), 0)
        home = self.c.get('/')
        self.assertIn('卓で間違えた問題が 1 問', home.text)
        result = self.c.post('/table/review', data={'csrf': csrf(home.text)})
        second_id = int(result.location.split('/')[-1])
        with self.app.app_context():
            second = arena.load_run(second_id)
            self.assertEqual(second['questions'], [item])
            arena.answer(second_id, 0, (item['answer'] + 1) % len(item['choices']))
            self.assertEqual(arena.review_count(), 1)
        retry = self.c.post(f'/table/run/{second_id}/retry', data={'csrf': csrf(home.text)})
        third_id = int(retry.location.split('/')[-1])
        with self.app.app_context():
            arena.answer(third_id, 0, item['answer'])
            self.assertEqual(arena.review_count(), 0)
            # Reposting an already answered old question cannot resurrect an error.
            arena.answer(rid, 0, (item['answer'] + 1) % len(item['choices']))
            self.assertEqual(arena.review_count(), 0)
        self.assertNotIn('卓で間違えた問題が', self.c.get('/').text)

    def test_latest_answer_order_not_run_creation_order_and_formats(self):
        with self.app.app_context():
            original = arena.create_run(self.cfg)
            item = arena.load_run(original)['questions'][0]
            newer = arena.create_run(self.cfg, [item])
            arena.answer(newer, 0, item['answer'])
            # An older run answered later must count as the latest outcome.
            arena.answer(original, 0, (item['answer'] + 1) % len(item['choices']))
            cash = arena.create_run({**self.cfg, 'format': 'cash'})
            cash_item = arena.load_run(cash)['questions'][0]
            arena.answer(cash, 0, (cash_item['answer'] + 1) % len(cash_item['choices']))
            self.assertEqual(arena.review_count('mtt'), 1)
            self.assertEqual(arena.review_count('cash'), 1)
            self.assertEqual(arena.review_count(), 2)
        tok = csrf(self.c.get('/table').text)
        response = self.c.post('/table/review', data={'csrf': tok, 'format': 'cash'})
        with self.app.app_context():
            reviewed = arena.load_run(int(response.location.split('/')[-1]))
            self.assertEqual(reviewed['config']['format'], 'cash')
            self.assertEqual(reviewed['questions'], [cash_item])
        self.assertEqual(self.c.post('/table/review', data={'csrf': tok, 'format': 'invalid'}).status_code, 400)

    def test_recent_run_survives_thirty_other_format_runs(self):
        with self.app.app_context():
            rid = arena.create_run(self.cfg)
            for _ in range(30):
                arena.create_run({**self.cfg, 'format': 'cash'})
            self.assertEqual(arena.recent_runs('mtt')[0]['id'], rid)
            self.assertEqual(len(arena.recent_runs('cash')), 5)

    def test_mixed_frequencies_keep_mixed_answer(self):
        self.assertEqual(arena.category(0), 0)
        self.assertEqual(arena.category(1), 1)
        for frequency in (0.00001, 0.1, 0.5, 0.9, 0.99999):
            self.assertEqual(arena.category(frequency), 2)

    def test_empty_queue_does_not_create_run(self):
        token = csrf(self.c.get('/table').text)
        response = self.c.post('/table/review', data={'csrf': token}, follow_redirects=True)
        self.assertIn('卓の復習待ちはありません', response.text)
        with self.app.app_context():
            self.assertEqual(q('SELECT COUNT(*) n FROM arena_runs', one=True)['n'], 0)
