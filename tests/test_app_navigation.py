"""クイズのブラウザ操作をNodeで回帰検証（外部npmパッケージ不要）。"""
import shutil
import subprocess
import unittest
from pathlib import Path


class TestQuizNavigation(unittest.TestCase):
    @unittest.skipUnless(shutil.which('node'), 'Node.js が必要です')
    def test_navigation(self):
        root = Path(__file__).resolve().parent.parent
        result = subprocess.run(
            ['node', '--test', 'tests/test_quiz_navigation.js'], cwd=root,
            text=True, capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
