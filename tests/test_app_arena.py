"""卓UIの採点・再送信・条件検証と、出典データを保った頻度学習。"""
import json
import random
import unittest
from test_app import make_app, login, csrf, PASSWORD, HAVE_FLASK
if HAVE_FLASK:
    from sensei import arena
    from sensei.db import q


@unittest.skipUnless(HAVE_FLASK, "Flask 未インストール")
class ArenaTests(unittest.TestCase):
    def setUp(self):
        self.app = make_app()
        self.c = self.app.test_client()
        login(self.c)

    def start(self, **kw):
        tok = csrf(self.c.get('/table').text)
        r = self.c.post('/table/start', data=dict(csrf=tok, **dict(
            {'mode':'range','format':'mtt','players':'2','position':'BB','stack':'8'}, **kw)))
        return int(r.location.split('/')[-1])

    def test_conditions_and_no_unsupported_ranges(self):
        for url in ['/table','/table?format=cash','/table/ranges','/table/ranges?format=cash&position=BB&stack=10']:
            self.assertEqual(self.c.get(url).status_code, 200)
        for url in ['/table?format=invalid','/table/ranges?stack=20','/table/ranges?position=UTG','/table/ranges?hand=bad']:
            self.assertIn(self.c.get(url).status_code, (400,404))
        for mode in arena.MODES:
            for n in arena.POSITIONS:
                for pos in arena.POSITIONS[n]:
                    cfg=dict(mode=mode,format='mtt',players=n,stack=8,position=pos)
                    if mode=='range' and n!=2:
                        with self.assertRaises(ValueError): arena.config_from(cfg)
                        continue
                    with self.app.app_context():
                        run=arena.load_run(arena.create_run(cfg))
                    self.assertEqual(len(run['questions']),5, cfg)
                    for it in run['questions']:
                        self.assertEqual(len(it['seats']),n)
                        cards=it['cards']+it['board']+it.get('villain',[])
                        self.assertEqual(len(cards),len(set(cards)))
                        self.assertTrue(all(s['stack']>=0 for s in it['seats']))
                        self.assertIn(it['answer'],range(len(it['choices'])))

    def test_atomic_grading_review_and_progress(self):
        rid=self.start()
        with self.app.app_context(): run=arena.load_run(rid)
        page=self.c.get(f'/table/run/{rid}')
        tok=csrf(page.text)
        self.assertNotIn(run['questions'][0]['explain'],page.text)
        for i,it in enumerate(run['questions']):
            chosen=(it['answer']+1)%len(it['choices']) if i==0 else it['answer']
            data=dict(csrf=tok,index=i,choice=chosen)
            for _ in range(2):
                self.assertEqual(self.c.post(f'/table/run/{rid}/answer',data=data).status_code,302)
        with self.app.app_context():
            self.assertEqual(q('SELECT COUNT(*) n FROM attempts',one=True)['n'],5)
            self.assertEqual(arena.stats('mtt'),{'n':5,'c':4})
            self.assertEqual(arena.stats('cash'),{'n':0,'c':0})
        self.assertIn('SESSION COMPLETE',self.c.get(f'/table/run/{rid}').text)
        retry=self.c.post(f'/table/run/{rid}/retry',data={'csrf':tok})
        with self.app.app_context():
            second=arena.load_run(int(retry.location.split('/')[-1]))
            self.assertEqual(len(second['questions']),1)
            self.assertEqual(second['questions'][0]['key'],run['questions'][0]['key'])
        exported=json.loads(self.c.get('/export.json').text)
        self.assertEqual(len(exported['arena_runs']),2)

    def test_invalid_and_out_of_order_answers_do_not_write(self):
        rid=self.start()
        tok=csrf(self.c.get(f'/table/run/{rid}').text)
        for i,a in [('bad',0),(1,0),(0,999),(0,-1),(-1,0)]:
            self.assertEqual(self.c.post(f'/table/run/{rid}/answer',data=dict(csrf=tok,index=i,choice=a)).status_code,400)
        self.assertEqual(self.c.post(f'/table/run/{rid}/answer',data=dict(index=0,choice=0)).status_code,400)
        with self.app.app_context(): self.assertEqual(arena.stats('mtt')['n'],0)
        self.assertEqual(self.c.get(f'/table/run/{rid}?q=5').status_code,400)

    def test_frequency_data_and_mixed_strategy(self):
        self.assertEqual(len(set(arena.hand_names())),169)
        for depth in (5,8,10):
            for pos in arena.POSITIONS[2]:
                fs=arena.frequencies(depth,pos)
                self.assertEqual(set(fs),set(arena.hand_names()))
                self.assertTrue(all(0<=v<=1 for v in fs.values()))
        # 公式Raw Dataに実在する混合。多数決で純粋戦略に丸めない。
        self.assertEqual(arena.frequencies(8,'BTN/SB')['Q4o'],.19)
        self.assertEqual(arena.frequencies(8,'BB')['Q7o'],.53)
        self.assertEqual(arena.category(.00001),2)
        self.assertEqual(arena.category(.99999),2)
        self.assertEqual(arena.category(0),0)
        self.assertEqual(arena.category(1),1)
        self.assertEqual(arena.post_order(2),['BB','BTN/SB'])
        self.assertEqual(arena.post_order(9)[-1],'BTN')

    def test_flop_exact_equities_and_allin_accounting(self):
        # 独立した全列挙の再計算。シードやモンテカルロ推定ではない。
        for sample in arena.flop_examples():
            eq,n=arena.drills.pm.equity([sample['hero'],sample['villain']],sample['board'],trials=1000)
            self.assertEqual(n,990)
            self.assertEqual(eq[0],sample['equity'])
        for n in arena.POSITIONS:
            for seed in range(12):
                it=arena.question(dict(mode='flop',format='cash',players=n,position='random',stack=8),random.Random(seed))
                bb=next(s for s in it['seats'] if s['pos']=='BB')
                hero=next(s for s in it['seats'] if s['hero'])
                self.assertEqual(bb['stack'],0)
                self.assertEqual(it['pot'],sum(s['bet'] for s in it['seats']))
                self.assertIn('GTO解ではない',it['label'])


@unittest.skipUnless(HAVE_FLASK, "Flask 未インストール")
class RememberLoginTests(unittest.TestCase):
    def test_remembered_session_survives_new_client(self):
        app=make_app(); c=app.test_client()
        tok=csrf(c.get('/login').text)
        r=c.post('/login',data=dict(csrf=tok,user='koja',password=PASSWORD,remember='yes'))
        self.assertIn('Expires=',r.headers['Set-Cookie'])
        self.assertEqual(app.permanent_session_lifetime.days,90)
        cookie=c.get_cookie('sensei_session')
        fresh=app.test_client(); fresh.set_cookie('sensei_session',cookie.value)
        self.assertEqual(fresh.get('/table').status_code,200)
        self.assertEqual(fresh.get('/login').location,'/')
        tok=csrf(fresh.get('/settings').text)
        fresh.post('/logout',data={'csrf':tok})
        self.assertEqual(fresh.get('/table').status_code,302)

    def test_shared_device_cookie_is_not_persistent(self):
        app=make_app();c=app.test_client()
        response=login(c)
        self.assertNotIn('Expires=',response.headers['Set-Cookie'])
        with c.session_transaction() as sess: self.assertFalse(sess.permanent)
