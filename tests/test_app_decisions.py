"""Situation actions: table rendering, source scope, server grading and review."""
import random
import unittest
from test_app import HAVE_FLASK, make_app, login, csrf
if HAVE_FLASK:
    from sensei import arena, decision_spots
    from sensei.db import q


class PickSpot:
    def __init__(self, spot_id):
        self.spot_id = spot_id

    def choice(self, values):
        if isinstance(values[0], dict):
            return next(v for v in values if v['id'] == self.spot_id)
        return values[0]


@unittest.skipUnless(HAVE_FLASK, 'Flask unavailable')
class DecisionTests(unittest.TestCase):
    def setUp(self):
        self.app = make_app()
        self.client = self.app.test_client()
        login(self.client)

    def test_fixed_conditions_and_mode_entry(self):
        cfg = arena.config_from(dict(mode='decisions', players='8', position='anything', stack='anything'))
        self.assertEqual(cfg['position'], 'random')
        self.assertEqual(cfg['stack'], 8)
        self.assertIn('mode=decisions', self.client.get('/').text)
        page = self.client.get('/table?mode=decisions').text
        self.assertIn('value="decisions" checked', page)
        self.assertIn('出典付きの固定局面', page)
        self.assertIn('value="positions" checked', self.client.get('/table?mode=unknown').text)

    def test_all_spots_all_table_sizes_render_without_duplicate_cards(self):
        for spot in decision_spots.data()['spots']:
            self.assertTrue(spot['sources'], spot['id'])
            for fmt in spot['formats']:
                for n in ([spot['players']] if 'players' in spot else range(2, 9)):
                    cfg = arena.config_from(dict(mode='decisions', players=n, format=fmt))
                    item = arena.question(cfg, PickSpot(spot['id']))
                    self.assertEqual(item['mode'], 'decisions')
                    self.assertEqual({s['pos']: s['bet'] for s in item['seats'] if s['bet']},
                                     {p: b for p, b in item['investments'].items() if b})
                    if n == 2:
                        self.assertNotIn('SB', item['investments'])
                        self.assertNotIn('SB フォールド', item['history'])
                    self.assertEqual(len(item['seats']), n)
                    self.assertEqual(sum(s['hero'] for s in item['seats']), 1)
                    self.assertEqual(sum(s['button'] for s in item['seats']), 1)
                    self.assertTrue(all(s['stack'] is None or s['stack'] >= 0 for s in item['seats']))
                    cards = item['cards'] + item['board'] + item.get('villain', [])
                    self.assertEqual(len(cards), len(set(cards)), spot['id'])
                    self.assertTrue(0 <= item['answer'] < len(item['choices']))
                    with self.app.app_context():
                        run_id = arena.create_run(cfg, [item])
                    page = self.client.get(f'/table/run/{run_id}')
                    self.assertEqual(page.status_code, 200)
                    self.assertIn(item['label'], page.text)
                    self.assertNotIn('相手の手札が既知のチップEV計算。MTT', page.text)

    def test_five_questions_grade_once_and_wrong_answers_are_reviewable(self):
        cfg = arena.config_from(dict(mode='decisions', players=8, format='cash'))
        with self.app.app_context():
            run_id = arena.create_run(cfg)
            run = arena.load_run(run_id)
        self.assertEqual(len(run['questions']), 5)
        self.assertEqual(len({x['key'] for x in run['questions']}), 5)
        token = csrf(self.client.get(f'/table/run/{run_id}').text)
        for i, item in enumerate(run['questions']):
            chosen = (item['answer'] + 1) % len(item['choices']) if i == 0 else item['answer']
            for _ in range(2):
                response = self.client.post(f'/table/run/{run_id}/answer', data={
                    'csrf': token, 'index': i, 'choice': chosen})
                self.assertEqual(response.status_code, 302)
        with self.app.app_context():
            attempts = q('SELECT tag,correct FROM attempts')
            self.assertEqual(len(attempts), 5)
            self.assertEqual({r['tag'] for r in attempts}, {'strategy'})
            self.assertEqual(sum(r['correct'] for r in attempts), 4)
            self.assertEqual(arena.review_count('cash'), 1)
            self.assertEqual(arena.review_count('mtt'), 0)
        response = self.client.post(f'/table/run/{run_id}/retry', data={'csrf': token})
        with self.app.app_context():
            retry = arena.load_run(int(response.location.split('/')[-1]))
            self.assertEqual(len(retry['questions']), 1)
            self.assertEqual(retry['questions'][0]['key'], run['questions'][0]['key'])
