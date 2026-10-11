# 修正履歴（Claude と Codex の共有）

新しい順。変更したら、その PR の中でこのファイルの先頭に追記する（日付・PR・何を・どこを・残っている宿題）。
細かい差分は `git log` と各 PR を見る。教材のファクトチェック記録は各ファイルの末尾と `app/content/FACT-CHECK.md` にある。

## 作る目的（2026-10-11 時点。変わったらここを直す）
- 学習者の Mr古謝 を、用語も怪しい初心者から「海外トーナメントでインマネ（ITM）」できるレベルまで育てる。ロードマップは `curriculum/00-roadmap.md`（Stage 0〜7）
- プレイ場所: 国内アミューズメント大会、仲間内のゲーム、オンライン/アプリ（日本からのリアルマネーや賭けのホームゲームは勧めない）
- 学びたいこと: 用語、ベットの大きさ、状況別の行動、メンタル、トレーニング方法
- 一番大事にしていること: 間違った方向で覚えたくない。出典を確認した正しい知識だけを教える（`.claude/rules/sourcing.md`）
- チャットでは不便なので、VPS 上の Web アプリ（`app/`）で、カリキュラム・すきま時間の反復練習・記録・コーチをまとめる。起動は本人が VPS で行う（Claude のトークンを節約するため）
- 世界の最新の戦略を LLM で集めて検証し、本人が承認したものだけ教材に足して育てる（知識ベース `/knowledge`）

## 学習者の課題（2026-10-11 時点。最新は `learner/active.md` と `learner/weak-points.md`）
- 現在地: Stage 0（ルールと用語）。累計25問中17問正解（68%）
- 席と順番: 行動の先／後（IP/OOP、レイト＝CO・BTN、プリフロップの最後は BB）、CO の位置、ブラインドの並び（BTN→SB→BB→UTG）
- 本人申告の弱点（2026-10-10）: 期待値（EV）の考え方、ベットの大きさの意味と決め方、オッズ・勝率の計算（ポットオッズ・アウツ）、周りが強そうに見えると合わせてしまう（同調）
- 対策: `curriculum/05-numbers-and-confidence.md` の4週間プランと、アプリの苦手克服クエスト `/quest`・トレーニング `/train`
- 好み: 4択で入力は最小限、席の問題は図つき、5問まとめて出題し各問に「なぜ学ぶか」を付ける。親しみやすく励ます口調

## 2026-10-11 Codex：クイズの回答を見直せる移動操作（PR #3 に同梱）
- 症状: クイズで戻ったあと、答えを変えないと先へ進めない。回答直後に戻ると、予約済みの自動送りで勝手に次へ飛ぶ
- Codex のパッチ（コミット dac708a、main 基準）を Claude が PR #3 のブランチに手で移植（作者は Codex のまま）。`style.css` と `CHANGELOG.md` は PR #3 側と土台が違うため、Codex の追加分だけを足した
- `app/sensei/static/app.js`: 全問に「前の問題」「次の問題」。回答済みなら答えを変えずに進める。移動したら自動送りの予約を取り消す。進捗バーは回答済みの数で表示
- `app/sensei/templates/quiz.html`・`static/style.css`: 移動ボタン（JS なしでは隠して全問表示）、読み上げ用の進捗、移動先の問題文にフォーカス
- テスト: `tests/test_quiz_navigation.js`（実際の app.js を Node で動かす4件。変更前の app.js では4件とも失敗）と `tests/test_app_navigation.py`。全69件成功
- 画面: Claude が実ブラウザ（スマホ幅）で、4問回答→3回戻る→答えを変えずに2回進む→答えを変えて直後に戻る、を確認（勝手に進まない、コンソールエラーなし）
- 出典: 操作の修正のみ。教材・戦略・数値は変更なし

## 2026-10-11 Codex：苦手に直結する5問練習と読みやすさ（PR #3 に同梱）
- Codex の push が GitHub 認証切れで止まったため、パッチ（コミット 609860e）を Claude が `git am` で PR #3 のブランチに取り込んだ（作者は Codex のまま）。別の PR は作らない
- ユーザー依頼「UIや課題解決、目標達成に向けてアプリをブラッシュアップ」に基づく `app/` と `tests/test_app_train.py` の変更。
- ホームは復習待ちを最優先、Stage 0 は図つきの席・順番5問、それ以降は現在のステージへ案内。
- 席と順番・EV・ベットサイズ・オッズ判断・同調の5つの入口を追加。`/practice/quick/<focus>` は設定に関係なく5問。既存の検証済みドリル・問題集と採点・復習を利用し、新しい戦略や数値は追加しない。
- 問題に「なぜ学ぶ？」を回答前から表示。結果から復習に進める。終了を「にげる」ではなく「ここまでの結果を見る」と表現。
- RPGの見出し・キャラクターは維持し、本文と選択肢は通常の日本語フォント。スマホ用の1列カード、キーボードのフォーカス枠、ヘッダーナビの折り返しを追加。
- PR #3 のコミット e3f01ab を土台に実装。マージ順は #2 → #3 → 本PR。VPSの起動・反映は本人が行う。
- 検証：一時venvで全68テスト成功（スキップなし）。5テーマ各5問・採点保存・復習優先を追加検証。画面は Claude がパソコン幅とスマホ幅（390px）のスクリーンショットで確認済み（横はみ出しなし、コンソールエラーなし）。宿題：本物のAPIでの知識ベース検証と既存の教材出典の宿題は継続。

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
