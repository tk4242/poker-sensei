# ポーカー先生 Webアプリ（VPS 用）

チャットより速く回せる「毎日の練習場」です。教材（`curriculum/`）・出典（`sources/`）・計算ツール（`tools/poker_math.py`）をそのまま使います。

## できること
| 画面 | 中身 |
|---|---|
| ホーム | 今日のメニュー（復習 → 苦手 → 次のレッスン → 合格ライン → ノルマ）、連続日数、14日の推移 |
| カリキュラム | ロードマップの Stage 0〜7。レッスン（教材の該当節＋理解チェック5問、8割で完了）と昇段試験（合格ラインを満たすと次のステージが開く） |
| トレーニング | すきま時間用の反復練習（バトル形式）。1問ずつすぐに答え合わせし、正解でまものにダメージ、5秒以内の正解は「かいしん」。テーマは12種（おまかせ＝復習と苦手を優先、期待値、ベットの大きさ、コール/フォールド、アウツ、ポットオッズ早撃ち、数学、役、ポジション、プリフロップ、ICM、メンタル・同調）。結果は通常の練習と同じ記録・復習に入り、レベルと経験値になる |
| 苦手克服クエスト | `curriculum/05` の4週間プラン（期待値 → ベットの大きさ → 勝率を数える → まとめて判断、毎回: 周りに流されない）。各週はレッスン・トレーニング・試練の3段。Stage 2 と Stage 6 のレッスンにも入っている |
| 練習 | 自動生成ドリル19種（役の強さ、ポジション図、最小レイズ、ポットオッズ10秒、MDF、α、アウツ、SPR、EV、エクイティ、BBディフェンス、3ベットサイズ、ICM、平均スタック）＋出典つき問題集（約200問）。間違い・「わからない」は間隔反復で復習に回る |
| 記録 | 実戦セッション（場所・順位・ITM・体調・ティルト7種・相手のタイプ分け・周りに合わせて決めたハンドの数）、ハンド（hands/TEMPLATE.md と同じ形）、勉強時間、テーマ別正答率 |
| コーチ | 記録からのアドバイス、プレイ前チェック（Tendler のウォームアップ・16時間ルール・数字カード＝早見表）、Cゲームのサイン、メンタル・ハンドヒストリー、予算計画。任意で AI コーチ（出典つき回答・ハンドレビュー） |
| 教材 | 教材全文、用語集検索、チートシート（印刷用）、計算機 |
| 知識 | 自動で育つ知識ベース（下の「自動で育つ知識ベース」）。収集 → 出典ページでの自動検証 → 本人の承認 → 教材・出題へ |
| 引き継ぎ | 「設定 → チャットのコーチに渡す要約」をチャットに貼ると、growth-tracker や /hand-review にそのまま渡せる |

ログインは本人1人だけ（パスワード、5回失敗で15分ロック、CSRF 対策、HTTPS 前提の Cookie）。

## VPS に置く手順（初回）
前提: Ubuntu などの Linux VPS、ドメイン1つ（例 `poker.example.com`）。**パスワードや API キーはチャットに貼らず、VPS の上だけで書いてください。**

1. DNS で `poker.example.com` の A レコードを VPS の IP に向ける。
2. VPS に SSH で入り、Docker を入れる（[Docker 公式の手順](https://docs.docker.com/engine/install/)。Ubuntu なら `curl -fsSL https://get.docker.com | sudo sh`）。
3. ファイアウォールで 22・80・443 だけ開ける（例: `sudo ufw allow OpenSSH && sudo ufw allow 80 && sudo ufw allow 443 && sudo ufw enable`）。
4. リポジトリを取ってくる（非公開リポジトリなので、VPS で `gh auth login` するか、読み取り専用のデプロイキーを使う）:
   ```bash
   git clone https://github.com/tk4242/poker-sensei.git
   cd poker-sensei/app
   cp .env.example .env && chmod 600 .env
   python3 -c "import secrets;print(secrets.token_hex(32))"   # 出てきた文字列を SECRET_KEY に
   nano .env    # DOMAIN、SECRET_KEY、APP_PASSWORD（12文字以上）を書く
   docker compose up -d --build
   ```
5. ブラウザで `https://poker.example.com` を開き、`APP_USER`（既定 `koja`）とパスワードでログイン。スマホならホーム画面に追加すると便利です。

HTTPS の証明書は Caddy が Let's Encrypt から自動で取ります（DNS が向いていないと取れません）。

### ドメインがないとき
```bash
docker compose -f docker-compose.yml -f docker-compose.local.yml up -d --build web
# 手元のPCから:  ssh -L 8000:127.0.0.1:8000 ユーザー@VPSのIP   → http://localhost:8000
```

## 更新・バックアップ
- 教材やアプリを更新: `cd poker-sensei && git pull && cd app && docker compose up -d --build`
- データ（SQLite）は Docker ボリューム `sensei-data` にあり、更新しても消えません。
- バックアップ: 画面の「設定 → 全データのバックアップ（JSON）」、または
  `docker compose exec web python -c "import sqlite3;s=sqlite3.connect('/data/sensei.db');d=sqlite3.connect('/data/backup.db');s.backup(d)" && docker compose cp web:/data/backup.db ./backup.db`
- パスワードを平文で置きたくないとき: `docker compose run --rm web python -m sensei hash-password` の出力を `APP_PASSWORD_HASH=` に書き、`APP_PASSWORD` を消す。
- 設定の確認: `docker compose run --rm web python -m sensei check`

## AIコーチ（任意）
`.env` に `ANTHROPIC_API_KEY` を書いて `docker compose up -d` し直すと有効になります。
- モデルは `claude-opus-5-5`（`COACH_MODEL` で変更可）。Web 検索は Poker TDA・法令・GTO Wizard・Upswing など信頼できるドメインに限定し、出典URLつきで答えさせています（`sensei/coach.py`）。
- Anthropic API の従量課金です（料金: [公式の料金ページ](https://platform.claude.com/docs/en/about-claude/pricing)）。1回ごとに独立した短い依頼にしてトークンを節約しています。
- AI の答えは間違うことがあります。大事な判断は出典を開いて確かめ、チャットの fact-checker でも確認してください。

## 自動で育つ知識ベース（任意。AIコーチと同じ API キーを使う）
画面「知識」で、AI が信頼できるサイトから出典と原文の引用つきの「知識カード」を最大3枚集めます。別の呼び出しで出典ページを実際に開いて検証し、通ったものが「承認待ち」に並びます。
**あなたが承認したものだけ**が、ステージのページと、トレーニングの「最新の知識」・おまかせに入ります。承認から90日を超えたカードには「要再確認」が付き、再検証できます。

- 料金: VPS の API キーで動くので、Claude のチャットの利用制限は減りません（API の料金は別）。1回ごとの料金の目安を記録し、画面で決めた月の上限（初期値 $5）に達すると止まります。目安の単価は `.env` の `KNOWLEDGE_PRICE_*` で計算します（最新の料金は Anthropic の公式料金ページで確認してください）。
- 週1回の自動実行（VPS の cron。例: 毎週月曜6時。`crontab -e` に1行足す）:
  ```
  0 6 * * 1 cd ~/poker-sensei/app && docker compose exec -T web python -m sensei knowledge-run >> knowledge.log 2>&1
  ```
  テーマはロードマップの Stage 1〜7 を、いちばん古いものから順に回します。

## 見た目と素材のライセンス
レトロRPG風の見た目は、既存ゲームの素材（キャラクター・ロゴ・フォント・音楽）を使わずに作っています。
- フォント: [DotGothic16](https://github.com/fontworks-fonts/DotGothic16)（SIL Open Font License 1.1。`sensei/static/fonts/OFL-DotGothic16.txt`）。アプリ内に同梱しているので外部へは読み込みに行きません。
- キャラクター・背景: このリポジトリのオリジナルのドット絵（`app/sprites/make_sprites.py` の文字の絵が原本。`python3 app/sprites/make_sprites.py` で SVG を作り直せます）。

## 中身（開発者向け）
- `sensei/` Flask アプリ。`drills.py`（自動生成ドリル。答えは `tools/poker_math.py` で計算）、`practice.py`（出題・採点・SRS）、`progress.py`（合格ライン）、`coach.py`（AI）
- `content/stages.json` ステージ・レッスン・合格ライン（`curriculum/00-roadmap.md` 準拠）
- `content/questions/stage*.json` 問題集。**追加・修正したら fact-checker を通す**（記録: `content/FACT-CHECK.md`）
- テスト: `pip install -r app/requirements.txt && python3 -m unittest discover tests`
- ローカルで試す: `cd app && SECRET_KEY=$(python3 -c "import secrets;print(secrets.token_hex(32))") APP_PASSWORD=test-password-123 SECURE_COOKIES=0 flask --app sensei:create_app run`
- 担当: `app/` は Claude（`.collab/owners.json`）。Codex は改善案を PR で。
