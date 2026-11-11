# 問題集とドリルのファクトチェック記録

## 2026-10-05（初版）
- 作り方: 問題は既存教材（`curriculum/01〜04`、ファクトチェック済み）に出典URLつきで書かれている記述だけから作成。【要確認】の項目・ソース間で食い違う数値は「唯一の正解」にしない。数値は `tools/poker_math.py` で検算。
- 検証: fact-checker 2体で全195問を確認。正解そのものの誤りは0件。直したのは17問（あいまいな選択肢・出典とずれた解説・古い出典）。削除0件。
  - Stage 0〜3（120問）: s0-rules-018（ショーダウンの順番の前提）、s0-terms-009（プローブベットの場面）、s1-preflop-014（原文は「レイトポジション」）、s3-postflop-009（ドンクの頻度の書き方）
  - Stage 4〜7（75問）: s5-live-004〜007（TDA 2026年版 Rule 44・55-A・69・73 に更新。旧2015年版から条番号とレイズ方法の記述が変わっていた）、s7-legal-002・009、s7-overseas-001（WSOP メインは15%入賞を維持）、s6-bankroll-003、s6-mental-017、s4-tournament-002、s4-icm-007
- ドリル（`sensei/drills.py`）: 席の並び・行動順・IP判定・BBディフェンス（2.25BB→20.8%）・BF/(BF+1)・アウツは教材と一致。直した点: ポジション区分の出典を PokerCoaching に（Poker.org は HJ をレイトに数える旨を注記）、3ベットのソルバー例の倍率、最小レイズの言い回し（Rule 45「そのラウンドで最大のフル」）、BBディフェンスのラベルを RULE に。
- 未確認のまま: s7-overseas-002（非居住者のギャンブル損失控除。IRS Pub. 519 本文を取得できず）、string bet の「最初の動作のみ有効」（TDA 条文では未確認）、s4-icm-003 の 37.5%（GTO Wizard の数字をそのまま使用）。
- 教材側の宿題: `curriculum/03-mental-training.md` A-8 のエチケットの出典が2015年版 TDA。2026年版に更新が必要。`curriculum/01-terms.md` 1.4 の区分と IP/OOP の行に出典を付ける。

## 2026-10-10（苦手克服 `weak05.json` 20問）
- 作り方: `curriculum/05-numbers-and-confidence.md`（ファクトチェック済み）の出典つきの記述だけから作成。数値（EV +50/+10/0、必要勝率 20/25/28.6/30/33.3/37.5%、必要フォールド率 33.3%、9アウツ 19.6%）は `tools/poker_math.py` で検算。
- 検証: fact-checker が全20問を原文と照合。正解そのものの誤りは0件。直したのは5問:
  - w05-011: Upswing Rule #3・#4 にソルバーへの言及がないため「ソルバーの傾向に基づく」を「戦略サイトの一般則」に。ラベルを新設の THEORY（一般則。ソルバー出力ではない）に変更
  - w05-015: 誤答「約30%」が Asch の実在の数値（平均同調率32%）と紛らわしいため「約95%」に差し替え
  - w05-017: 正解文の重複表現を修正、注記を原文（「筆者の偏見に基づく」）に寄せた
  - w05-018: 出典がキャッシュゲームの記事であることと「保証ではない」を追記
  - w05-019: 「みんな強そう＝自信が下に振れたサイン」は本書の読み替えであると明記
- 教材側の宿題: `curriculum/05` 3-3 にも「ソルバーの傾向に基づく一般則」という同じ言い回しがある（Upswing 原文にソルバーの言及はない）。
## 2026-10-11 数字の基礎コース

対象：`sensei/foundations.py`、`templates/basics*.html`。リポジトリのfact-checker手順に沿って別エージェントが公式3ページと照合し、`tools/poker_math.py`で30条件を検算。
- EVの定義、判断時点を基準にした比較、チップEVと大会価値：正しい。
- コール額÷コール後ポット、将来ベットがある場合の限界：正しい。相手1人・追加ベット/引き分け/レーキなし・仮の勝率を明記。
- サイズ25/50/75/100/150%の必要勝率は16.7/25.0/30.0/33.3/37.5%。最適サイズの推奨表ではない。
- Strategyの頻度・EV・EQとInfoboxの説明：公式Study Modeと一致。
- 指摘：ベット教材のGTO Wizard機能説明にStudy Modeの出典を追加 → 反映済み。
- 学習手順と4/5の目安はアプリ独自のものと明記。GTO解・賞金EVの最適化・有料機能の利用権を提供する主張はしない。

根拠：
- https://blog.gtowizard.com/what-is-expected-value-in-poker/
- https://blog.gtowizard.com/what-are-pot-odds-in-poker/
- https://help.gtowizard.com/study-mode/

## 2026-11-08 Codex：卓トレーニング / レンジ暗記
- 対象：`sensei/arena.py`、`templates/arena*.html`、`templates/_table.html`、`content/ranges/`。
- 独立したfact-checkerによる原典照合：HRCの全1,014頻度（5/8/10bb×SB/BB×169）を公式Raw Dataと比較して一致。混合を過半数で純粋戦略に丸めていない。
- HUのstack/pot（SB判断1.5bb、BB判断S+1bb）、2/6/8/9人のpre/post行動順、手札・169表の対応を確認。
- 5つのフロップ対決の全990runoutsを `poker_math.equity` で独立に再計算。数値一致。元ポット6/6.5、bet3/6/9のEV・必要EQを検算。
- 修正指摘を反映：多人数フロップのSB 0.5bbを座席の投資と履歴へ追加。「必要勝率」を引き分けの取り分込みの「必要エクイティ」に訂正。
- 追加対決 8c9c vs AdAs / 6d7h2s：EQ34.242424%。元ポット6bbでcall EV +1.1091/+0.1636/-0.7818bb、6.5bbで+1.2803/+0.3348/-0.6106bb（bet3/6/9）。価格でcall/foldが変わることを確認。
- 最終判定：教材ファクトチェック合格。一般のMTT/リングへ限定HU解を適用しない表示、原CSVの条件メタデータ不足の表示を維持。6/8/9人のレンジやGTOフロップ頻度は未検証のため収録しない。架空のEV損失を表示しない。
- 原データの明示的なオープンライセンスは未確認。正確性の検証と利用許諾の判断は区別。ART/GTOのデータは採用しない。


## 2026-11-08 Codex：最大8人への追加修正（PR #7）
- `stage0.json` の5問を8人卓へ変更。最後は8番目のBB、BTNの次はSB、BTN直前はCO、3番目はLJ、UTG+1の次はLJ。
- 別fact-checkerが既存のPoker.org出典と選択肢・正解・解説を照合し合格。8人ではUTG+2を省く席名体系に一致。
- 指摘に従い、8人卓問題の不正解候補UTG+2をBBへ、出典で確認できない「オンラインMTTは8人卓が多い」という一般化を削除。
- 卓トレーナーは2/6/8、従来ドリルは6/8へ限定。新GTO戦略・数値の追加や変更なし。

## 2026-11-10 Codex：アクション入門8テーマ40問・2〜8人卓
- 教材作成担当とは別のaction_fact_checkが全出典を独立openし、全説明/正答/例の条件を照合して合格。source_ids→URLの対応はaction-lessons.jsonとsources/SOURCES.md。
- actions/ranges/flop/sizing/threebet/turnriver：定義、レンジ形態、ナッツ優位、チェック/Cベット、将来ベットがある場合のEQ実現を確認。Cベットを「プリフロップの最後の攻撃者」へ精密化、必要エクイティに引き分け持分を含むと補足。単独復習でも前提が読めるようsizing問題を修正。
- 数値：tools/poker_math.pyで必要EQ16.7/25.0/33.3/25.0%、EV+3.00bbを独立検算。役判定はKトップペアQキッカー/フラッシュと一致。3bet追加額7/5.5bb、コール後pot16.5bb、HU追加0.5bbも確認。
- HU：TDA2026v1.1 Rule36-CでBTN=SB、プリフロップSB先/ポストフロップBB先。HRC公式huneでpush/fold制約とブラインド前stackを確認。多人数卓から2人残った場合と最初からHUの違いを明記。
- bluff：GTO Wizard Picking the Right Semi-Bluffs、Blockers & Unblockersを独立照合。A5sはNL500/100bb/6max UTG対HJの公式例の考え方に限定。相手の強い継続手を減らす/フォールド候補を残す説明であり、最適サイズ/頻度の転載や捏造なし。カード除去AsKd不可も確認。
- 席順：PokerStars Poker Positions/PositionのBTN相対CO・HJ・LJとTDAを照合。3人BTN、4人CO、5人HJ、6人UTG=LJ、7人UTG→LJ、8人UTG→UTG+1→LJ。全2〜8のpost_orderも合格。
- 適用限界：一般則と定義の学習で、任意局面を解くGTOソルバーではない。MTTとリングの条件差、ICM/レーキ、HRC限定モデルの範囲を保つ。確認できない多人数レンジや推奨頻度は追加しない。

## 2026-11-10 卓上アクション20問
- 18問の作成者と別のaction_fact_checkがTDA45/49、PokerStars、GTO Wizardの出典を照合して承認。最小raise 2→4、2→6→10、pre2.5→8→13.5bbを確認。
- tools/poker_math.pyで必要EQ25%、仮定勝率30%/20%のEV+0.65/-0.65bbを検算。これは手札から計算した勝率ではないと問題文に明示。
- 18×7人数の126派生で席・手番・ポット・投入・残stack・カード重複を検証。HUでは別SBのdeadmoneyとfold履歴を除去。フロップは開始6.5bbを条件として与え、プリフロップ履歴を省略。
- 公式例2問はfact-check担当が作成し、親が原典を独立照合（Navigating Range Disadvantage as the 3-Bettor、KQoチェック、KcQc smallstabフォールド）。NL500/6人/開始150bb/CO対BB/12bb3bet/854rだけに限定。現在pot/stack不明は表示を補完しない。
- Claude Agentのfact-checker呼出しはavailable agents:noneで実行不可。上記独立担当が同じfact-checker手順で出典・計算確認を実施。
- 3〜8人GTOレンジは全条件と利用権の確認された無料データ未確保。表の席を減らす変換や架空頻度は採用しない。今回追加はルール・算術18問と原典局面2問のみ。

## 2026-11-11 公開レンジ資料・人数ガイド
- 独立action_fact_checkがLightTHREE/公式動画リンク/GTO Wizardを調査。記事はMTT目安、後ろ人数基準。stack/ante/rake/ICM/raise条件は不明、本人の本編と169マス一致未確認。新range-reading5問とguideの断定回避を承認。
- PokerStars/TDA一次資料と2〜8人のbehind全28非BB席を独立照合。8UTG後ろ7、6HJ後ろ4、BTN後ろ2、HU BTN/SB後ろ1。BB全foldは既に勝ちでクイズから除外。
- PokerQz公開PDFを親・独立担当が照合。NL50/6max/100BB/UTG HJ CO fold/BTN first-in/Raise2.5BB。54s76.4+23.6=100、22の76.3+23.7=100。クラス集約値の読解として採用可能、特定スートへの頻度適用やGTO独立検証とは扱わない。
- PokerQz本文には簡易レンジ表記もあるため公表PDFの値と混同しない。全ソルバー条件は未検証。Chromeの既存タブはツール接続不可、公開ページとPDFのみを確認した。
