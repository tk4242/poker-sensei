# 共同作業ルール（Claude と Codex が同じリポジトリを触る）

このリポジトリ（tk4242/poker-sensei）は Claude Code と OpenAI Codex の両方が編集する。衝突（バッティング）を避けるため、次を守る。
Codex は Git ルートの `AGENTS.md` を読む（出典: https://learn.chatgpt.com/docs/agent-configuration/agents-md、2026-10-05確認）。Claude Code は `CLAUDE.md` から `@AGENTS.md` で取り込む。

## 仕組み（ルールを人任せにしない）
担当表は `.collab/owners.json`、道具は `tools/collab.py`（テスト: `tests/test_collab.py`）。
- **main へ push するのは Claude だけ**。Codex は自分専用のブランチ `codex/work`（`--branch` で別名も可）へ push し、`main` 宛ての Pull Request を出す。main への直接 push はツールが止める。
- **push は必ずこれで**: Claude は `python3 tools/collab.py sync --agent claude`、Codex は `python3 tools/collab.py sync --agent codex`。最新の main を取り込み（Claude は rebase、Codex は merge。履歴を書き換えないので force 不要）→ 他担当のファイルを触っていないか確認 → テスト → push を行い、拒否されたら取り込み直して最大3回やり直す。**force push は一切しない**。
- **認証がなくて push できないとき**（終了コード6）: 認証情報を探したり回避したりせず、そこで止めてユーザーに報告する。
- **衝突したら**: rebase を中止して手元を元のまま残し、止まる（終了コード3）。双方の意図を残して解決するか、ユーザーに報告する。
- **他の担当のファイル**を触ると push が止まる（終了コード2）。頼まれて意図的に触るときだけ `--allow-other` を付け、理由をコミットメッセージに書く。
- 事前確認: `python3 tools/collab.py check --agent codex` / 他の担当の最近の push: `python3 tools/collab.py status`。
- 任意: `python3 tools/collab.py install-hook` で push 前の確認を自動化（環境変数 `COLLAB_AGENT` を設定）。
- GitHub 側でも、main への push のたびにテストと文脈サイズの点検が自動で走る（`.github/workflows/check.yml`）。

## Pull Request の流れ（Codex）
1. 変更をコミットし、`sync --agent codex` で `codex/work` へ push。
2. GitHub で `codex/work` → `main` の PR を作る（本文の最初に、何を・なぜ変えたかと、出典・テストの結果を書く）。
3. 内容は Claude の `fact-checker` がレビューし、マージはユーザーが決める。マージ後、Codex は次の作業の前に `sync` で最新の main を取り込む。

## 基本ルール
1. 作業を始める前に `python3 tools/collab.py status` で、相手の最近の変更を確認する。
2. 変更は小さく、1コミット1目的。変更したらすぐ `sync` して、手元に溜めない。
3. 他者のコミットを書き換えない（rebase は自分の未pushコミットだけ）。
4. 他の担当のファイルは、頼まれない限り編集しない（下の担当表）。

## 担当（暫定。ユーザーの回答で `.collab/owners.json` と一緒に更新する）
| 場所 | 担当 | 備考 |
|---|---|---|
| `learner/`、`hands/`（成長記録・進捗・ハンド検討） | Claude（`growth-tracker`） | Codex は読むだけ。短い間隔で小まめに push される |
| `.claude/`、`CLAUDE.md` | Claude | Claude Code の設定 |
| `curriculum/`、`sources/`、`tools/`、`tests/` | 共有 | 先に着手した側が優先。変更前に pull（`sync` が自動で行う）。教材を変えたら出典を付け、ファクトチェックを通す |
| `AGENTS.md`、`.collab/`、`.github/` | 共有 | 変更理由をコミットメッセージに書く |

## 教材の品質ルール（Codex も同じ）
- 戦略・数値・ルール・法律の主張には出典を付ける。確認できない内容は書かず、`【要確認】` を付ける。
- 日本国内での賭け金のあるポーカーや、日本からのリアルマネー・オンラインポーカーは勧めない（`curriculum/04-japan-and-overseas.md`）。
