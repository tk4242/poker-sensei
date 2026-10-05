# poker-sensei 🃏

初心者から「海外トーナメントでインマネ」を目指す、出典つきのポーカー教材と Claude Code 用のコーチ環境。

## 使い方
1. このリポジトリで Claude Code を開く（`claude`）。`CLAUDE.md` が自動で読み込まれ、Claude がヘッドコーチになる。
2. よく使うコマンド:
   - `/lesson` 次のレッスン
   - `/quiz` 確認テスト
   - `/hand-review` 自分のハンドを検討
   - `/session-log` プレイ後の記録
   - `/fact-check curriculum/02-strategy.md` 教材の検証
   - `/refresh-sources` 古い情報の更新（月1回）
3. 計算ツール: `python3 tools/poker_math.py --help`（テスト: `python3 -m unittest discover tests`）

## 中身
| パス | 内容 |
|---|---|
| `CLAUDE.md` | コーチの基本ルール（出典必須、GTOとエクスプロイトの区別、話し方） |
| `.claude/rules/sourcing.md` | 出典とファクトチェックのルール |
| `.claude/agents/` | サブエージェント7体（researcher / fact-checker / hand-reviewer / math-coach / mental-coach / quiz-master / growth-tracker） |
| `.claude/skills/` | スキル6個（上のコマンド） |
| `curriculum/00-roadmap.md` | 7ステージのロードマップと合格ライン |
| `curriculum/01〜04` | 用語・戦略・メンタル/練習・日本と海外（全てファクトチェック記録つき） |
| `sources/SOURCES.md` | 出典台帳 |
| `learner/` | プロフィール・進捗・苦手リスト・成長記録（`growth.md`） |
| `hands/` | ハンドレビュー |

## 注意
日本国内での賭け金のあるポーカーや、日本からのリアルマネー・オンラインポーカーは違法になりうる。詳しくは `curriculum/04-japan-and-overseas.md`（法律・税務の助言ではない）。
