import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS))
import collab  # noqa: E402

OWNERS = {"learner/": "claude", "learner/special.md": "codex", "CLAUDE.md": "claude"}


class OwnerTests(unittest.TestCase):
    def test_owner_of(self):
        self.assertEqual(collab.owner_of("learner/growth.md", OWNERS), "claude")
        self.assertEqual(collab.owner_of("learner/special.md", OWNERS), "codex")  # 具体的な方を優先
        self.assertEqual(collab.owner_of("CLAUDE.md", OWNERS), "claude")
        self.assertIsNone(collab.owner_of("curriculum/01-terms.md", OWNERS))  # 共有
        self.assertIsNone(collab.owner_of("CLAUDE.md.bak", OWNERS))  # 完全一致のみ

    def test_violations(self):
        files = ["learner/growth.md", "curriculum/a.md", "CLAUDE.md"]
        self.assertEqual(collab.violations(files, "claude", OWNERS), [])
        self.assertEqual(
            collab.violations(files, "codex", OWNERS),
            [("learner/growth.md", "claude"), ("CLAUDE.md", "claude")],
        )


def run(*cmd, cwd):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return r


class SyncTests(unittest.TestCase):
    """本物のgitで、2つの作業コピーが同じリモートへ安全にpushできることを確認する。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        t = Path(self.tmp.name)
        self.remote = t / "remote.git"
        run("git", "init", "-q", "--bare", "-b", "main", str(self.remote), cwd=t)
        seed = t / "seed"
        run("git", "clone", "-q", str(self.remote), str(seed), cwd=t)
        self.config(seed, "seed")
        (seed / ".collab").mkdir()
        (seed / ".collab" / "owners.json").write_text(json.dumps({"owners": {"learner/": "claude"}}))
        (seed / "tools").mkdir()
        (seed / "tools" / "collab.py").write_text((TOOLS / "collab.py").read_text())
        (seed / "tests").mkdir()
        (seed / "tests" / "test_ok.py").write_text("import unittest\nclass T(unittest.TestCase):\n    def test(self): pass\n")
        run("git", "add", "-A", cwd=seed)
        run("git", "commit", "-qm", "init", cwd=seed)
        run("git", "push", "-q", "origin", "HEAD:main", cwd=seed)
        self.a = t / "claude"
        self.b = t / "codex"
        for d in (self.a, self.b):
            run("git", "clone", "-q", str(self.remote), str(d), cwd=t)
            self.config(d, d.name)

    def tearDown(self):
        self.tmp.cleanup()

    def config(self, d, name):
        run("git", "config", "user.name", name, cwd=d)
        run("git", "config", "user.email", f"{name}@example.com", cwd=d)

    def commit(self, d, path, text, msg):
        p = d / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        run("git", "add", "-A", cwd=d)
        run("git", "commit", "-qm", msg, cwd=d)

    def sync(self, d, agent, *extra):
        return run(sys.executable, "tools/collab.py", "sync", "--agent", agent, *extra, cwd=d)

    def test_two_agents_interleave_without_force(self):
        self.commit(self.a, "learner/growth.md", "a", "claude: log")
        self.commit(self.b, "curriculum/new.md", "b", "codex: lesson")
        ra = self.sync(self.a, "claude")
        self.assertEqual(ra.returncode, 0, ra.stdout + ra.stderr)
        rb = self.sync(self.b, "codex")  # 手元が遅れているので rebase してから push される
        self.assertEqual(rb.returncode, 0, rb.stdout + rb.stderr)
        log = run("git", "log", "--oneline", "--format=%s", cwd=self.remote).stdout.split("\n")
        self.assertEqual(log[:2], ["codex: lesson", "claude: log"])  # 直線の履歴、どちらも残る

    def test_other_agents_files_are_refused(self):
        self.commit(self.b, "learner/growth.md", "x", "codex: touches claude area")
        r = self.sync(self.b, "codex")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("learner/growth.md", r.stdout)
        remote_files = run("git", "ls-tree", "-r", "--name-only", "main", cwd=self.remote).stdout
        self.assertNotIn("learner/growth.md", remote_files)

    def test_allow_other_overrides(self):
        self.commit(self.b, "learner/growth.md", "x", "codex: sanctioned")
        r = self.sync(self.b, "codex", "--allow-other")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_conflict_aborts_and_keeps_local(self):
        self.commit(self.a, "curriculum/same.md", "from claude", "claude edit")
        self.commit(self.b, "curriculum/same.md", "from codex", "codex edit")
        self.assertEqual(self.sync(self.a, "claude").returncode, 0)
        r = self.sync(self.b, "codex")
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertEqual((self.b / "curriculum" / "same.md").read_text(), "from codex")  # 手元は無傷
        self.assertEqual(run("git", "status", "--porcelain", cwd=self.b).stdout.strip(), "")

    def test_dirty_tree_refused(self):
        (self.a / "dirty.txt").write_text("x")
        run("git", "add", "-A", cwd=self.a)
        r = self.sync(self.a, "claude")
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
