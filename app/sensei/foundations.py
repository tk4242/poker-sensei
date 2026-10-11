"""初心者向けの数学入門。戦略ソルバーではなく、前提を固定した学習用計算。"""
import json
import random

from . import drills, practice
from .db import q

SOURCES = {
    'ev': {'title': 'GTO Wizard: What Is Expected Value in Poker?', 'url': 'https://blog.gtowizard.com/what-is-expected-value-in-poker/'},
    'odds': {'title': 'GTO Wizard: What Are Pot Odds in Poker?', 'url': 'https://blog.gtowizard.com/what-are-pot-odds-in-poker/'},
    'wizard': {'title': 'GTO Wizard Help: Study Mode', 'url': 'https://help.gtowizard.com/study-mode/'},
}
ASSUMPTIONS = '計算の前提：相手は1人、コール後の追加ベットなし、引き分け・レーキなし。チップの増減だけを比較します。勝率は練習用の仮定で、実際のハンドから推定した値ではありません。'
LESSONS = {
    'ev': {'title': '期待値：1回の勝ち負けから平均へ', 'short': '期待値（EV）', 'goal': '勝ったかより、判断を繰り返すとどうなるかを考える。',
           'points': [('EVって何？', '同じ条件で判断を繰り返したときの、1回あたりの平均の損益です。プラスでも、この1回で必ず勝つわけではありません。'),
                      ('まず比較の基準を決める', 'ここでは「今フォールドする」を0とします。すでにポットに出した分を、コールする費用にもう一度足しません。'),
                      ('2つの結果を足す', '勝つ確率 × 勝ったときに増える分 − 負ける確率 × 失う分。チップのEVと大会の賞金価値は別で、賞金判断にはICMなどの検討が必要です。')], 'source': 'ev'},
    'odds': {'title': 'オッズ：コールの値段を知る', 'short': 'ポットオッズ', 'goal': '支払う額と、コール後の合計を分けて数える。',
             'points': [('ポットとコール', 'ポットは場に集まっているチップ。コールは相手のベットに合わせて追加する額です。'),
                        ('必要勝率を出す', 'コール額 ÷ 自分がコールした後のポット。ここでは勝率がこの値と同じなら損益ゼロ、上ならコールのチップEVはプラスです。'),
                        ('勝率は別に考える', '必要勝率は値段から計算できますが、自分の勝率は相手が持ちうるハンドの組み合わせに依存します。追加のベットが残る場面では、単純な勝率比較だけでは足りません。')], 'source': 'odds'},
    'bet': {'title': 'ベットサイズ：額よりポットとの割合', 'short': 'ベットサイズ', 'goal': '「大きい・怖い」を、ポット比と必要勝率に置き換える。',
            'points': [('サイズを割合で読む', '50%ポットは、ベット前のポットの半分の額。相手のベットが大きくなるほど、このモデルでコールに必要な勝率は上がります。'),
                       ('打つ理由も考える', '強いハンドで相手からチップを得ることと、相手を降ろすことでは、期待する結果が違います。プラスEVのベットでも、チェックのEVのほうが高いことがあります。'),
                       ('最適サイズはまだ断定しない', 'この早見表はコールの値段表です。自分が何%で打つべきかは決めません。GTO Wizardでは同じ条件の各アクションのEVを比較して確認します。')], 'source': 'ev'},
    'wizard': {'title': 'GTO Wizard：答えより比較のしかた', 'short': 'GTO Wizard入門', 'goal': '条件・頻度・EVを分けて読み、丸暗記から一歩進む。',
               'points': [('条件をそろえる', 'Studyの画面でポジション、ボード、アクションを確認します。このアプリから自動連携はしていません。公式画面は下のリンクから開けます。'),
                          ('頻度とEVを区別する', 'Strategyはアクションの配分、EVは期待値、EQはエクイティです。ベット頻度が50%という表示を、勝率50%と読まないようにしましょう。'),
                          ('1つのハンドを比較する', '自分の予想を決めてから、同じ局面のアクション別EVを確認。違っていたら、サイズや相手のレンジなど、見落とした条件を1つ探すのがこのコースの練習方法です。')], 'source': 'wizard'},
}


def scenario(size=50, equity=40):
    if size not in (25, 50, 75, 100, 150) or equity not in (10, 20, 25, 30, 40, 60):
        raise ValueError('練習用の選択肢から選んでください。')
    pot, bet = 100, size
    return {'pot': pot, 'bet': bet, 'equity': equity, 'total': pot + 2 * bet,
            'win': pot + bet, 'lose': bet,
            'required': drills.pm.pot_odds(pot + bet, bet) * 100,
            'ev': round(drills.pm.ev(equity / 100, pot + bet, bet), 6)}


def title(topic):
    return '数字の基礎5問: ' + LESSONS[topic]['short']


def overview():
    out = []
    for topic, lesson in LESSONS.items():
        row = q('SELECT result FROM batches WHERE title=? AND graded=1 ORDER BY id DESC LIMIT 1', (title(topic),), one=True)
        result = json.loads(row['result']) if row else None
        out.append(dict(lesson, topic=topic, score=result['score'] if result else None,
                        completed=bool(result and result['score'] >= 4)))
    return out


CONCEPTS = {
    'ev': [
        ('EVがプラスの判断でも、その1回は負けることがある？', ['ある。EVは繰り返した平均', 'ない。毎回勝つ', 'EVと勝率は同じ意味', '負けたら計算は必ず間違い'], '結果1回ではなく、同じ条件での平均を見ます。'),
        ('このコースで「フォールドのEVは0」とする基準は？', ['今の判断時点からの増減', 'ハンド開始前からの収支', '大会で受け取る賞金', 'すでに出したチップも返る前提'], 'すでに出したチップは戻りません。ここでは今からの選択を比較します。')],
    'odds': [
        ('必要勝率を求めるときの分母は？', ['自分のコール後のポット', '相手のベット前のポットだけ', '自分の残りスタック', '相手のベット額だけ'], '相手のベットと自分のコールを含む合計を使います。'),
        ('追加のベットが残っている場面でも、必要勝率との比較だけで常に判断できる？', ['できない。将来のベットも影響する', 'できる。勝率だけで十分', '必要勝率は常に50%', '相手のレンジは無関係'], '勝率をそのまま最終的な取り分と見なせないことがあります。')],
    'bet': [
        ('ポット比の早見表だけで、自分の最適なベットサイズは決まる？', ['決まらない。これはコールの値段表', '必ず50%ポットになる', '最大サイズが必ず最適', '必要勝率とベット頻度は同じ'], '値段の計算と、どの戦略のEVが高いかの比較は別です。'),
        ('あるベットのEVがプラスだった。最善だと結論できる？', ['他のアクションのEVも比べる', 'プラスなら必ず最善', 'サイズは大きいほど必ずよい', 'チェックのEVは常に0'], '同じ基準で、チェックや別サイズのEVも比較します。')],
    'wizard': [
        ('Strategyでベット頻度50%と表示。意味は？', ['その条件でベットを選ぶ配分', 'そのハンドの勝率', '必ず50%ポットで打つ', '賞金を得る確率'], '頻度・ベットサイズ・EQは別の指標です。'),
        ('EVとEQについて正しいのは？', ['EVは期待値、EQはエクイティ', 'どちらもベット額', 'EVは勝率だけ', 'EQは残り人数'], '表示する指標と単位を確かめます。'),
        ('別の局面のEVと比較する前に何を見る？', ['条件と比較の基準が同じか', '文字の色だけ', '自分の直近の勝敗だけ', '相手が強そうに見えるかだけ'], '条件が違う数字を、そのまま自分の局面に移しません。'),
        ('公式のInfoboxで確認できる情報は？', ['ポジション・ポット・ボード', '相手の実際の手札', '次に配られるカード', '必ず取れる賞金'], 'StudyのInfoboxで局面の条件を確認できます。'),
        ('この入門コースの計算例は？', ['前提を固定したチップEVの練習', 'GTO Wizardの実測ソルバー出力', '賞金EVを自動最適化した結果', 'どの場面でも最適なベット指示'], 'このアプリの例題は計算練習です。ソルバーによる戦略出力ではありません。')],
}


def questions(topic, rng=None):
    rng = rng or random.Random()
    lesson = LESSONS[topic]
    out = []

    def add(prompt, choices, explanation, source=None):
        item = drills.finish('foundations-' + topic, 2, 'terms' if topic == 'wizard' else 'math', prompt, choices, choices[0], explanation,
                             lesson['goal'], 'RULE', SOURCES[source or lesson['source']],
                             '数字の基礎 / ' + lesson['short'], rng, foundation=topic)
        out.append(practice.shuffled(item, rng))

    for prompt, choices, explanation in CONCEPTS[topic]:
        add(prompt, choices, explanation)
    for size in rng.sample((25, 50, 75, 100, 150), 3) if topic != 'wizard' else ():
        e = rng.choice((20, 25, 40, 60))
        s = scenario(size, e)
        if topic == 'ev':
            correct = s['ev']
            vals = [correct, correct + 10, correct - 10, correct + 30]
            add(f"{ASSUMPTIONS} ベット前100、相手が{size}、コールも{size}。勝率{e}%なら、フォールドを0としたコールEVは？",
                [f'{v:+g} チップ' for v in vals],
                f"{e}% × {s['win']} − {100-e}% × {size} = {correct:+g}チップ。勝ったときは自分のコール分を利益に数えません。（tools/poker_math.py で検算）")
        else:
            values = [s['required'], 50, 100 * size / (100 + size), 100 * size / 100]
            # Round first, then deduplicate; pad with clearly distinct alternatives.
            labels = list(dict.fromkeys(f'{v:.1f}%' for v in values))
            for v in (5, 10, 80, 90):
                if len(labels) >= 4:
                    break
                if f'{v:.1f}%' not in labels:
                    labels.append(f'{v:.1f}%')
            add(f"{ASSUMPTIONS} ベット前100に相手が{size}%ポット（{size}チップ）をベット。コールの損益分岐となる必要勝率は？",
                labels[:4], f"{size} ÷ (100 + {size} + {size}) = {s['required']:.1f}%。自分のコールも分母に含めます。（tools/poker_math.py で検算）", 'odds')
    return out
