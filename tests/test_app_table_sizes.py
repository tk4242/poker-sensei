"""Every supported table size remains valid without inventing multiplayer GTO data."""
import random
import unittest
from test_app import HAVE_FLASK, make_app, login, csrf
if HAVE_FLASK:
    from sensei import arena


@unittest.skipUnless(HAVE_FLASK, 'Flask unavailable')
class TableSizesTests(unittest.TestCase):
    def test_all_sizes_have_correct_action_order_and_seat_count(self):
        expected = {
            2: ['BTN/SB', 'BB'], 3: ['BTN', 'SB', 'BB'],
            4: ['CO', 'BTN', 'SB', 'BB'], 5: ['HJ', 'CO', 'BTN', 'SB', 'BB'],
            6: ['UTG', 'HJ', 'CO', 'BTN', 'SB', 'BB'],
            7: ['UTG', 'LJ', 'HJ', 'CO', 'BTN', 'SB', 'BB'],
            8: ['UTG', 'UTG+1', 'LJ', 'HJ', 'CO', 'BTN', 'SB', 'BB'],
        }
        self.assertEqual(arena.POSITIONS, expected)
        for n, pre in expected.items():
            post = ['BB', 'BTN/SB'] if n == 2 else ['SB', 'BB'] + pre[:-2]
            self.assertEqual(arena.post_order(n), post)
            for mode in ('positions', 'flop'):
                cfg = arena.config_from(dict(mode=mode, players=n, position='random'))
                for seed in range(20):
                    item = arena.question(cfg, random.Random(seed))
                    self.assertEqual(len(item['seats']), n)
                    self.assertEqual(len({seat['pos'] for seat in item['seats']}), n)
                    self.assertEqual(sum(seat['button'] for seat in item['seats']), 1)
                    self.assertIn(item['hero'], pre)
                    self.assertTrue(0 <= item['answer'] < len(item['choices']))
                    if mode == 'positions':
                        order = pre if item['street'] == 'プリフロップ' else post
                        self.assertIn(' → '.join(order), item['explain'])

    def test_non_hu_range_rejected_and_all_other_sizes_start(self):
        client = make_app().test_client()
        login(client)
        for n in range(2, 9):
            for mode in ('positions', 'flop'):
                response = client.post('/table/start', data={
                    'csrf': csrf(client.get('/table').text), 'players': n,
                    'mode': mode, 'position': 'random', 'stack': '8', 'format': 'mtt'})
                self.assertEqual(response.status_code, 302)
                self.assertIn('/table/run/', response.location)
                self.assertEqual(client.get(response.location).status_code, 200)
            if n > 2:
                with self.assertRaisesRegex(ValueError, '未収録'):
                    arena.config_from(dict(mode='range', players=n, position='random'))
