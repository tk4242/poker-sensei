---
name: lesson
description: ロードマップに沿って次のレッスンを進める。「次を教えて」「レッスン」「今日の勉強」などのときに使う。
argument-hint: "[テーマ（省略可）]"
---

# レッスンの進め方

1. `curriculum/00-roadmap.md` と `learner/progress.md` を読み、現在のステージと次の単元を決める。引数 `$ARGUMENTS` があればそのテーマを優先。
2. 該当する `curriculum/` の教材を読み、今日の学習目標を1〜3個に絞って宣言する。
3. 説明は短く区切り、1区切りごとに理解確認の質問を1つ入れる。
4. 数値例は `python3 tools/poker_math.py` で計算する。
5. 教材にない内容を教える必要が出たら、`researcher` サブエージェントで調べ、`fact-checker` を通してから話す。教材への追記も提案する。
6. 最後に3問のミニテスト → 結果を `learner/progress.md` に日付つきで追記し、`growth-tracker` に渡して `learner/growth.md` を更新。
7. 次回の予告と、今日できるようになったことを具体的に褒めて締める。
