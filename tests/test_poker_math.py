import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import poker_math as pm  # noqa: E402


class FormulaTests(unittest.TestCase):
    def test_pot_odds(self):
        # ポット100に相手が50ベット → ポット150、コール50 → 50/200 = 25%
        self.assertAlmostEqual(pm.pot_odds(150, 50), 0.25)

    def test_mdf_and_bluff(self):
        self.assertAlmostEqual(pm.mdf(100, 50), 2 / 3)
        self.assertAlmostEqual(pm.bluff_breakeven(100, 100), 0.5)

    def test_outs(self):
        # フラッシュドロー9アウツ、ターン+リバー: 1 - C(38,2)/C(47,2) = 0.3497
        self.assertAlmostEqual(pm.outs_probability(9, 2), 1 - 703 / 1081, places=6)
        self.assertAlmostEqual(pm.outs_probability(9, 1), 9 / 47)
        self.assertAlmostEqual(pm.outs_probability(9, 1, unseen=46), 9 / 46)


class HandTests(unittest.TestCase):
    def rank(self, s):
        return pm.best_hand(pm.parse_cards(s))[0]

    def test_categories(self):
        self.assertEqual(self.rank("AhKhQhJhTh2c3d"), 8)
        self.assertEqual(self.rank("Ah2c3d4s5h9c9d"), 4)  # ホイール
        self.assertEqual(self.rank("AhAdAcKhKd2c3d"), 6)
        self.assertEqual(self.rank("2h7h9hJhKh2c3d"), 5)

    def test_wheel_loses_to_six_high(self):
        wheel = pm.best_hand(pm.parse_cards("Ah2c3d4s5h"))
        six = pm.best_hand(pm.parse_cards("2c3d4s5h6c"))
        self.assertLess(wheel, six)

    def test_kicker(self):
        a = pm.best_hand(pm.parse_cards("AhAdKc9s7h"))
        b = pm.best_hand(pm.parse_cards("AsAcQc9d7d"))
        self.assertGreater(a, b)


class EquityTests(unittest.TestCase):
    def test_aa_vs_kk_preflop(self):
        # 一般に知られる値は AA 約82% vs KK 約18%
        eqs, _ = pm.equity([pm.parse_cards("AhAd"), pm.parse_cards("KsKc")], trials=20000, seed=1)
        self.assertAlmostEqual(eqs[0], 0.82, delta=0.015)

    def test_exact_river(self):
        eqs, n = pm.equity([pm.parse_cards("AhKh"), pm.parse_cards("QsQd")],
                           pm.parse_cards("2c7dJh9s"))
        self.assertEqual(n, 44)
        # AhKhが逆転できるのは残りのA・K各3枚の計6枚だけ → 6/44
        self.assertAlmostEqual(eqs[0], 6 / 44)


if __name__ == "__main__":
    unittest.main()
