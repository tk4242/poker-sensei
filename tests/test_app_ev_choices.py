"""EV出題の全入力組み合わせで重複選択肢・500エラーを防ぐ。"""
import itertools
import unittest
from unittest.mock import Mock
from test_app import HAVE_FLASK


@unittest.skipUnless(HAVE_FLASK, "Flask 未インストール")
class EvChoicesTests(unittest.TestCase):
    def test_all_192_input_combinations(self):
        from sensei import drills
        for p, win, lose in itertools.product(
                [0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.6],
                [100, 150, 200, 300, 400, 500], [50, 100, 150, 200]):
            with self.subTest(p=p, win=win, lose=lose):
                rng = Mock()
                rng.choice.side_effect = [p, win, lose]
                item = drills.gen_ev(rng)
                self.assertEqual(len(item["choices"]), 4)
                self.assertEqual(len(set(item["choices"])), 4)
                self.assertEqual(item["choices"][item["answer"]], f"{p * win - (1 - p) * lose:+.0f}")
