# 卓トレーニングのデータ

## HRC HU（2026-11-08確認）
- 出典：<https://www.holdemresources.net/hune>
- 原CSV：<https://www.holdemresources.net/hrdata/holdemresources_hu_equilibrium.zip>
- SHA-256: `650da7525b35e12adbc03df26d6690c30b583ff4b7d930156c104012a040ec9d`
- `holdemresources_hu_push.csv` / `holdemresources_hu_call.csv` のstack=5.00,8.00,10.00のみを抽出。先頭stack列を除く169列の小数を変更せず保存。1,014値を独立したfact-checkerが原CSVと全件比較し一致。
- 公式の公開チャートではなくRaw Dataの頻度を使用。チャートの閾値から頻度を推測しない。0と1だけを純粋戦略、それ以外を混合として出題。
- HUでSBがpush/fold、BBがcall/foldだけを選ぶ限定ゲーム。スタックはブラインド前。公式No Ante例との整合確認済み。ただし原CSVにante/rake/payoutのメタデータはない。その限界を画面でも表示し、通常のMTTやレーキ込みリングへ一般化しない。
- 公式が原データを公開しているが、明示的なオープンライセンスは確認していない。「自由再配布可能」との権利表記はしない。
- ART/GTOの多人数データは、計算条件と利用条件が今回の収録用途で確認できないため採用していない。GTO Wizardなどの有料ソルバーからのスクレイピングも行わない。

## フロップ
- `flop-examples.json` はこのアプリ用の計算例。`tools/poker_math.py` の `equity([hero, villain], board, trials=1000)` で残り45枚から2枚の全990通りを列挙。引き分けは折半。
- 5つの対決のEQ：56.060606 / 4.343434 / 20.202020 / 91.616162 / 34.242424%。
- 元ポット6bb（HU）または6.5bb（BTN対BB・SBの0.5bb込み）。相手のall-in 3/6/9bbに対して、必要EQ=C/(P+2C)、call EV=EQ*(P+2C)-C。fold EV=0。レーキ・ICM・追加ベットなし。
- 計算の出典：<https://blog.gtowizard.com/what-are-pot-odds-in-poker/>。既知の相手の2枚を公開する数学教材であり、フロップのGTOレンジ解ではない。
- 5番目の対決は3/6bbでcall、9bbでfold。サイズで判断が変わる理由を学ぶ。
