# 02 NLHE トーナメント戦略ガイド — ベットサイズと状況別アクション（初心者→インマネ目標）

- 作成日: 2026-10-05
- 対象: WSOP / APT / WPT / EPT などの海外ライブMTT、国内ライブトーナメント（アミューズメント含む）、ホームゲーム、オンライン/アプリ
- 表記ルール:
  - **[GTO]** = ソルバー（均衡）ベースの基準。相手を問わない土台。
  - **[EXP]** = 特定のプレイヤー層への搾取（エクスプロイト）調整。「母集団の傾向」であり、目の前の相手に当てはまるとは限らない。
  - **【要確認】** = 一次ソースで数値を検証できなかった項目。
  - 数値はすべてBB（ビッグブラインド）単位。「2.3x」=2.3BBへのオープン。
- 注意: 調査で引用したWebFetch要約はページ全文ではなくモデル要約経由のため、細かい数値は原典で再確認を推奨。

---

## 0. 前提：BBA（ビッグブラインド・アンティ）とは

- BBAは「BBのプレイヤーがテーブル全員分のアンティをまとめて払う」方式。ARIAが2017年に導入し、WSOPはサーキットと2018年夏のハイローラー全イベントに採用、WPT・partypoker・PokerStars・888pokerも採用（2018年時点の報道）。 https://www.pokernews.com/news/2018/01/big-blind-antes-pros-cons-29848.htm
- 影響: アンティ分だけ初期ポットが大きくなる（BBA構造ではプリフロップの初期ポットが約2.5BB＝SB0.5+BB1+アンティ1）。 https://redchippoker.com/mtt-secrets-3-bet-shoves/
  - → ①オープンは小さくても盗む価値が高い、②BBは安い価格で守れるので広くディフェンスする、③ショートのショーブ/リショーブが利益的になりやすい。
- 2026年の各ツアー（WSOP/APT/WPT/EPT/国内JOPT等）で全イベントがBBAかどうかは個別ストラクチャー表を要確認【要確認】。2026 WSOPは5/26〜7/15開催、メインイベントFTは8月に延期と報じられている。 https://en.wikipedia.org/wiki/2026_World_Series_of_Poker

---

## 1. プリフロップ：スタック深さ別サイズ

### 1-1. オープンレイズ（RFI）サイズ

| スタック | 推奨オープン | 根拠・出典 |
|---|---|---|
| 100bb | 2.3x [GTO] | GTO Wizardのスタック深さ比較 https://blog.gtowizard.com/how-stack-sizes-change-your-range/ |
| 50bb | 2.1x [GTO] | 同上。3ベットポット記事でもCO 2.1bb / 2.3bb https://blog.gtowizard.com/mastering-three-bet-pots-out-of-position-in-mtts/ https://blog.gtowizard.com/mastering-three-bet-pots-in-position-in-mtts/ |
| 40bb | 2.3x（BTN vs BB の解析。UTGの数値は未確認） [GTO] | https://blog.gtowizard.com/flop-heuristics-for-defending-the-blinds-in-mtts/ |
| 30bb | 2.1x前後 [GTO] | https://blog.gtowizard.com/mastering-three-bet-pots-in-position-in-mtts/ |
| 20bb | ほぼミニレイズ（2x）[GTO] | 「if the solver could bet less it probably would」 https://blog.gtowizard.com/how-stack-sizes-change-your-range/ （UTG・chipEV・MTTアンティあり） |
| 14bb | レイズに加えショーブが選択肢になり、リンプレンジ（UTGで4.6%）が出現。8bb・5bbのUTGファーストインはショーブorフォールドのみ [GTO] | 同上 |
| 9bb以下 | ミニレイズはショーブに置き換わる（AAも7bb以下はショーブ側）[GTO] | https://blog.gtowizard.com/playing-under-10bb-part-1-cev/ （chipEV、アンティは各自0.125bb＝BBAではない構造） |

**ソース間の幅（重要）**
- 解説系の一般論: 「2〜2.5BBが堅実なデフォルト」（PokerCoaching/Jonathan Little）。 https://pokercoaching.com/blog/preflop-strategy-guide-the-ultimate-guide-to-preflop-bet-sizing/
- Upswingの例: 2.25BBオープン（ボタン900/ブラインド200-400、BBアンティ400）。約47%でフォールドが取れれば即利益。 https://upswingpoker.com/poker-tournament-tips-strategy-mtt/
- **Red Chip Poker は「序盤のディープスタック時は約3xが大半の推奨」、「約80bbを下回ったら2.5xに下げてよい」**としており（序盤記事は3xに具体的bb数を結び付けていない）、ソルバー系（2.1〜2.3x）より大きい。 https://redchippoker.com/tournaments-3-early-levels/ https://redchippoker.com/tournaments-4-mid-levels/
- 結論（初心者向け）: **オンライン/強いフィールドは2〜2.3x、ライブで降りない相手が多い序盤は2.5〜3xも可**。後者は [EXP]。Upswingも「ブラインドに弱いプレイヤーがいるならオープンを大きく」としている。 https://upswingpoker.com/bet-size-strategy-tips-rules/

### 1-2. リンパーがいる時（アイソレーション）

- Upswing（記事は形式を明記せず、例示はキャッシュ寄り）: オンライン「3BB＋リンパー1人につき1BB」、ライブ「4BB＋リンパー1人につき1BB」。 https://upswingpoker.com/vs-multiple-limpers/
- トーナメント専用の数式は確認できず【要確認】。トーナメントはオープン自体が小さいので、上記をやや縮めて使うのが自然（推論であり出典なし）。

### 1-3. 3ベットサイズ

| 状況 | サイズ | 出典 |
|---|---|---|
| 一般則 IP | オープンの約3倍 | Upswing https://upswingpoker.com/bet-size-strategy-tips-rules/ ／ PokerCoaching https://pokercoaching.com/blog/preflop-strategy-guide-the-ultimate-guide-to-preflop-bet-sizing/ |
| 一般則 OOP | オープンの約4倍 | 同上 |
| ソルバー例 50bb BTN(IP) vs CO 2.1bb | 6.82bbへ（約3.2倍）[GTO] | https://blog.gtowizard.com/mastering-three-bet-pots-out-of-position-in-mtts/ |
| ソルバー例 50bb BB(OOP) vs CO 2.3bb | 9.8bbへ（約4.3倍）[GTO] | https://blog.gtowizard.com/mastering-three-bet-pots-in-position-in-mtts/ |
| ソルバー例 30bb BB vs 2.1bb | 8.2bbへ（約3.9倍）[GTO] | 同上 |
| Jonathan Little | オープンの約3倍（「2.5BB→7〜8BB」の例はPDF内で確認できず【要確認】。PDF内の実例は2BBオープン→5BB 3ベット→11.5BB 4ベット、50bb） | https://jonathanlittlepoker.com/pdf/Strategies.pdf |

- キャッシュの標準（IP 3.5x / OOP 4.5x）より、**トーナメントは浅くなるほど小さくしてよい**（Red Chip）。 https://redchippoker.com/tournaments-4-mid-levels/
- 25〜40bb: K9s、KJo、A6s などで「オールインではない3ベットブラフ」を使う（Upswing）。 https://upswingpoker.com/poker-tournament-tips-strategy-mtt/

### 1-4. 3ベット・ショーブ（リショーブ）ゾーン

- 有効スタック**約10〜25bb**が3ベットショーブ帯（著者により境界は多少異なる）。目安として「ショーブ額がオープンの**IPで10倍以内、OOPで12倍以内**」なら効率的。 https://redchippoker.com/mtt-secrets-3-bet-shoves/
- 40bb以上では小さい3ベットが優位になりやすい（同上）。

### 1-5. 4ベット

| スタック | サイズ | 出典 |
|---|---|---|
| 60bb+（トーナメント） | IP: 3ベットの約2.2倍 / OOP: 約2.6〜2.8倍 | https://upswingpoker.com/4-bet-size-strategy/ |
| 50bb前後 | 非オールイン4ベット（AA/KK/AKs等）とオールイン4ベットを混ぜる | 同上 |
| 30bb以下 | オールインが主な4ベットサイズ | 同上 |

### 1-6. プッシュ/フォールド開始ライン — **ソース間で差あり**

- Upswing: 「約15bb以下でプッシュ/フォールド」としつつ、2026年更新部分で「MTTではプッシュ/フォールド表の重要性は下がり、ミニレイズ戦略が好まれる」と付記。 https://upswingpoker.com/push-fold-tournament-strategy-charts/
- Upswing（別記事）: 「13〜15bbではナッシュのショーブレンジに従う」。 https://upswingpoker.com/open-raising-with-a-short-stack-tournaments/
- GTO Wizard: 14bbでショーブとリンプ（4.6%）が加わる（レイズも残る）、**9bb以下でミニレイズがショーブに置き換わる**、8bb・5bbのUTGファーストインはショーブ/フォールドのみ（ただしBBでオープンを受ける側は7bbでもフラットがある）。 https://blog.gtowizard.com/how-stack-sizes-change-your-range/ https://blog.gtowizard.com/playing-under-10bb-part-1-cev/
- 初心者への落とし所: **〜12〜15bbでショーブ表を使い始め、10bb未満では原則「ショーブorフォールド」**。チャートは「ナッシュ（chip EV）」が前提で、バブル等ICM下では締める必要あり（Upswingは「チャート丸暗記に頼るな」と警告）。 https://upswingpoker.com/push-fold-tournament-strategy-charts/

### 1-7. BBディフェンス（BBAで何が変わるか）

- 2.25BBオープンに対しBBは**20.8%のエクイティ**でコールが合う計算。レイトのオープンには**最低40%程度**（コール＋3ベット）守る。 https://upswingpoker.com/poker-tournament-tips-strategy-mtt/
- 19bb・BTNミニレイズ（フルリング・アンティあり）の例: 1,600コールで8,640のポット → 原文は**18.9%**と記載（ただし原文の式は「1640/(1600+7040)」で、1,600/8,640で計算すると**18.5%**。原文の算術に不整合あり）。ボタンのATC（any two cards）を防ぐにはBB約**46.4%**ディフェンスが必要。60%オープンのBTN相手に**16.1%ショーブ＋29.3%フラット＝45.4%**の例。 https://upswingpoker.com/guide-big-blind-defense-mtts-modern-short-stack-play/
- 7bbでもBBは2xオープンに非常に広くコール（96sが利益的コール）。 https://blog.gtowizard.com/playing-under-10bb-part-1-cev/
- **大きいオープンにはより多くフォールド**（ソルバーはオープナーのレンジをサイズ間で固定と仮定）。CO 4xに対しBTNは「T未満のカードを含むハンドをほぼ全部、AJoすら」フォールド。7xにはBTN/SB/BBがほぼ同じ対応（低SPRでポジションの価値が薄れる）。 https://blog.gtowizard.com/how-to-respond-to-large-preflop-raises-in-poker/ **注意: この記事は125bb・レーキありのキャッシュゲーム解析でありMTT/BBAではない**。→ ライブで3〜5xオープンが多い卓での方向性の参考 [GTO（キャッシュ）を方向性としてMTTに転用]。

---

## 2. ポストフロップのサイズ原則

### 2-1. Cベットサイズを決めるもの

- サイズの主要因は**ナッツアドバンテージとフォールドエクイティ**。 https://blog.gtowizard.com/the-mechanics-of-c-bet-sizing/
- Cベット戦略を最も動かすのは「ボードテクスチャよりプリフロップのレンジ構成」。 https://blog.gtowizard.com/flop-heuristics-ip-c-betting-in-mtts/

### 2-2. ボードテクスチャ別 — **ソース間で差あり**

| ボード | GTO Wizard（メカニクス記事）[GTO] | Upswing（一般則） |
|---|---|---|
| ドライ（GTO Wizardの例は Q♥Q♣6♦） | 小（概ね33%） | 小（25〜35%） |
| ウェット（例 K♥J♥7♦） | 大〜オーバーベット（75%と125%が主。オーバーベットは125%の方） | 大きめ（55〜80%） |
| 超ウェット（例 Q♦J♦T♦ モノトーン連結） | **小（33%）**：相手にナッツが多く（コールレンジの29.4%がストレート/フラッシュ）、自分のミドルハンドを守る必要 | （区別なし、「ウェット=大」） |

出典: https://blog.gtowizard.com/the-mechanics-of-c-bet-sizing/ ／ https://upswingpoker.com/bet-size-strategy-tips-rules/
- **注意: GTO Wizardのメカニクス記事の例はすべてキャッシュ100bb・BB vs BTNのシングルレイズポット**。MTT（40bb等）では数値が変わりうる。
- 補足（GTO Wizard MTTヒューリスティクス）: ペア/レインボーはベットしやすい、ストレートのある連結ボードはより二極化して大きめ、**ミドルカードのフロップがCベットに最悪**。モノトーンはチェックレイズリスクに言及。 https://blog.gtowizard.com/flop-heuristics-ip-c-betting-in-mtts/
- MTT 3ベットポットでは25%ポットの小さいCベットが多用される（深い時は50%も）[GTO]。 https://blog.gtowizard.com/mastering-three-bet-pots-in-position-in-mtts/ ／ Upswingも「3ベットポットは25〜40%」。 https://upswingpoker.com/bet-size-strategy-tips-rules/
- BB側: 「ほぼ全てのフロップでアグレッサーにチェック」。BTN 40bbのCベットに対するBBのドンクは平均2%程度。**相手のベットが大きいほどBBはフォールドが増え、レイズは減り、レイズサイズは小さくなる**。 https://blog.gtowizard.com/flop-heuristics-for-defending-the-blinds-in-mtts/

### 2-3. ターン・リバー

- ターンのダブルバレルは「66%ポット以上と大きめ」（Upswing一般則）。 https://upswingpoker.com/bet-size-strategy-tips-rules/
- リバーのベットレンジは**大きく二極化**（強いバリュー＋ブラフ、ミドルが少ない）。最強ハンドは基本的に最大サイズ、ただしブラフ候補が足りないと大サイズはナッツにしかコールされない。 https://blog.gtowizard.com/principles-of-river-play/
- バリューベットは「コールされたとき50%超勝てる」ことが条件。 https://blog.gtowizard.com/principles-of-river-play/ ／ Jonathan Littleも「悪いハンドに50%以上コールされる必要」。 https://jonathanlittlepoker.com/pdf/Strategies.pdf

### 2-4. オーバーベット

- ~~ナッツアドバンテージがあり二極化レンジを表す時に「少なくとも2倍ポット」級（Upswing）~~ → 訂正: Upswingの「at least 2x pot」は**リバーのチェックレイズのサイズ**（二極化レンジを表すため大きく）であり、オーバーベットの推奨ではない。 https://upswingpoker.com/bet-size-strategy-tips-rules/
- ウェットボード（K♥J♥7♦、キャッシュ100bb）では75%と125%（オーバーベット）が主なサイズ（GTO Wizard）。 https://blog.gtowizard.com/the-mechanics-of-c-bet-sizing/
- マルチウェイでは「大きなナッツアドバンテージがある時以外はオーバーベットしない」。 https://blog.gtowizard.com/10-tips-multiway-pots-in-poker/

### 2-5. ブロックベット

- OOPプレイヤーが**10%ポット程度**の小さいブロックベットを、よく構成されたレンジ（ブラフ・トップペア・ツーペア・セット）で使う例。 https://blog.gtowizard.com/principles-of-river-play/
- [EXP] アグレッシブな相手には約2.5BBの小さいブロックベットでブラフを誘う（Jonathan Little）。 https://jonathanlittlepoker.com/pdf/Strategies.pdf

### 2-6. SPR（スタック/ポット比）

- SPR = 有効スタック ÷ ポット。 https://blog.gtowizard.com/stack-to-pot-ratio/
- **SPR 1**: オールインコールに必要なエクイティは約33%。トップペア以上でスタックオフ可、フラッシュドローも多くがコール可。
- **SPR 2**: 必要エクイティ約40%（原文）。多くのフラッシュドローはコール可、OESDはバックドアFD付きならコール可。
- **SPR 約5**: 必要エクイティ約45%（=5/11、poker_math.pyで検算）。ナッツFDも微妙になり、**OESDは純粋なフォールド**。
- **SPR 16+**: トップペアでもコール/フォールドが無差別に近い。SPR4を超えるとワンペアでのスタックオフが危うくなる。（以上 https://blog.gtowizard.com/stack-to-pot-ratio/ ）
- MTTの3ベットポット（50bb）ではフロップSPRが3未満になり、**トップペアは強いハンド**。 https://blog.gtowizard.com/mastering-three-bet-pots-out-of-position-in-mtts/

---

## 3. 状況別アクション表

| 状況 | 基本方針 | 区分 | 出典 |
|---|---|---|---|
| BBでオープンを受ける（2〜2.3x） | 価格が良いので広く守る（必要エクイティ約19〜21%、レイト相手に40%以上ディフェンス） | GTO | https://upswingpoker.com/poker-tournament-tips-strategy-mtt/ https://upswingpoker.com/guide-big-blind-defense-mtts-modern-short-stack-play/ |
| BBで大きいオープン（4x〜7x）を受ける | ディフェンスを大幅に締める | GTO（キャッシュ125bbの解析を転用） | https://blog.gtowizard.com/how-to-respond-to-large-preflop-raises-in-poker/ |
| 〜30bbのショート | スーコネ・小ポケットを減らしハイカード寄りに（HJオープン31.22%→24.6%の例） | GTO | https://upswingpoker.com/open-raising-with-a-short-stack-tournaments/ |
| 10〜25bbで相手が広くオープン | 3ベットショーブ | GTO/EXP | https://redchippoker.com/mtt-secrets-3-bet-shoves/ |
| 10bb未満 | ショーブorフォールド中心。ショーブレンジは生エクイティとブロッカー重視（Axo＞スーテッド） | GTO | https://blog.gtowizard.com/playing-under-10bb-part-1-cev/ |
| マネーバブル（大人数MTT） | ICM圧力は**主にショートに**かかる。ショートは慎重、ビッグは中間スタックを攻める | GTO(ICM) | https://blog.gtowizard.com/money-bubble-vs-final-table-bubble/ https://blog.gtowizard.com/what-is-the-bubble-factor-in-poker-tournaments/ |
| ミドルスタック（**FT例**。マネーバブルの例ではない） | ファイナルテーブル例で中間スタック（29bb）のバブルファクターが最大1.93＝「ICMの棺桶」。ラダーを優先しビッグスタックとの衝突を避ける。参考：Sunday Million平均BFはマネーバブルで約1.6、FT前で約1.7 | GTO(ICM) | https://blog.gtowizard.com/what-is-the-bubble-factor-in-poker-tournaments/ |
| ビッグスタック | バブルファクター最小（同FT例のチップリーダー41bbで1.04〜1.11、ショートは1.28〜1.40）。中間スタックを狙い、他のビッグスタックとは避ける | GTO(ICM) | 同上 ＋ https://blog.gtowizard.com/money-bubble-vs-final-table-bubble/ |
| ファイナルテーブル・バブル | 逆転：**ショートが最もICM圧力が小さく**、ダブルアップを狙ってやや大胆に。ビッグはチップリーダー同士で最大の圧力 | GTO(ICM) | https://blog.gtowizard.com/money-bubble-vs-final-table-bubble/ |
| 小規模大会（例 200人）のマネーバブル | FTバブルに近い戦略になる（FT到達が現実的なため） | GTO(ICM) | 同上 |
| ICM下のポストフロップ | ソルバーは小さいサイズに寄る（「ダウンワード・ドリフト」）。カバーしている側がより攻撃的に | GTO(ICM) | https://blog.gtowizard.com/how-icm-impacts-postflop-strategy/ |
| ICMでのコール判断 | 必要エクイティ = BF/(BF+1)。例：BF1.18→54%。別例でchipEV 37.5%→ICM約47% | GTO(ICM) | https://blog.gtowizard.com/what-is-the-bubble-factor-in-poker-tournaments/ https://blog.gtowizard.com/icm-basics/ |
| バブルで周りが縮こまる（ライブ） | スチールと軽い3ベットを増やす（コーラーよりアグレッサー側に） | EXP | https://redchippoker.com/tournaments-4-mid-levels/ |
| PKO（プログレッシブ・ノックアウト） | バウンティで必要エクイティが下がる→カバーしている時は広くコール。ただし「ペイアウト/バブルは締め、バウンティは広げる」。カバー時のCベットは大きめ | GTO | https://blog.gtowizard.com/bringing-it-all-together-pko-review/ |
| PKO：BBジャムへのコール | 例：UTG+1（25bb）オープン→BB（12bb）の3ベットジャムへのコール率 classic 56.8% → PKO 88.4%（双方ミニマムバウンティ、フィールド残り75%） | GTO | https://blog.gtowizard.com/pko-versus-classic-responding-to-a-preflop-open/ |
| マルチウェイ | レンジベット禁止、ゴミは諦め、バリュー基準を上げる、小さめサイズ、ナッツ性重視、ポジションの価値増大 | GTO(近似) | https://blog.gtowizard.com/10-tips-multiway-pots-in-poker/ |

---

## 4. プレイヤー層別のエクスプロイト調整 [EXP]

**重要:** 以下は「母集団の傾向」に基づく推奨で、GTOではない。個々の相手を観察して当てはまる時だけ使う。

### 4-1. ライブ低〜中レートのトーナメント（海外ライブMTTのサテ/デイリー含む）

- 序盤のレク層は「ポストフロップで粘着的」、深いスタックで**トップペアでスタックオフしすぎ**、序盤に巨大レイズやリンプでマルチウェイを作る。→ 序盤はブラフを控えバリュー重視、スペキュレーティブハンドでシングルレイズポットに入る。 https://redchippoker.com/tournaments-3-early-levels/
- ルース・パッシブ相手: 良いトップペア以上ならほぼ常にバリューベット継続、相手が圧力をかけてきたらプレミアム以外降りる。コーリングステーションへの薄いリバーバリューは約25%ポット。 https://jonathanlittlepoker.com/pdf/Strategies.pdf （PDFの発行年は未確認【要確認】）
- タイト・パッシブ相手: レイトから広くスチール、フロップCベットで降ろす。 同上

### 4-2. 「リバーでブラフが少ない」傾向 — **ソースにより見解差あり**

- 国内アミューズメント: 「ブラフが極端に少なく、特にリバーの大きなベットはほとんどバリュー」→大きなベット/レイズには微妙なハンドを降りる。 https://pokeracademy.jp/amuse-how-to-win/
- Phil Galfond: $2/$5のライブ例で、アンダーブラフの傾向に対して**周りが過剰フォールドする適応**が起こり、今度はリバーブラフが効く局面が生まれうると指摘（傾向は連鎖する）。 https://www.philgalfond.com/articles/how-understanding-your-player-pool-can-boost-your-winrate
- GTO Wizard（低レート・マスデータ）: 特定ライン（ターンプローブ、範囲ベット後のベット-チェック-ベット）は**むしろオーバーブラフ**。例：J♠6♠5♣T♥でのBBターンプローブ範囲の約56%がメイドしていないハンド。ただし記事自体が「データ不足」と明記し、オンライン低レート由来と思われる（ライブ適用は【要確認】）。 https://blog.gtowizard.com/calling-down-the-over-bluffed-lines-in-lower-limits/
- 落とし所: **「リバーの大きいベット/レイズ」はライブ/アミューズで降り寄り、「ターンのプローブ」等の一部ラインは低レートでもブラフ過多のことがある**。全ラインで一律に「ブラフがない」と決めつけない。

### 4-3. 国内アミューズメント / ホームゲーム

- 傾向: プリフロップでコール・リンプが多い、ポストフロップで弱いハンドでもコールし続ける、ブラフが極端に少ない。対策: タイトにレイズ、強いハンドは大きめにバリューベット、ブラフ削減、大きいベットには降りる。 https://pokeracademy.jp/amuse-how-to-win/
- 初心者の典型ミス: AK/AQをコールしすぎ、強いハンドでスロープレイ、ベット額をポット比ではなくチップの絶対額で判断。 https://note.com/jolly_ixia10/n/n53b6300e0d77 （個人note、母集団データではなく経験則）
- リンパーが多い卓はアイソレーションを大きめに（Upswingのキャッシュ用目安：ライブ4BB+1BB/リンパー）。 https://upswingpoker.com/vs-multiple-limpers/
- アミューズメントのトーナメントはストラクチャーが速い（スタックが浅い・レベルが短い）ことが多いと思われるが、一般的データは確認できず【要確認】。速い構造ほど1-6のショート戦略の比重が上がる。

### 4-4. オンライン / アプリ

- 法律の注意: 日本居住者が日本からリアルマネーのオンラインポーカーに参加することは違法になりうる（`04-japan-and-overseas.md` 1章）。ここでの戦略は、換金のない国内アプリや海外渡航中など合法な場での利用を前提とする。

- 対戦相手のレベルが比較的高い/HUD等がありうる環境ではGTO基準（2〜2.3xオープン、3ベットIP約3x/OOP約4x、ドライボード小Cベット）を土台に。上記ソースの数値は主にオンラインMTTソリューション由来。 https://blog.gtowizard.com/how-stack-sizes-change-your-range/
- アプリ/国内オンラインの母集団傾向を示す信頼できるデータは見つからず【要確認】。

---

## 5. 初心者が最初に覚える10原則

1. **[GTO] オープンは小さく（2〜2.5x）、浅くなるほど小さく。** 100bb 2.3x → 50bb 2.1x → 20bbでほぼミニレイズ。 https://blog.gtowizard.com/how-stack-sizes-change-your-range/ https://pokercoaching.com/blog/preflop-strategy-guide-the-ultimate-guide-to-preflop-bet-sizing/
2. **[一般則/GTO近似] 3ベットはIPで約3倍、OOPで約4倍。** https://upswingpoker.com/bet-size-strategy-tips-rules/
3. **[GTO] BBは安く参加できるので広く守る（2.25x・BBA構造で約21%のエクイティでOK）。ただし大きいオープンには締める。** https://upswingpoker.com/poker-tournament-tips-strategy-mtt/ https://blog.gtowizard.com/how-to-respond-to-large-preflop-raises-in-poker/
4. **[GTO/EXP] 10〜25bbは3ベットショーブ、10bb未満（ファーストイン）はショーブorフォールドが主役。** https://redchippoker.com/mtt-secrets-3-bet-shoves/ https://blog.gtowizard.com/playing-under-10bb-part-1-cev/
5. **[GTO（キャッシュ100bb例）] ドライボードは小さく（25〜35%）、ダイナミックなボードは大きく。ただし超ウェット（モノトーン連結）は小さく。** https://upswingpoker.com/bet-size-strategy-tips-rules/ https://blog.gtowizard.com/the-mechanics-of-c-bet-sizing/
6. **[GTO] SPRを見る：SPRが低いほどトップペアでスタックオフOK、SPR4超ではワンペアは慎重に。** https://blog.gtowizard.com/stack-to-pot-ratio/
7. **[GTO近似] マルチウェイではブラフを減らし、バリューの基準を上げ、小さめに打つ。** https://blog.gtowizard.com/10-tips-multiway-pots-in-poker/
8. **[GTO(ICM)] マネーバブルではショートが最も慎重に（ミドルもFT付近では「ICMの棺桶」）、ビッグスタックはミドルを攻める。FTバブルでは逆にショートが大胆に。** https://blog.gtowizard.com/money-bubble-vs-final-table-bubble/ https://blog.gtowizard.com/what-is-the-bubble-factor-in-poker-tournaments/
9. **[GTO原則＋EXP] バリューベットは「コールされたら50%超勝てる」時に。[EXP] コーリングステーションには強いハンドは大きめ、薄いバリューは小さめ（JL：約25%ポット）でベットし、ブラフは減らす。** https://blog.gtowizard.com/principles-of-river-play/ https://pokeracademy.jp/amuse-how-to-win/
10. **[EXP] ライブ/アミューズのリバーの大きなベット・レイズは強い傾向 → 微妙なハンドは降りてよい（ただし母集団傾向であり絶対ではない）。** https://pokeracademy.jp/amuse-how-to-win/ https://www.philgalfond.com/articles/how-understanding-your-player-pool-can-boost-your-winrate

---

## 6. ソース間の主な相違点まとめ

| 論点 | A | B |
|---|---|---|
| 序盤ライブのオープンサイズ | ソルバー: 2.1〜2.3x（GTO Wizard） | Red Chip: 80bb+で約3x、以下2.5x |
| プッシュ/フォールド開始 | Upswing: 約15bb以下（13〜15bbでナッシュ） | GTO Wizard: 14bbでショーブとリンプが加わる（レイズも残る）、9bb以下でミニレイズ→ショーブ。Upswing 2026更新も「MTTはミニレイズ寄り」 |
| ウェットボードのCベット | Upswing: 55〜80% | GTO Wizard（キャッシュ100bb）: ウェット75%/125%、ただし超ウェットは33% |
| 低レートのブラフ頻度 | 国内アミューズ記事: リバーのブラフ極少 | GTO Wizard: 一部ライン（ターンプローブ等）はオーバーブラフ／Galfond: アンダーブラフ→過剰フォールドの連鎖 |
| 3ベットサイズ | 一般則 IP3x/OOP4x | ソルバー例 IP約3.2x（6.82/2.1）、OOP約3.9〜4.3x（8.2/2.1、9.8/2.3）（概ね一致） |

---

## 出典

- GTO Wizard — How Stack Sizes Change Your Range: https://blog.gtowizard.com/how-stack-sizes-change-your-range/
- GTO Wizard — Mastering Three-Bet Pots Out of Position in MTTs: https://blog.gtowizard.com/mastering-three-bet-pots-out-of-position-in-mtts/
- GTO Wizard — Mastering Three-Bet Pots In Position in MTTs: https://blog.gtowizard.com/mastering-three-bet-pots-in-position-in-mtts/
- GTO Wizard — Flop Heuristics for Defending the Blinds in MTTs: https://blog.gtowizard.com/flop-heuristics-for-defending-the-blinds-in-mtts/
- GTO Wizard — Flop Heuristics: IP C-Betting in MTTs: https://blog.gtowizard.com/flop-heuristics-ip-c-betting-in-mtts/
- GTO Wizard — The Mechanics of C-Bet Sizing: https://blog.gtowizard.com/the-mechanics-of-c-bet-sizing/
- GTO Wizard — Principles of River Play: https://blog.gtowizard.com/principles-of-river-play/
- GTO Wizard — Stack-to-pot ratio: https://blog.gtowizard.com/stack-to-pot-ratio/
- GTO Wizard — Playing Under 10bb (Part 1): https://blog.gtowizard.com/playing-under-10bb-part-1-cev/
- GTO Wizard — How To Respond to Large Preflop Raises: https://blog.gtowizard.com/how-to-respond-to-large-preflop-raises-in-poker/
- GTO Wizard — What is the Bubble Factor: https://blog.gtowizard.com/what-is-the-bubble-factor-in-poker-tournaments/
- GTO Wizard — ICM Basics: https://blog.gtowizard.com/icm-basics/
- GTO Wizard — Money Bubble vs Final Table Bubble: https://blog.gtowizard.com/money-bubble-vs-final-table-bubble/
- GTO Wizard — How ICM Impacts Postflop Strategy: https://blog.gtowizard.com/how-icm-impacts-postflop-strategy/
- GTO Wizard — Bringing It All Together: PKO Review: https://blog.gtowizard.com/bringing-it-all-together-pko-review/
- GTO Wizard — PKO Versus Classic: Responding to a Preflop Open: https://blog.gtowizard.com/pko-versus-classic-responding-to-a-preflop-open/
- GTO Wizard — 10 Tips for Multiway Pots: https://blog.gtowizard.com/10-tips-multiway-pots-in-poker/
- GTO Wizard — Calling Down Over-Bluffed Lines in Lower Limits: https://blog.gtowizard.com/calling-down-the-over-bluffed-lines-in-lower-limits/
- Upswing Poker — 7 Poker Tournament Tips: https://upswingpoker.com/poker-tournament-tips-strategy-mtt/
- Upswing Poker — Open-Raising with a Short Stack: https://upswingpoker.com/open-raising-with-a-short-stack-tournaments/
- Upswing Poker — Bet Sizing Strategy: 8 Rules: https://upswingpoker.com/bet-size-strategy-tips-rules/
- Upswing Poker — 4-Bet Size Strategy: https://upswingpoker.com/4-bet-size-strategy/
- Upswing Poker — Ultimate Guide to Big Blind Defense (MTT short stack): https://upswingpoker.com/guide-big-blind-defense-mtts-modern-short-stack-play/
- Upswing Poker — Push Fold Charts: https://upswingpoker.com/push-fold-tournament-strategy-charts/
- Upswing Poker — vs Multiple Limpers: https://upswingpoker.com/vs-multiple-limpers/
- PokerCoaching (Jonathan Little) — Ultimate Guide to Preflop Bet Sizing: https://pokercoaching.com/blog/preflop-strategy-guide-the-ultimate-guide-to-preflop-bet-sizing/
- Jonathan Little — Strategies for Beating Small Stakes Poker Tournaments (PDF): https://jonathanlittlepoker.com/pdf/Strategies.pdf
- Red Chip Poker — Tournaments #3: Early Levels: https://redchippoker.com/tournaments-3-early-levels/
- Red Chip Poker — Tournaments #4: Mid Levels and the Bubble: https://redchippoker.com/tournaments-4-mid-levels/
- Red Chip Poker — MTT Secrets: 3-Bet Shoves: https://redchippoker.com/mtt-secrets-3-bet-shoves/
- Phil Galfond — How Understanding Your Player Pool Can Boost Your Winrate: https://www.philgalfond.com/articles/how-understanding-your-player-pool-can-boost-your-winrate
- PokerNews — Big Blind Antes: Do the Pros Outweigh the Cons? (2018): https://www.pokernews.com/news/2018/01/big-blind-antes-pros-cons-29848.htm
- Wikipedia — 2026 World Series of Poker: https://en.wikipedia.org/wiki/2026_World_Series_of_Poker
- ポーカーアカデミー — アミューズメントカジノでの勝ち方: https://pokeracademy.jp/amuse-how-to-win/
- note（でぶみ）— ポーカー初心者の傾向: https://note.com/jolly_ixia10/n/n53b6300e0d77

### 調査メモ（未使用・未検証）
- Run It Once、ICMIZER、HoldemResources(HRC)の記事は今回の調査で具体数値を引用できる形で確認できず【要確認】。YouTube動画は内容検証できなかったため引用していない。

---

## ファクトチェック記録（2026-10-05）

方法: 各引用URLをWebFetchで再取得し、数値と前提（スタック深さ・アンティ構造・キャッシュ/MTT・GTO/EXP）を照合。計算は `tools/poker_math.py pot-odds` で検算。WebFetchはモデル要約経由のため、✅でも細部は原典確認が望ましい。

| # | 主張 | 判定 | 対応 |
|---|---|---|---|
| 1 | 100bb 2.3x → 50bb 2.1x（GTO Wizard スタック深さ） | ✅ | UTG・chipEV MTT と明記 |
| 2 | 20bbほぼミニレイズ・「もっと小さくしたい」 | ✅ | 原文引用に差し替え |
| 3 | 14bb以下「ショーブorリンプ中心」 | ⚠️ | 14bbでショーブとリンプ4.6%が「加わる」。8/5bbがショーブ/フォールドのみ、に修正 |
| 4 | 9bb以下でミニレイズ→ショーブ、AAも7bb以下ショーブ、7bb BBで96sコール、Axo優先 | ✅ | アンティ0.125bb/人（BBAではない）を追記 |
| 5 | 40bb BTN/UTG vs BB 2.3x | ⚠️ | BTN vs BB 2.3xのみ確認。UTGは削除 |
| 6 | 3ベット 50bb BTN 6.82 vs CO 2.1／BB 9.8 vs CO 2.3／30bb BB 8.2 vs 2.1 | ✅ | 倍率を検算（3.25/4.26/3.90） |
| 7 | Upswing・PokerCoaching IP3x/OOP4x、オープン2〜2.5BB | ✅ | — |
| 8 | Jonathan Little「2.5BB→7〜8BB」 | ❓ | PDF内で該当例を確認できず【要確認】。実在例（2BB→5BB→11.5BB）を併記 |
| 9 | Red Chip「80bb+で約3x」 | ⚠️ | 3xは「序盤ディープ」でbb数の明記なし。「80bb未満で2.5x」は✅。修正 |
| 10 | Red Chip 3ベットショーブ10〜25bb、IP10x/OOP12x、BBAで初期ポット2.5bb | ✅ | — |
| 11 | Red Chip キャッシュ3ベット3.5x/4.5x、浅いほど小さく | ✅ | — |
| 12 | Upswing 4ベット 60bb+ IP2.2x/OOP2.6〜2.8x、50bb混合、30bb以下オールイン | ✅ | — |
| 13 | Upswing push/fold 約15bb以下・2026更新「MTTはミニレイズ寄り」 | ✅ | — |
| 14 | Upswing 13〜15bbナッシュ、HJ 31.22%→24.6% | ✅ | — |
| 15 | Upswing 2.25BBオープン、BB 20.8%、レイトに40%以上防衛 | ✅ | BBアンティ400を追記。500/(1900+500)=20.8%を検算 |
| 16 | 19bb例 18.9%・46.4%・16.1%+29.3%=45.4% | ⚠️ | 原文の値どおりだが原文の式に不整合（1,600/8,640=18.5%）。注記 |
| 17 | 大きいオープン：7xで「T未満ほぼ全フォールド」 | ❌ | 実際は**CO 4xに対するBTN**の記述（AJoすらフォールド）。記事は**キャッシュ125bb・レーキあり**。修正・ラベル変更 |
| 18 | Cベット主要因＝ナッツアドバンテージとフォールドエクイティ | ✅ | — |
| 19 | ドライ例 7♥2♦2♣ 33% | ❌ | 原文のドライ例は**Q♥Q♣6♦**。全例がキャッシュ100bb BvB(BTN) SRPと注記 |
| 20 | ウェット75〜125%「オーバーベット」 | ⚠️ | オーバーベットは125%のみ。2-2・2-4を修正 |
| 21 | 超ウェットQJT 33% | ✅ | 相手ナッツ29.4%を追記 |
| 22 | Upswing ドライ25〜35%/ウェット55〜80%/3BP 25〜40%/ターン66%+ | ✅ | — |
| 23 | Upswing オーバーベット「少なくとも2倍ポット」 | ❌ | 原文は**リバーのチェックレイズ**サイズ。訂正 |
| 24 | MTT IPCベット：プリフロップレンジ＞テクスチャ、ミドル/連結/モノトーンが難しい | ✅ | — |
| 25 | BBドンク平均2%、ベットが大きいほどBBは降り・レイズ減・レイズ小 | ✅ | — |
| 26 | 3BPで25%Cベット、SPR<3でトップペア強い | ✅ | — |
| 27 | リバー二極化・バリュー>50%・OOP 10%ブロック | ✅ | — |
| 28 | SPR1=33%、SPR約5=40% | ❌ | 原文の40%は**SPR2**。SPR5は約45%（5/11）。OESDはSPR5で純フォールド。修正 |
| 29 | SPR16でトップペア無差別、SPR4超でワンペア危うい | ✅ | — |
| 30 | マルチウェイ10 tips（レンジベット禁止・小さめ・オーバーベットはナッツ優位時のみ等） | ✅ | — |
| 31 | マネーバブルはショートに圧力、FTバブルは逆、200人大会はFTバブル的 | ✅ | — |
| 32 | バブルファクター ミドル最大1.93・ビッグ1.04〜1.11（バブル付近） | ⚠️ | 数値は✅だが**ファイナルテーブルの例**。マネーバブル平均約1.6を併記し文脈修正 |
| 33 | BF/(BF+1)、BF1.18→54%、37.5%→約47% | ✅ | 検算 54.1% |
| 34 | ICMダウンワード・ドリフト、カバー側が攻撃的 | ✅ | — |
| 35 | PKO：バウンティで必要エクイティ低下、「ペイアウト/バブルは締め、バウンティは広げる」、カバー時Cベット大きめ | ✅ | — |
| 36 | PKO UTG+1のBBジャムコール 57%→約90% | ✅ | 正確値56.8%→88.4%と前提（25bb vs 12bb、残り75%）を追記 |
| 37 | 低レート オーバーブラフライン、J♠6♠5♣T♥で約56%非メイド、データ不足明記 | ✅ | — |
| 38 | JL：ルースパッシブへの継続バリュー、圧力にはプレミアム以外降り、薄いバリュー約25% | ✅ | — |
| 39 | JL：バブルでスチール増 | ❌ | PDF内で確認できず。バブル行からJL出典を削除 |
| 40 | JL：アグレッシブ相手に約2.5BBの小さいブロックベット、バリュー50% | ✅ | PDF発行年は引き続き【要確認】 |
| 41 | Upswing アイソレーション 3BB/4BB＋1BB/リンパー（キャッシュ向け） | ⚠️ | 数値✅、記事は形式を明記せず。表現修正 |
| 42 | ポーカーアカデミー（アミューズ傾向）、note（初心者ミス3点） | ✅ | — |
| 43 | Galfond $2/$5 アンダーブラフ→過剰フォールドの適応 | ✅ | — |
| 44 | BBA：ARIA 2017年、WSOPサーキット/2018夏ハイローラー全イベント、WPT等 | ✅ | — |
| 45 | 2026 WSOP 5/26〜7/15、ME FTは8月に延期 | ✅ | — |
| 46 | 10原則 | ⚠️ | 各原則に[GTO]/[EXP]ラベルを付与。原則8（ミドルの文脈）・原則9（「薄く・大きく」の矛盾）を修正 |
| 47 | アミューズのストラクチャーが速い、2026各ツアーのBBA採用状況、アプリ母集団傾向 | ❓ | 【要確認】のまま |
