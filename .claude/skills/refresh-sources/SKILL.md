---
name: refresh-sources
description: 出典台帳の古い情報（取得から90日超、日程・料金・法改正・アプリ状況）を再確認して教材を更新する。月1回、または情報が古そうなときに使う。
disable-model-invocation: true
---

1. `sources/SOURCES.md` から取得日が90日より前の行、または「変わりやすい」印の行を一覧にする。
2. 各項目を `researcher` サブエージェントで再調査する（並列でよい）。
3. 変化があった項目は `curriculum/` を修正し、`fact-checker` を通す。
4. 台帳の取得日を更新し、変更点のまとめを `learner/progress.md` の「お知らせ」に追記する。
