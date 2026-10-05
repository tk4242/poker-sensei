#!/usr/bin/env python3
"""Claude と Codex が同じリポジトリを触るときの衝突防止ツール（標準ライブラリのみ）。

使い方:
  python3 tools/collab.py check --agent codex            # 未pushの変更が他担当のパスを触っていないか確認
  python3 tools/collab.py sync  --agent claude           # 最新を取り込み→確認→テスト→push（force pushはしない。claudeはmain、codexはcodex/workへ）
  python3 tools/collab.py status                         # 他の担当が最近pushした内容を表示
  python3 tools/collab.py install-hook                   # push前に自動で check を実行（環境変数 COLLAB_AGENT で担当を指定）

担当表は .collab/owners.json。他担当のパスを意図的に触るときだけ --allow-other を付ける。
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REMOTE = "origin"
BRANCH = "main"
TRACKING = f"refs/remotes/{REMOTE}/{BRANCH}"
AGENTS = ("claude", "codex")


def git(*args, cwd=None, check=True):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} が失敗: {r.stderr.strip() or r.stdout.strip()}")
    return r


def repo_root(cwd=None):
    return Path(git("rev-parse", "--show-toplevel", cwd=cwd).stdout.strip())


def load_owners(root):
    path = Path(root) / ".collab" / "owners.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8")).get("owners", {})


def owner_of(path, owners):
    """パスの担当を返す。担当表になければ None（共有）。長い（具体的な）パターンを優先。"""
    best = None
    for pattern, who in owners.items():
        hit = path.startswith(pattern) if pattern.endswith("/") else path == pattern
        if hit and (best is None or len(pattern) > len(best[0])):
            best = (pattern, who)
    return best[1] if best else None


def violations(files, agent, owners):
    """他担当のパスを触っているファイルを [(ファイル, 担当)] で返す。"""
    out = []
    for f in files:
        who = owner_of(f, owners)
        if who and who != agent:
            out.append((f, who))
    return out


def unpushed_files(root):
    """origin/main との差分ファイル（未push分＋作業ツリーの変更）。"""
    files = set()
    if git("rev-parse", "--verify", "-q", TRACKING, cwd=root, check=False).returncode == 0:
        files |= set(git("diff", "--name-only", f"{TRACKING}...HEAD", cwd=root).stdout.split())
    files |= set(git("diff", "--name-only", "HEAD", cwd=root).stdout.split())
    return sorted(files)


def fetch(root):
    git("fetch", "-q", REMOTE, f"+refs/heads/{BRANCH}:{TRACKING}", cwd=root)


def cmd_check(args):
    root = repo_root()
    if args.agent not in AGENTS:
        print(f"警告: 担当が不明（{args.agent!r}）。--agent claude|codex を指定してください。")
        return 0
    bad = violations(unpushed_files(root), args.agent, load_owners(root))
    if bad and not args.allow_other:
        print(f"他担当のファイルを変更しています（あなたは {args.agent}）:")
        for f, who in bad:
            print(f"  {f}（担当: {who}）")
        print("意図した変更なら --allow-other を付け、コミットメッセージに理由を書いてください。")
        return 2
    print("OK: 他担当のパスは触っていません。")
    return 0


def cmd_status(args):
    root = repo_root()
    fetch(root)
    r = git("log", "--oneline", "-n", str(args.n), TRACKING, "--format=%h %an %ar %s", cwd=root)
    print(r.stdout.strip() or "（履歴なし）")
    ahead = git("rev-list", "--count", f"{TRACKING}..HEAD", cwd=root).stdout.strip()
    behind = git("rev-list", "--count", f"HEAD..{TRACKING}", cwd=root).stdout.strip()
    print(f"手元が先行: {ahead} / 遅れ: {behind}")
    return 0


def default_target(agent):
    """claude は main へ、codex は自分専用ブランチへ push する（main へ直接は push しない）。"""
    return BRANCH if agent == "claude" else "codex/work"


def remote_branch_exists(root, name):
    return git("ls-remote", "--exit-code", "--heads", REMOTE, name, cwd=root, check=False).returncode == 0


def integrate(root, target):
    """最新を手元に取り込む。main 宛ては rebase（直線の履歴）、作業ブランチ宛ては merge（履歴を書き換えず force 不要）。
    衝突したら中止して手元を元に戻し、False を返す。"""
    fetch(root)
    if target == BRANCH:
        steps = [("rebase", TRACKING)]
    else:
        steps = [("merge", "--no-edit", TRACKING)]
        if remote_branch_exists(root, target):
            ref = f"refs/remotes/{REMOTE}/{target}"
            git("fetch", "-q", REMOTE, f"+refs/heads/{target}:{ref}", cwd=root)
            steps.append(("merge", "--no-edit", ref))
    for step in steps:
        r = git(*step, cwd=root, check=False)
        if r.returncode != 0:
            git(step[0], "--abort", cwd=root, check=False)
            print(r.stdout.strip() + "\n" + r.stderr.strip())
            return False
    return True


def cmd_sync(args):
    root = repo_root()
    if args.agent not in AGENTS:
        print("--agent claude|codex を指定してください。")
        return 2
    target = args.branch or default_target(args.agent)
    if args.agent == "codex" and target == BRANCH and not args.allow_other:
        print("codex は main へ直接 push しません。作業ブランチ（既定 codex/work）へ push して PR を出してください。")
        return 2
    if git("status", "--porcelain", cwd=root).stdout.strip():
        print("コミットされていない変更があります。先にコミットしてください。")
        return 2
    owners = load_owners(root)
    for attempt in range(1, args.retries + 1):
        if not integrate(root, target):
            print("衝突しました（取り込みを中止し、手元は元のままです）。双方の意図を残して手で解決するか、ユーザーに報告してください。")
            return 3
        files = sorted(set(git("diff", "--name-only", f"{TRACKING}...HEAD", cwd=root).stdout.split()))
        bad = violations(files, args.agent, owners)
        if bad and not args.allow_other:
            print(f"他担当のファイルを変更しています（あなたは {args.agent}）:")
            for f, who in bad:
                print(f"  {f}（担当: {who}）")
            return 2
        if not files:
            print("push するものはありません。")
            return 0
        if not args.no_test:
            t = subprocess.run([sys.executable, "-m", "unittest", "discover", "tests"], cwd=root, capture_output=True, text=True)
            if t.returncode != 0:
                print("テストが失敗しました。push を中止します。\n" + t.stderr[-800:])
                return 4
        p = git("push", REMOTE, f"HEAD:refs/heads/{target}", cwd=root, check=False)  # force は使わない
        if p.returncode == 0:
            print(f"push 完了（{len(files)}ファイル → {target}）。")
            if target != BRANCH:
                print(f"次は {BRANCH} 宛ての Pull Request を作成してください（GitHub の画面、または gh pr create）。")
            return 0
        err = (p.stderr or "").lower()
        if any(k in err for k in ("authentication", "could not read username", "permission denied", "403", "401")):
            print("GitHub の認証がなく push できません。認証を探したり回避したりせず、ユーザーに報告してください。")
            print(p.stderr.strip()[-300:])
            return 6
        print(f"push が拒否されました（{attempt}/{args.retries}）。最新を取り込み直します。")
    print("再試行の上限に達しました。ユーザーに報告してください。")
    return 5


HOOK = """#!/bin/sh
# collab.py が作成。push 前に他担当のパスを触っていないか確認する。
python3 tools/collab.py check --agent "${COLLAB_AGENT:-unknown}"
"""


def cmd_install_hook(args):
    root = repo_root()
    hook = root / ".git" / "hooks" / "pre-push"
    hook.write_text(HOOK, encoding="utf-8")
    hook.chmod(0o755)
    print(f"インストールしました: {hook}\n使うときは環境変数 COLLAB_AGENT=claude または codex を設定してください。")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description="Claude と Codex の衝突防止")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("check", "sync"):
        s = sub.add_parser(name)
        s.add_argument("--agent", default=os.environ.get("COLLAB_AGENT", "unknown"))
        s.add_argument("--allow-other", action="store_true", help="他担当のパスを意図的に触る")
        if name == "sync":
            s.add_argument("--no-test", action="store_true")
            s.add_argument("--retries", type=int, default=3)
            s.add_argument("--branch", help="push 先のブランチ（既定: claude は main、codex は codex/work）")
    s = sub.add_parser("status")
    s.add_argument("-n", type=int, default=5)
    sub.add_parser("install-hook")
    args = p.parse_args(argv)
    try:
        return {"check": cmd_check, "sync": cmd_sync, "status": cmd_status, "install-hook": cmd_install_hook}[args.cmd](args)
    except RuntimeError as e:
        print(e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
