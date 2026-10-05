# ノーリミット・テキサスホールデム 用語・ルール リファレンス（初級〜中級 / MTT向け）

- 作成日: 2026-10-05
- 対象: 海外トーナメント（MTT）でのインマネ（入賞）を目指す日本語学習者
- 表記: 日本語本文（英語表記）。出典番号 [S#] は末尾「出典」リストに対応。
- 【要確認】= 一次情報で裏付けを取れなかった、または店舗・サイトにより運用が異なる項目。

---

## 1. ルール基礎

### 1.1 ゲームの流れ（Texas Hold'em）
- 各プレイヤーに2枚の手札（ホールカード / hole cards）。共通カード（コミュニティカード / board）は最大5枚。[S1]
- ベッティングラウンドは4回: **プリフロップ（preflop）→ フロップ（flop, 3枚）→ ターン（turn, 1枚）→ リバー（river, 1枚）**。[S1]
- 各ストリートの前にディーラーは1枚バーン（burn）する。[S1]
- 手役は「自分の2枚＋ボード5枚」の計7枚から**最良の5枚**で作る。手札を2枚・1枚・0枚のどれを使ってもよい（0枚＝ボードをそのまま使う「プレイ・ザ・ボード / playing the board」）。[S1]
- アクション順:
  - プリフロップ: BBの左隣（UTG）から時計回り。[S1]
  - フロップ以降: ボタンの左隣（残っている中で最初の人、通常SB）から時計回り。[S1]
  - ヘッズアップ（2人）: ボタンがSBを払い、**プリフロップは先に、フロップ以降は最後に**アクションする。[S1]
- ノーリミットの最小レイズ: 「そのラウンドで直前に行われた最大の“フル”ベット/レイズ額以上」上乗せする必要がある（TDA Rule 45）。[S2]
  - 例: BB=200、UTGが600にレイズ（上乗せ400）→ 次のレイズは最低 600+400=**1,000**。
- トーナメントは**デッドボタン（dead button）**方式（TDA Rule 34）。[S2]
- ショーダウン: オールインが発生し他の全員のアクションが完了したら全ハンドを即オープン（TDA Rule 17）。オールインでない場合、最終ラウンドで最後にアグレッシブなアクションをした人が先に見せる（Rule 18-A）。[S2]

### 1.2 ハンドランキング（強い順）[S3]
| 順位 | 日本語 | 英語 | 例 |
|---|---|---|---|
| 1 | ストレートフラッシュ（最強はロイヤルフラッシュ） | Straight Flush (Royal Flush) | A♠K♠Q♠J♠T♠ |
| 2 | フォーカード（クアッズ） | Four of a Kind (Quads) | 9♣9♦9♥9♠K♦ |
| 3 | フルハウス | Full House | Q♣Q♦Q♥7♠7♦ |
| 4 | フラッシュ | Flush | A♥J♥8♥4♥2♥ |
| 5 | ストレート | Straight | 8♣7♦6♥5♠4♦ |
| 6 | スリーカード（セット/トリップス） | Three of a Kind | 6♣6♦6♥A♠T♦ |
| 7 | ツーペア | Two Pair | K♣K♦5♥5♠9♦ |
| 8 | ワンペア | One Pair | J♣J♦A♥8♠3♦ |
| 9 | ハイカード（ノーペア） | High Card | A♣Q♦9♥6♠3♦ |

補足:
- ロイヤルフラッシュは独立した役ではなく「Aハイのストレートフラッシュ」。[S3]
- **スート（マーク）に強弱はない**。スートだけが違うハンドは同じ強さ＝チョップ（引き分け）。[S3]
- 同じ役同士はランク→キッカー（kicker）の順で比較。例: A♠K♦ vs A♥Q♣、ボード A♦9♣7♥4♠2♦ → 両者Aのワンペア、キッカーK > Q でA♠K♦の勝ち。[S3]
- A は最強カードだが、A-2-3-4-5（ホイール / wheel）の最下位ストレートにも使える。Q-K-A-2-3 のような「回り込み」はストレートではない。[S3]

### 1.3 ブラインドとアンティ
- **スモールブラインド（SB）/ビッグブラインド（BB）**: ボタンの左1つ目・2つ目が強制的に置くベット。[S1]
- **アンティ（ante）**: 全員（または代表者）が払う追加の強制ベット。ポットを大きくしアクションを促す。
- **ビッグブラインド・アンティ（BBA / Big Blind Ante）**: BBのプレイヤーがテーブル全員分のアンティをまとめて払う方式。手間が減り進行が速い。[S4]
  - 現代の主要トーナメントでは BBA が主流で、**BBA額 = BB額**が一般的（例: 1,000/2,000 のレベルで BB は 2,000 + BBA 2,000）。[S5]（金額は大会のストラクチャー表で必ず確認）
  - Poker TDA 2026年版（Version 1.0, 2026-09-07）推奨手順 RP-11: 単独支払い型アンティを使う場合は「**big-blind-first calculation（BB優先計算）の BBA** を推奨」。アンティは（FT含め）大会途中で減額すべきでない。[S2]
    - TDA本文は "big-blind-first" の詳細な定義を載せていないが、一般的な解釈は「BBのスタックが BB＋アンティに足りない場合、まずBBに充て、残りをアンティに充てる」。Card Player [S5] によれば2019年TDAサミット時点では約9割のカードルームが逆の「アンティ優先」だったため、**会場によって運用が異なり得る。ローカルルールが優先されるので大会ごとに確認**。【要確認：各大会の運用】
  - TDA Rule 22: BBAの大会で入賞圏内に同時に2人以上飛んだ場合、「アンティを払った後の開始スタック」が大きい方が上位。[S2]
- 戦略上の意味: BBAでは最初からポットが SB+BB+アンティ = 2.5BB（BBA=1BBの場合）あり、ブラインドスチールの価値が上がる。（計算: 0.5+1+1=2.5BB）

### 1.4 ポジション
アクションが後ろ（ボタンに近い）ほど相手の行動を見てから判断でき有利。

**9-max（9人卓）プリフロップのアクション順** [S6]
| 順 | 略称 | 名称 |
|---|---|---|
| 1 | UTG | アンダー・ザ・ガン（Under the Gun） |
| 2 | UTG+1 | — |
| 3 | UTG+2 | — |
| 4 | LJ | ロージャック（Lojack） |
| 5 | HJ | ハイジャック（Hijack） |
| 6 | CO | カットオフ（Cutoff）※ボタンの右隣 [S7] |
| 7 | BTN | ボタン（Button / Dealer） |
| 8 | SB | スモールブラインド |
| 9 | BB | ビッグブラインド |

- **8-max**（オンラインMTTに多い）: UTG, UTG+1, LJ, HJ, CO, BTN, SB, BB（9-maxからUTG+2が抜ける）。[S6]
- **6-max**: 一般に LJ（UTGと呼ぶ場合も）, HJ, CO, BTN, SB, BB。6-maxの最初の席を「UTG」と呼ぶか「LJ」と呼ぶかはツール・サイトにより異なる。【要確認：表記ゆれ】
- 大まかな区分: アーリー（EP: UTG〜UTG+2）、ミドル（MP: LJ, HJ）、レイト（LP: CO, BTN）、ブラインド（SB, BB）。
- **IP（インポジション / in position）**: ポストフロップで相手より後に行動できる。**OOP（アウトオブポジション）**: 先に行動しなければならない。

---

## 2. 必須用語（カテゴリ別）

### 2.1 アクション（Action）
| 用語 | 定義 | 例 |
|---|---|---|
| チェック（check） | ベットがない状況でベットせず手番を回す | — |
| ベット（bet） | そのラウンドで最初にチップを出す | — |
| コール（call） | 直前のベット/レイズと同額を出す | — |
| レイズ（raise） | ベット額を上乗せする。最小額は直前のフル上乗せ額以上 [S2] | BB200で600→次は最低1,000 |
| フォールド（fold） | 手を降りる | — |
| オールイン（all-in / shove / jam） | 持ちチップを全て賭ける [S8] | 「10BBでジャム」 |
| オープン（open / open-raise） | プリフロップで最初に参加する人のレイズ | CO open 2.2BB |
| リンプ（limp） | プリフロップでレイズせずBBにコールして参加 [S7] | — |
| オーバーリンプ（over-limp） | 先行リンパーの後ろからさらにリンプ | — |
| アイソレーション（iso-raise / isolate） | リンパー（またはBB）とヘッズアップになる目的でレイズ [S9] | UTGリンプ→COがアイソ |
| 3ベット（3-bet） | オープンへのリレイズ（ブラインドを1ベット目と数える）[S7] | — |
| 4ベット / 5ベット | 3ベットへのリレイズ / さらにそのリレイズ [S7] | — |
| コールドコール（cold call） | 自分はまだチップを入れていない状態で、レイズ（複数のベット分）にコール [S7] | BTNがCOのオープンにコール |
| フラット（flat call） | レイズせずにコールで受ける（俗語） | — |
| スクイーズ（squeeze） | オープン＋1人以上のコーラーがいる状況での3ベット [S10] | UTG open, HJ call → BTN 3bet |
| チェックレイズ（check-raise） | 先にチェックし、相手のベットにレイズ [S7] | — |
| ドンクベット（donk bet / lead） | 前ラウンドの主導権がないOOPのプレイヤーが先頭でベット [S7] | BBコール後、フロップでBBがベット |
| コンティニュエーションベット（c-bet / Cベット） | 前のラウンドで主導権を持ったプレイヤーが続けてベット [S7] | プリフロップレイザーがフロップでベット |
| ディレイドCベット（delayed c-bet） | プリフロップのアグレッサーが、前のストリート（通常フロップ）をチェックで回した後にベットすること [S27] | プリフロップレイザーがフロップをチェック→ターンでベット |
| プローブベット（probe bet） | 前ストリートでプリフロップのアグレッサー（IP）がCベットせずチェックした後、OOP側が先にベットすること。ターンかリバーでのみ起こる [S28] | BBコール→フロップ両者チェック→ターンでBBがベット |
| ブロックベット（block bet） | OOPのプレイヤーが小さめ（ポットの20〜40%）にベットし、相手の大きいベットを防ぐ [S11] | — |
| オーバーベット（overbet） | ポットより大きいベット [S7] | ポット100に150ベット |
| フロート（float） | 弱い手で（主にIPで）フロップのベットにコールし、後のストリートでブラフするかショーダウンで勝つ狙い [S29] | 相手のCベットにコール→ターンで相手がチェック→ベットして奪う |
| ストラドル（straddle） | 主にUTGが任意で置く追加ブラインド（通常2BB）。キャッシュゲームで見られる [S7] | — |
| ミニマムレイズ / ミニレイズ（min-raise） | 最小額のレイズ。MTTのオープンで2BBなど | — |

### 2.2 ポジション（Position）
| 用語 | 定義 |
|---|---|
| ボタン（BTN / dealer button） | ディーラー位置を示すマーカー、またはその席。ポストフロップで最後に行動 [S7] |
| カットオフ（CO） | ボタンの右隣 [S7] |
| ハイジャック（HJ） | COの右隣（ボタンの2つ右）[S7] |
| ロージャック（LJ） | HJの右隣（9-maxでは4番目にアクション）[S6] |
| UTG | BBの左隣、プリフロップで最初に行動 [S7] |
| ブラインド（SB / BB） | 強制ベットを払う2席 |
| IP / OOP | 相手より後に行動 / 先に行動 |
| エフェクティブスタック（effective stack） | 関与するプレイヤー間で最も小さいスタック。失う/得る最大額を決める [S7][S12] |

### 2.3 ボード / ハンド（Board & Hands）
| 用語 | 定義 | 例 |
|---|---|---|
| ホールカード（hole cards） | 自分だけの2枚 | — |
| スーテッド / オフスート（suited / offsuit） | 2枚が同スート（s）/ 異なるスート（o） | AKs, AKo |
| ポケットペア（pocket pair） | 手札がペア | 77 |
| コンボ（combo） | 具体的なカード組合せ数。ペア6通り、スーテッド4通り、オフスート12通り、全1,326通り（自己計算: C(52,2)=1,326） | AK = 16コンボ |
| ナッツ（nuts） | その時点で可能な最強ハンド [S7] | — |
| キッカー（kicker） | 同じ役同士の勝敗を決める残りのカード [S7] | — |
| セット（set） | ポケットペア＋ボード1枚のスリーカード [S7] | 77 on 7-K-2 |
| トリップス（trips） | ボードのペア＋手札1枚のスリーカード [S7] | A7 on 7-7-2 |
| トップペア / オーバーペア | ボード最高位と同じペア / ボード全てより高いポケットペア | — |
| ドロー（draw） | 完成すれば強い役になる未完成ハンド | — |
| フラッシュドロー（flush draw） | 同スート4枚。アウツ9枚 | — |
| オープンエンド（OESD / open-ended） | 両側どちらでも完成する連続4枚。アウツ8枚 [S7] | 9-8 on 7-6-2 |
| ガットショット（gutshot） | 中抜けストレートドロー。アウツ4枚 [S7] | 9-8 on J-7-2（T待ち） |
| バックドア（backdoor） | ターン・リバー両方で必要カードが来て完成するドロー [S7] | — |
| アウツ（outs） | 来れば自分が勝つ（と見込む）残りカード | — |
| レインボー（rainbow） | 全て異なるスートのフロップ [S7] | K♠8♦3♣ |
| モノトーン（monotone） | 3枚同スートのフロップ | — |
| ツートーン（two-tone） | 2枚同スートのフロップ（フラッシュドローあり） | — |
| ペアボード（paired board） | ボードにペアがある | — |
| ドライ / ウェット（dry / wet） | ドローが少ない / 多いボード | K-7-2r はドライ |
| ブラフキャッチャー（bluff catcher） | 相手のブラフにしか勝てないが、ブラフには勝てる手 | — |
| ショーダウン（showdown） | 最終的に手を見せて勝敗を決める | — |
| チョップ（chop / split pot） | 同じ強さでポットを分ける | — |

### 2.4 数学（Math）
| 用語 | 定義 | 出典 |
|---|---|---|
| ポットオッズ（pot odds） | コール額 ÷（コール後の合計ポット）。必要勝率と比較する | [S13] |
| エクイティ（equity） | ショーダウンまで行った場合にポットのうち自分の取り分（勝率）| [S8] |
| EV（期待値 / expected value） | ある行動を何度も繰り返した時の平均損益 | 一般概念 |
| インプライドオッズ（implied odds） | 将来のストリートで追加で得られる見込みのチップも考慮したオッズ [S13] | [S13] |
| リバースインプライドオッズ（reverse implied odds） | コール後、将来のストリートで失う可能性のある額（完成しても負けている・2番手の手で払い続ける等）。インプライドオッズの逆 [S30] | [S30] |
| フォールドエクイティ（fold equity） | ベットで相手を降ろすことで平均的に得るポットの取り分 [S7] | [S7] |
| SPR（stack-to-pot ratio） | エフェクティブスタック ÷ ポット。例: ポット10、スタック100 → SPR 10 [S12] | [S12][S14] |
| MDF（最小防御頻度 / minimum defense frequency） | 相手のブラフを損益ゼロにするために継続（コール/レイズ）すべき最低頻度 = ポット ÷（ポット＋ベット）[S15] | [S15] |
| アルファ（alpha / α） | ブラフが損益ゼロになるために必要な相手のフォールド率 = ベット ÷（ポット＋ベット）= 1 − MDF [S15] | [S15] |
| エクイティリアライゼーション（equity realization / EQR） | 生のエクイティのうち実際に回収できる割合。EV = エクイティ × EQR × ポット。100%超は過剰実現、未満は過少実現。OOPでは全般に低い [S31] | [S31] |
| コンビナトリクス（combinatorics） | コンボ数を数えて相手レンジを見積もる手法 | [S16] |
| ブロッカー（blocker / card removal） | 自分の手札が相手レンジの一部を物理的に消す効果 [S16] | A♠K♦ on T♠6♠3♠ → 相手のナッツフラッシュをブロック |

### 2.5 戦略（Strategy）
| 用語 | 定義 |
|---|---|
| レンジ（range） | ある状況で相手（自分）が持ち得るハンドの集合 |
| ポラライズド（polarized） | 強い手と弱い手（ブラフ）中心で中間がない構成。大きめのベットで使われやすい [S17] |
| リニア（linear） | 上から順に強い手〜中程度の手 [S17] |
| マージド（merged） | 強い手・中程度・弱い手が混在した構成 [S17] |
| コンデンスド（condensed） | 中程度の手が多く、ナッツ級や完全なエアが少ない構成 [S17] |
| キャップド（capped） | 最強クラスの手を含まない（前の行動で否定された）レンジ | 
| レンジアドバンテージ / ナッツアドバンテージ | レンジ全体のエクイティが高い / 最強クラスのコンボを多く持つこと |
| バリューベット（value bet） | より弱い手にコールされて得をするためのベット |
| ブラフ / セミブラフ（bluff / semi-bluff） | 弱い手で降ろす狙いのベット / ドローなど改善の余地がある手でのブラフ |
| GTO（Game Theory Optimal） | ナッシュ均衡戦略。どちらのプレイヤーも一方的に戦略を変えて得できない（搾取されない）状態 [S18] |
| エクスプロイト（exploit / exploitative play） | 相手の偏り（降りすぎ等）を突いてGTOから意図的にずらす戦略 [S18] |
| ソルバー（solver） | ゲーム木を計算して均衡戦略を近似するソフトウェア。NLHは人力で解けないほど巨大なため使用 [S18] |
| バランス（balance） | 同じ行動の中にバリューとブラフを適切な比率で混ぜること |
| スチール（steal） | CO/BTN/SBからブラインド（＋アンティ）を奪う目的のオープン |
| ディフェンス（defend） | 主にBBがスチールに対しコール/3ベットで抵抗すること |

### 2.6 トーナメント（Tournament / MTT）
| 用語 | 定義 |
|---|---|
| MTT（multi-table tournament） | 複数卓で行う大会。卓が減るとテーブルブレイク/バランシング |
| バイイン（buy-in） | 参加費 [S8] |
| レイトレジストレーション（late registration / レイトレジ） | 大会開始後も一定レベルまで参加登録できる制度 [S19] |
| リエントリー（re-entry） | 敗退後に再度参加費を払って新規スタックで再参加 [S20] |
| リバイ（rebuy） | 敗退前（プレイ中）でもチップを買い足せる制度 [S20] |
| サテライト（satellite / サテ） | 賞品が上位大会の参加権の大会 [S7] |
| バブル（bubble） | 入賞（賞金圏）直前の段階、またはその直前で敗退する順位 [S7] |
| ITM / インマネ（in the money） | 賞金圏に入ること [S7] |
| ファイナルテーブル（final table / FT） | 最後の1卓 |
| ICM（Independent Chip Model） | トーナメントのチップ量を賞金期待値（$EV）に変換するモデル。チップ価値は線形でない（2倍のチップ≠2倍の価値）[S21] |
| チップEV（chip EV / cEV） | チップ量そのものを価値とみなす期待値。ICMを考慮しない [S21] |
| $EV | 賞金ベースの期待値 [S21] |
| リスクプレミアム（risk premium） | ICMにより、チップEVで必要な勝率に上乗せされる追加の必要勝率。例: 3人（スタック500/300/200）・賞金$50/$30/$20で、200点のBBがSB（500点）のオールインにコールする場面、チップEV上37.5%必要なところICMでは約47%必要 [S21] |
| バブルファクター（bubble factor） | スタックを失った時の$EV損失 ÷ 相手を飛ばした時の$EV獲得。オールインのコールに必要な勝率 = BF ÷（BF＋1）（等スタック・デッドマネー無しの単純化された場合）[S22] |
| プッシュ/フォールド（push/fold） | 浅いスタック（目安10〜15BB以下）でオールインかフォールドの二択で戦うこと 【要確認：BB閾値は目安】 |
| エフェクティブスタック（BB換算） | MTTではスタックをBB単位で考える。例: 24,000点、BB 2,000 → 12BB |
| ショートスタック / ディープスタック | BB数が少ない / 多い状態 |
| ストラクチャー（structure） | ブラインドレベルの上がり方・時間・開始スタック |
| デッドボタン（dead button） | トーナメントでは脱落者が出てもボタン位置ルールを維持する方式 [S2] |
| バウンティ / ノックアウト（bounty / KO） | 他者を飛ばすと賞金（賞金首）が得られる形式 |
| PKO（progressive knockout） | 飛ばした相手のバウンティの半分を現金で獲得し、残り半分は自分のバウンティに加算 [S23] |
| ミステリーバウンティ（mystery bounty） | バウンティ額が封筒等でランダムに決まる形式（賞金プールは通常の賞金とバウンティに分割）[S23] |
| ハンド・フォー・ハンド（hand-for-hand / H4H） | バブル付近で全卓が1ハンドずつ同期して進行する方式（遅延による順位操作を防ぐ）。TDAは手順を RP-8 で定める（宣言時点から入賞資格が判定される等）[S2][S32] |
| チップリーダー / ショート（chip leader / short stack） | 最大スタック / 少ないスタック |
| ディール（deal / chop） | 終盤で残りプレイヤーが賞金配分を合意する。チップチョップ（チップ比率で分配）やICMチョップ等。全員の合意が必要で、可否・手続きは会場/主催者のポリシー次第（TDAルールには規定なし）[S33] 【要確認：各大会で可否】 |

---

## 3. 日本でよく使われるポーカー用語・スラング（和→英）

| 日本語 | 英語 | 意味 | 出典 |
|---|---|---|---|
| インマネ | ITM (in the money) | トーナメントで入賞すること | [S24] |
| バブル / バブる | bubble | 入賞直前（で敗退すること）| [S24][S25] |
| オールイン | all-in | 全チップを賭ける | [S25] |
| 飛ぶ / 飛んだ | bust / get knocked out | チップがなくなり敗退する | 【要確認：出典未取得の口語】 |
| プリフロ | preflop | プリフロップ | [S24][S25] |
| ポスフロ | postflop | ポストフロップ（フロップ以降）| [S25] |
| リエン / リエントリー | re-entry | 再エントリー | [S25]（略語「リエン」は【要確認】）|
| サテ | satellite | サテライト（予選）| [S24] |
| バイイン | buy-in | 参加費 | [S25] |
| ナッツ | nuts | 最強ハンド | [S24][S25] |
| ポケット | pocket pair | 手札のペア | [S25] |
| スーテッド / オフスート | suited / offsuit | 同スート / 異スート | [S25] |
| ドンク（ベット） | donk bet | 主導権のない側の先打ちベット | [S25] |
| ブラフキャッチ | bluff catch | ブラフを読んでコールする | [S25] |
| スタック | stack | 手元のチップ | [S25] |
| エクイティ | equity | 勝率（ポットの取り分）| [S25] |
| FT | final table | ファイナルテーブル | 一般略語 |
| スリーベット / 3ベ | 3-bet | リレイズ | 「3ベ」は【要確認：口語】|
| ジャム / シャブ | jam / shove | オールイン | 【要確認：口語】|

注意: 日本語の「スリーカード」は英語では three of a kind（trips/set）。英語で "three card" とは言わない。「ワンペア」は one pair、「ノーペア」は high card。

---

## 4. 主要公式と計算例（すべて自分で再計算済み）

### 4.1 ポットオッズ（必要勝率）
**必要勝率 = コール額 ÷（相手のベットを含む現在のポット ＋ コール額）** [S13]

- 例1（Wikipedia の例）: ポット30（相手のベット込み）、コール10 → 10 ÷ (30+10) = **25%**（オッズ表記 3:1）[S13]
- 例2: ポット100に相手が50ベット → 現在のポット150、コール50 → 50 ÷ (150+50) = 50/200 = **25%**
- 例3（ポットベット）: ポット100に100ベット → 100 ÷ 300 = **33.3%**
- 判断: 自分のエクイティ ＞ 必要勝率 ならコールは（インプライドオッズ等を除いて）+EV。

### 4.2 MDF（最小防御頻度）
**MDF = ポット ÷（ポット ＋ ベット）**（ポットは相手のベット前の額）[S15]

- ポット100に50ベット: 100/150 = **66.7%**
- ポット100に60ベット: 100/160 = **62.5%**（GTO Wizardの例と一致）[S15]
- ポット100に100ベット: 100/200 = **50%**
- 注意: MDFは「ブラフにエクイティがない」前提。相手がブラフ不足なら守り過ぎる必要はない。実戦（特にOOP）ではGTOでもMDFより降りることが多い。[S15]

### 4.3 ブラフの損益分岐点（アルファ / α）
**必要フォールド率 = ベット ÷（ポット ＋ ベット）** = 1 − MDF [S15]

- ポット100に60ベット: 60/160 = **37.5%** [S15]
- ポット100に75ベット: 75/175 = **42.9%**
- ポット100に100ベット: 100/200 = **50%**
- ポット100に150（オーバーベット）: 150/250 = **60%**

### 4.4 SPR
**SPR = エフェクティブスタック ÷ ポット** [S12][S14]
- ポット100、エフェクティブ100 → SPR 1。オールインにコールするには 100/300 = **33%** の勝率が必要 [S14]

### 4.5 2と4のルール（Rule of 2 and 4）
- フロップで（リバーまで2枚見られる前提＝オールイン等）: アウツ × 4 ≒ 完成確率(%)
- ターンで（残り1枚）: アウツ × 2 ≒ 完成確率(%)
- **近似式であり、アウツが多いと×4は過大評価になる。** [S26]

自己計算による正確な値との比較（フロップ時点の未知カード47枚、ターン時点46枚）:

| アウツ | フロップ→リバー 正確値 | ×4 | 3×アウツ＋9 | ターン→リバー 正確値 | ×2 |
|---|---|---|---|---|---|
| 4（ガットショット） | 16.5% | 16% | 21% | 8.7% | 8% |
| 8（OESD） | 31.5% | 32% | 33% | 17.4% | 16% |
| 9（フラッシュドロー） | 35.0% | 36% | 36% | 19.6% | 18% |
| 12 | 45.0% | 48% | 45% | 26.1% | 24% |
| 15（コンボドロー） | 54.1% | 60% | 54% | 32.6% | 30% |
| 21 | 69.9% | 84% | 72% | 45.7% | 42% |

計算式: フロップ→リバー = 1 − C(47−o,2)/C(47,2)、ターン→リバー = o/46。
- ×4は8〜9アウツまではほぼ正確だが、15アウツで約6ポイント、21アウツで約14ポイント過大。10アウツ以上では「3×アウツ＋9」が近い [S26]（ただし少ないアウツでは逆に大きく外れる）。
- ×2は少しだけ過小評価（9アウツで 18% vs 19.6%）。
- 重要: フロップで相手がベットしてくる場合、通常は「次の1枚（ターン）」分のオッズしか保証されない（9アウツでフロップ→ターン ≒ 19.1%）。×4はオールインでリバーまで見られる時に使う。

### 4.6 ICMでの必要勝率（バブルファクター）
**必要勝率 = BF ÷（BF ＋ 1）**（等スタックのオールイン、デッドマネー無しの単純化）[S22]
- BF = 1.18 → 1.18/2.18 = **54%**（チップEVなら50%）[S22]

---

## 出典

- [S1] Wikipedia "Texas hold 'em" — https://en.wikipedia.org/wiki/Texas_hold_%27em
- [S2] Poker TDA Rules 2026 Version 1.0（2026-09-07）— https://www.pokertda.com/view-poker-tda-rules/ （Rule 17, 18-A, 22, 34, 45, RP-8, RP-11）
- [S3] Wikipedia "List of poker hands" — https://en.wikipedia.org/wiki/List_of_poker_hands
- [S4] PokerNews "Big Blind Ante Definition" — https://www.pokernews.com/pokerterms/big-blind-ante.htm
- [S5] Card Player "What Comes First, The Big Blind Or The Ante?" — https://www.cardplayer.com/cardplayer-poker-magazines/66420-cppt-live-casino-hotel-32-21/articles/23815-what-comes-first-the-big-blind-or-the-ante （BBA=BB額、2019年時点のアンティ優先の議論。筆者はアンティ優先を支持）
- [S6] Poker.org "Poker table positions cheat sheet" — https://www.poker.org/poker-cheat-sheets/poker-table-positions-cheat-sheet-aN4rp4C1NZmu/
- [S7] Wikipedia "Glossary of poker terms" — https://en.wikipedia.org/wiki/Glossary_of_poker_terms
- [S8] WPT JAPAN ポーカー用語集（一般用語の補助）— https://wptevent.jp/poker/poker-word-list/
- [S9] Upswing Poker "What is Isolating in Poker?" — https://upswingpoker.com/glossary/isolate/
- [S10] Upswing Poker "The Squeeze Play" — https://upswingpoker.com/glossary/squeeze-play/
- [S11] Upswing Poker "What is a Block Bet" — https://upswingpoker.com/block-bet/
- [S12] Upswing Poker "Stack-to-Pot Ratio (SPR)" — https://upswingpoker.com/glossary/stack-to-pot-ratio-spr/
- [S13] Wikipedia "Pot odds" — https://en.wikipedia.org/wiki/Pot_odds
- [S14] GTO Wizard "Stack-to-pot ratio" — https://blog.gtowizard.com/stack-to-pot-ratio/
- [S15] GTO Wizard "MDF & Alpha" — https://blog.gtowizard.com/mdf-alpha/
- [S16] GTO Wizard "Understanding Blockers in Poker" — https://blog.gtowizard.com/understanding-blockers-in-poker/
- [S17] GTO Wizard "Range Morphology" — https://blog.gtowizard.com/range-morphology/
- [S18] GTO Wizard "What is GTO in Poker?" — https://blog.gtowizard.com/what-is-gto-in-poker/
- [S19] PokerSkill "Late Registration in Poker" — https://www.pokerskill.com/poker-glossary/late-registration/ （定義は一般的な理解に基づく。本文未精読のため細部は【要確認】）
- [S20] PokerNews "Re-Entry" — https://www.pokernews.com/pokerterms/re-entry.htm
- [S21] GTO Wizard "ICM Basics" — https://blog.gtowizard.com/icm-basics/
- [S22] GTO Wizard "What is the Bubble Factor in poker tournaments?" — https://blog.gtowizard.com/what-is-the-bubble-factor-in-poker-tournaments/
- [S23] PokerNews "Your GTO Wizard Guide to Knockout Poker Formats" — https://www.pokernews.com/strategy/your-guide-to-knockout-poker-formats-47675.htm
- [S24] JCSH ポーカー用語集 — https://jcsh.jp/play/poker-terms
- [S25] WPT JAPAN ポーカー用語集 — https://wptevent.jp/poker/poker-word-list/
- [S26] PokerSkill "Rule of 2 and 4" — https://www.pokerskill.com/poker-glossary/rule-of-2-and-4/ （数値は本書で自己再計算）
- [S27] Upswing Poker "What is a Delayed C-Bet" — https://upswingpoker.com/delayed-continuation-bet-c-bet-strategy/
- [S28] Upswing Poker "What is a Probe Bet in Poker?" — https://upswingpoker.com/glossary/probe-bet/
- [S29] Upswing Poker "What is Floating in Poker" — https://upswingpoker.com/glossary/float/
- [S30] Upswing Poker "What are Reverse Implied Odds" — https://upswingpoker.com/reverse-implied-odds/
- [S31] GTO Wizard "Equity Realization" — https://blog.gtowizard.com/equity-realization/
- [S32] PokerNews "Hand-for-Hand Definition" — https://www.pokernews.com/pokerterms/hand-for-hand.htm
- [S33] PokerNews "How to Make a Deal in Poker: ICM and Chip Chop Explained" — https://www.pokernews.com/strategy/to-chop-or-not-to-chop-explaining-standard-deal-making-metho-33148.htm

---

## ファクトチェック記録（2026-10-05）

凡例: ✅ 正しい / ⚠️ 一部修正・補足 / ❌ 誤り（修正済み） / ❓ 未検証・要確認のまま

| 項目 | 確認方法 | 判定 | 対応 |
|---|---|---|---|
| Poker TDA 2026 Rules Version 1.0（2026-09-07）の存在 | pokertda.com/view-poker-tda-rules/ を直接取得。ヘッダー "2026 Rules, Version 1.0. Sept 7, 2026" | ✅ | なし |
| RP-11（BBA・big-blind-first推奨、FT含めアンティ減額しない） | 同上。原文 "If a single-payer ante is used, the big blind ante format (BBA) with big-blind-first calculation is recommended. Antes should not be reduced (including at the final table)…" | ✅ | big-blind-first の具体的手順はTDA本文に定義がない旨を明記（解釈であることを明示） |
| Rule 17 / 18-A / 22 / 34 / 45 の番号と内容 | 同上。各ルール名・本文を照合 | ✅ | なし |
| 「過去にはアンティ優先の会場も」[S5] | Card Player記事: 2019年TDAサミットで約9割がアンティ優先、筆者もアンティ優先を支持。BBA=BB額も確認 | ⚠️ | 「一部の会場」→「約9割（2019年時点）」に修正 |
| BBAの定義・利点 [S4] | PokerNews取得 | ✅ | なし |
| ハンドランキング・キッカー例・ホイール | 手計算で検証 | ✅ | なし |
| ポジション名（9-max/8-max）[S6] | Poker.org取得: SB, BB, UTG, UTG+1, UTG+2, LJ, HJ, CO, BTN。8-maxはUTG+2を除く | ✅ | なし |
| 6-max の表記 | S6に記載なし | ❓ | 【要確認】維持 |
| 最小レイズ例（BB200→600→最低1,000）、ヘッズアップのアクション順 | TDA Rule 45、Wikipediaの記述と照合 | ✅ | なし |
| ガットショットの例「9-8 on J-T-2（7待ち）」 | 8-9-T-J は7でもQでも完成する**オープンエンド（8アウツ）** | ❌ | 「9-8 on J-7-2（T待ち）」に修正 |
| コンボ数（1,326、AK=16）| C(52,2)=1,326 を計算 | ✅ | なし |
| ポットオッズ例1〜3（25%/25%/33.3%） | poker_math.py pot-odds で再計算 | ✅ | なし |
| MDF例（66.7%/62.5%/50%）、GTO WizardのOOPでMDFより降りる記述 | poker_math.py mdf、GTO Wizard [S15] 取得 | ✅ | なし |
| アルファ例（37.5%/42.9%/50%/60%） | poker_math.py bluff | ✅ | なし |
| SPR例（10、SPR1で33%） | poker_math.py spr、GTO Wizard [S14] 原文 "$100/$300 = 33%" | ✅ | なし |
| 2と4のルール表（全6行）、9アウツのフロップ→ターン19.1% | poker_math.py outs と math.comb で再計算（全値一致） | ✅ | なし |
| バブルファクター式・BF1.18→54% [S22] | GTO Wizard取得、計算 1.18/2.18=0.541 | ✅ | なし |
| リスクプレミアム例 [S21] | GTO Wizard取得: 賞金は $50/$30/$20（本書は100/60/40と誤記。比率は同じなので必要勝率は不変）。37.5%→約47% は一致 | ⚠️ | 賞金額と状況（200点のBBが500点SBのオールインにコール）を原典どおりに修正 |
| ディレイドCベット | Upswing [S27] | ✅ | 定義を「プリフロップのアグレッサーが前ストリートをチェックで回した後にベット」に精緻化、【要確認】削除 |
| プローブベット | Upswing [S28]（ターン/リバーのみ） | ✅ | 出典追加、【要確認】削除 |
| フロート | Upswing [S29]。定義上ポジションは必須でない | ⚠️ | 「主にIPで」に修正、出典追加、【要確認】削除 |
| リバースインプライドオッズ | Upswing [S30] | ✅ | 出典追加、【要確認】削除 |
| エクイティリアライゼーション | GTO Wizard [S31]（EV = Equity × EQR × pot、OOPで低い） | ✅ | 出典追加、【要確認】削除 |
| ハンド・フォー・ハンド | PokerNews [S32]、TDA RP-8 | ✅ | 出典追加、【要確認】削除 |
| ディール/チョップ | PokerNews [S33]: 全員の合意が必要、可否は会場ポリシー次第。TDA 2026にはディールの規定なし | ⚠️ | 出典追加。大会ごとの可否は【要確認】維持 |
| プッシュ/フォールドのBB閾値、口語（飛ぶ、リエン、3ベ、ジャム/シャブ）、S19本文 | 今回未検証 | ❓ | 【要確認】維持 |
