import unittest
from test_app import HAVE_FLASK, make_app, login

@unittest.skipUnless(HAVE_FLASK, 'Flask unavailable')
class RangeGuideTests(unittest.TestCase):
    def test_every_seat_and_format_explains_behind_without_strategy(self):
        from sensei.arena import POSITIONS
        client=make_app().test_client(); login(client)
        for fmt in ['mtt','cash']:
            for n, positions in POSITIONS.items():
                for i, pos in enumerate(positions):
                    response=client.get('/learn/range-guide',query_string={'format':fmt,'players':n,'position':pos})
                    self.assertEqual(response.status_code,200)
                    self.assertIn(f'{n}人卓の{pos}：後ろは{n-i-1}人',response.text)
                    self.assertIn('全169マスや最適頻度はアプリに転記していません',response.text)
                    if pos=='BB': self.assertIn('新しくオープンする場面ではありません',response.text)
        for qs in [{'players':'9'},{'players':'bad'},{'players':'2','position':'BTN'},{'format':'bad'}]:
            self.assertEqual(client.get('/learn/range-guide',query_string=qs).status_code,400)

    def test_auth_and_reference_links(self):
        client=make_app().test_client()
        self.assertEqual(client.get('/learn/range-guide').status_code,302)
        login(client)
        for route in ['/table/ranges','/learn/actions']:
            self.assertIn('/learn/range-guide',client.get(route).text)
