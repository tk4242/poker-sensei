"""公開版点検で見つけたスマホメニュー・設定保存の回帰検証。"""
import unittest
from test_app import HAVE_FLASK, csrf, login, make_app


@unittest.skipUnless(HAVE_FLASK, 'Flask 未インストール')
class TestLiveFixes(unittest.TestCase):
    def setUp(self):
        self.app = make_app()
        self.c = self.app.test_client()
        login(self.c)

    def settings(self):
        from sensei.db import get_setting
        with self.app.app_context():
            return get_setting('daily_quota', 30), get_setting('batch_size', 5)

    def test_invalid_settings_do_not_partially_save(self):
        token = csrf(self.c.get('/settings').text)
        for quota, batch in [('40', 'abc'), ('40', ''), ('', '10'), ('6.5', '10'),
                             ('40', '4.5'), ('4', '10'), ('201', '10'), ('40', '2'), ('40', '21'),
                             ('nan', '5'), ('40', '9' * 5000)]:
            with self.subTest(quota=quota, batch=batch[:20]):
                r = self.c.post('/settings', data={'csrf': token, 'daily_quota': quota, 'batch_size': batch})
                self.assertEqual(r.status_code, 400)
                self.assertIn('保存していません', r.text)
                self.assertEqual(self.settings(), (30, 5))

    def test_valid_settings_save_both_at_boundaries(self):
        token = csrf(self.c.get('/settings').text)
        for quota, batch in [(5, 3), (200, 20), (40, 10)]:
            r = self.c.post('/settings', data={'csrf': token, 'daily_quota': str(quota), 'batch_size': str(batch)})
            self.assertEqual(r.status_code, 302)
            self.assertEqual(self.settings(), (quota, batch))

    def test_mobile_menu_and_no_false_home_highlight(self):
        page = self.c.get('/settings').text
        self.assertIn('<details class="mobile-menu">', page)
        mobile = page.split('aria-label="スマホメニュー"')[1].split('</nav>')[0]
        for path in ('/settings', '/knowledge', '/quest', '/library'):
            self.assertIn('href="' + path + '"', mobile)
        bottom = page.split('<nav class="bottom">')[1]
        self.assertNotIn('href="/" class="on"', bottom)
        self.assertNotIn('mobile-menu', self.app.test_client().get('/login').text)
