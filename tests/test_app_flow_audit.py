"""Regression checks from the full route/form audit."""
import unittest
from unittest.mock import patch

from test_app import HAVE_FLASK, csrf, login, make_app


@unittest.skipUnless(HAVE_FLASK, "Flask 未インストール")
class TestFlowAudit(unittest.TestCase):
    def setUp(self):
        self.app = make_app()
        self.client = self.app.test_client()
        login(self.client)
        self.token = csrf(self.client.get('/tools').text)

    def calculate(self, **data):
        return self.client.post('/tools', data=dict(csrf=self.token, **data))

    def test_invalid_calculator_inputs_do_not_produce_misleading_results(self):
        cases = [
            dict(kind='pot', pot='-100', bet='50'),
            dict(kind='pot', pot='100', bet='-10'),
            dict(kind='pot', pot='nan', bet='50'),
            dict(kind='pot', pot='100', bet='inf'),
            dict(kind='spr', pot='0', stack='100'),
            dict(kind='spr', pot='100', stack='-1'),
            dict(kind='ev', p='101', win='300', lose='100'),
            dict(kind='ev', p='-1', win='300', lose='100'),
            dict(kind='ev', p='40', win='nan', lose='100'),
            dict(kind='avg', entrants='10', start='100', remain='20', bb='10'),
            dict(kind='avg', entrants='10', start='100', remain='1.5', bb='10'),
        ]
        for data in cases:
            with self.subTest(data=data):
                response = self.calculate(**data)
                self.assertEqual(response.status_code, 200)
                self.assertIn('入力を確認', response.text)

    def test_valid_calculator_boundaries(self):
        for p, result in [('0', '-100.00'), ('100', '+300.00')]:
            response = self.calculate(kind='ev', p=p, win='300', lose='100')
            self.assertNotIn('入力を確認', response.text)
            self.assertIn(result, response.text)
        response = self.calculate(kind='spr', stack='0', pot='100')
        self.assertNotIn('入力を確認', response.text)
        self.assertIn('0.00', response.text)

    def test_reference_diagrams_are_at_most_eight_players(self):
        with patch('sensei.views.learn.render_template', return_value='ok') as render:
            for url in ['/learn/lesson/L0-4', '/cheatsheet']:
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                diagrams = render.call_args.kwargs['diagrams']
                self.assertTrue(diagrams)
                self.assertEqual([d['n'] for d in diagrams], [8, 6])

    def test_empty_news_training_guides_to_knowledge_and_keeps_active_battle(self):
        self.client.get('/train/positions')
        with self.client.session_transaction() as session:
            previous = dict(session['battle'])
        response = self.client.get('/train/news', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('このテーマの問題はまだありません', response.text)
        with self.client.session_transaction() as session:
            self.assertEqual(session['battle'], previous)

    def test_session_edit_preserves_opponent_note_and_type(self):
        from sensei.db import q
        from sensei.views.records import OPP_TYPES, opponent_fields
        note = '左の人は「不明」とは違う / リバーを観察'
        self.client.post('/records/session/new', data=dict(
            csrf=self.token, venue='amusement', opp_types=OPP_TYPES[0], opponents=note))
        response = self.client.get('/records/session/1')
        self.assertIn('value="' + note + '"', response.text)
        self.assertNotIn('value="不明" checked', response.text)
        with self.app.app_context():
            saved = q('SELECT opponents FROM play_sessions WHERE id=1', one=True)['opponents']
        types, restored = opponent_fields(saved)
        self.client.post('/records/session/1', data=dict(
            csrf=self.token, venue='amusement', opp_types=types, opponents=restored))
        with self.app.app_context():
            self.assertEqual(q('SELECT opponents FROM play_sessions WHERE id=1', one=True)['opponents'], saved)
        self.assertEqual(opponent_fields('昔の自由メモ'), ([], '昔の自由メモ'))
        self.assertEqual(opponent_fields(' / メモのみ'), ([], 'メモのみ'))

    def test_extra_check_does_not_replace_required_warmup_item(self):
        from sensei.views.coach import WARMUP
        response = self.client.post('/coach/mental', data=dict(
            csrf=self.token, kind='pre', check=WARMUP[:-1] + ['数字カードを見た']), follow_redirects=True)
        self.assertIn('ウォームアップが全部そろっていません', response.text)
        self.assertNotIn('準備完了！', response.text)
        response = self.client.post('/coach/mental', data=dict(
            csrf=self.token, kind='pre', check=WARMUP + ['数字カードを見た']), follow_redirects=True)
        self.assertIn('準備完了！', response.text)


if __name__ == '__main__':
    unittest.main()
