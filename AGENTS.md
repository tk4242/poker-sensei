# 共同作業ルール（Claude と Codex が同じリポジトリを触る）

このリポジトリ（tk4242/poker-sensei）は Claude Code と OpenAI Codex の両方が編集する。衝突（バッティング）を避けるため、次を守る。
Codex は Git ルートの `AGENTS.md` を読む（出典: https://learn.chatgpt.com/docs/agent-configuration/agents-md、2026-10-05確認）。Claude Code は `CLAUDE.md` から `@AGENTS.md` で取り込む。

## 基本ルール
1. 作業を始める前と push の前に、必ず `git pull --rebase origin main` で最新を取り込む。
2. force push はしない。他者のコミットを書き換えない（rebase は自分の未pushコミットだけ）。
3. 1回の変更は小さく、1コミット1目的。変更したらすぐ push して、長く手元に溜めない。
4. 衝突したら、双方の意図を残して解決する。判断できないときは作業を止めて、ユーザーに報告する。
5. 他の担当のファイルは、頼まれない限り編集しない（下の担当表）。

## 担当（暫定。ユーザーの回答で更新する）
| 場所 | 担当 | 備考 |
|---|---|---|
| `learner/`（成長記録・進捗） | Claude（`growth-tracker`） | Codex は読むだけ。短い間隔で小まめに push される |
| `.claude/`、`CLAUDE.md` | Claude | Claude Code の設定 |
| `curriculum/`、`sources/` | 先に編集を始めた方。変更前に必ず pull | 内容を変えたら出典を付け、ファクトチェックを通す（`.claude/rules/sourcing.md`） |
| `tools/`、`tests/` | 共有。変更前に pull、変更後に `python3 -m unittest discover tests` | |
| `AGENTS.md` | どちらでもよい。変更理由をコミットメッセージに書く | |

## 教材の品質ルール（Codex も同じ）
- 戦略・数値・ルール・法律の主張には出典を付ける。確認できない内容は書かず、`【要確認】` を付ける。
- 日本国内での賭け金のあるポーカーや、日本からのリアルマネー・オンラインポーカーは勧めない（`curriculum/04-japan-and-overseas.md`）。
