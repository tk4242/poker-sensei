"""Count pending preflop opponents, never confuse them with table size."""
import random
import unittest
from test_app import HAVE_FLASK
if HAVE_FLASK:
    from sensei import arena


@unittest.skipUnless(HAVE_FLASK, 'Flask unavailable')
class BehindTests(unittest.TestCase):
    def test_every_seat_and_seed_preserves_valid_action_context(self):
        coverage = set()
        for n, positions in arena.POSITIONS.items():
            for hero in positions:
                cfg = arena.config_from(dict(mode='positions', players=n, position=hero))
                for seed in range(120):
                    item = arena.question(cfg, random.Random(seed))
                    self.assertIn('行動順：', item['explain'])
                    if item['task'] != 'behind':
                        continue
                    coverage.add((n, hero))
                    self.assertNotEqual(hero, 'BB')
                    self.assertEqual(item['street'], 'プリフロップ')
                    self.assertEqual(item['board'], [])
                    index = positions.index(hero)
                    expected = len(positions[index+1:])
                    self.assertGreater(expected, 0)
                    self.assertEqual(item['choices'], [f'{i}人' for i in range(n)])
                    self.assertEqual(item['choices'][item['answer']], f'{expected}人')
                    folded = {s['pos'] for s in item['seats'] if s['folded']}
                    self.assertEqual(folded, set(positions[:index]))
                    self.assertNotIn(hero, folded)
                    self.assertIn(' → '.join(positions), item['explain'])
        self.assertEqual(coverage, {(n, p) for n, ps in arena.POSITIONS.items() for p in ps if p != 'BB'})

    def test_button_two_behind_is_not_heads_up(self):
        for n in range(2, 9):
            hero = 'BTN/SB' if n == 2 else 'BTN'
            cfg = arena.config_from(dict(mode='positions', players=n, position=hero))
            items = [arena.question(cfg, random.Random(seed)) for seed in range(120)]
            behind = next(item for item in items if item['task'] == 'behind')
            self.assertEqual(behind['choices'][behind['answer']], '1人' if n == 2 else '2人')
            self.assertIn('HUとは違います', behind['hint'])
