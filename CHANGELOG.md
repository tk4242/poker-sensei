# 修正履歴（Claude と Codex の共有）

新しい順。変更したら、その PR の中でこのファイルの先頭に追記する（日付・PR・何を・どこを・残っている宿題）。
細かい差分は `git log` と各 PR を見る。教材のファクトチェック記録は各ファイルの末尾と `app/content/FACT-CHECK.md` にある。

## 2026-10-10〜11 PR #3（Claude）苦手克服クエスト・トレーニング・知識ベース・RPG風UI
https://github.com/tk4242/poker-sensei/pull/3 （PR #2 の上に作成。#2 → #3 の順にマージ）
- 苦手克服クエスト `/quest`: `curriculum/05` の4週間プラン。データは `app/content/stages.json` の `quest`。Stage 2 に L2-6〜8 と合格ライン `s2-decision`、Stage 6 に L6-6 を追加
- 問題集 `app/content/questions/weak05.json`（20問、fact-checker 済み、指摘5件を反映）。新ラベル `THEORY`（戦略サイトの一般則。ソルバー出力ではない）
- トレーニング `/train`（1問ずつ即答え合わせのバトル形式）: `app/sensei/train.py`、`views/train.py`、テンプレ `battle.html` など。記録は `attempts`（mode='train'）と `srs` に入る
- 知識ベース `/knowledge`: `app/sensei/knowledge.py`。Claude API で収集 → web_fetch で出典を検証 → 本人承認 → ステージのページとトレーニングに出る。cron 用 `python -m sensei knowledge-run`、月の上限（初期値 $5）
- プレイ記録に `conformed`（周りに合わせたハンドの数）。既存 DB には起動時に列を追加（`db.py` の `MIGRATIONS`）
- 見た目: フォント DotGothic16（OFL、`app/sensei/static/fonts/`）、オリジナルのドット絵（原本は `app/sprites/make_sprites.py`）。CSP のためテンプレートに style 属性を書かない（テストあり）
- テスト: `tests/test_app_train.py`、`tests/test_app_knowledge.py`（合計66件）
- 宿題: 知識ベースは本物の API で未実行（偽の応答でのみテスト）。`curriculum/05` 3-3 の「ソルバーの傾向に基づく一般則」は Upswing 原文にソルバーの言及がないので直す

## 2026-10-10 PR #2（Claude・別スレッド）苦手克服プランとドリル3種
https://github.com/tk4242/poker-sensei/pull/2
- `curriculum/05-numbers-and-confidence.md`（期待値・ベットの大きさ・オッズ・同調メンタル、4週間プラン）
- `app/sensei/drills.py` に `bet_price`・`ev`・`call_decision` を追加
- `learner/weak-points.md` に本人申告の弱点4件、`/session-log` に「合わせたハンド数」

## 2026-10-05 PR #1（Claude、マージ済み）VPS 用の学習 Web アプリ
https://github.com/tk4242/poker-sensei/pull/1
- `app/`（Flask + SQLite + Caddy、Docker Compose）。手順は `app/README.md`
- Stage 0〜7 のレッスン・昇段試験、自動生成ドリル、問題集195問、間隔反復、記録、メンタル、AI コーチ
- 担当表 `.collab/owners.json` に `app/`・`tests/test_app*` を Claude 担当として登録
- 宿題: Docker イメージのビルドは未確認（作業環境で Docker Hub の制限）。`curriculum/03` A-8 の TDA 出典が2015年版（2026年版へ更新）。`curriculum/01` 1.4 の区分と IP/OOP に出典を付ける。出典つきのレンジ表・ショーブ表のドリルは未作成
