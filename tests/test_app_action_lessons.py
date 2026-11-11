"""アクション入門の保存・採点・誤答復習・出典を検証する。"""
import random
import unittest

from test_app import HAVE_FLASK, csrf, login, make_app


@unittest.skipUnless(HAVE_FLASK, 'Flask 未インストール')
class ActionLessonTests(unittest.TestCase):
    def setUp(self):
        self.app = make_app()
        self.c = self.app.test_client()
        login(self.c)

    def test_all_lessons_grade_and_save_progress(self):
        from sensei import action_lessons, practice
        topics = list(action_lessons.data()['lessons'])
        self.assertEqual(topics, ['actions', 'ranges', 'flop', 'sizing', 'threebet', 'turnriver', 'hu', 'bluff', 'range-reading'])
        for topic in topics:
            with self.subTest(topic=topic):
                page = self.c.get('/learn/actions/' + topic)
                self.assertEqual(page.status_code, 200)
                response = self.c.post('/learn/actions/' + topic + '/practice', data={'csrf': csrf(page.text)})
                bid = int(response.location.rsplit('/', 1)[1])
                with self.app.app_context():
                    batch = practice.load_batch(bid)
                    self.assertEqual(len(batch['questions']), 5)
                    answers = {f'a{i}': item['answer'] for i, item in enumerate(batch['questions'])}
                response = self.c.post(response.location, data={**answers, 'csrf': csrf(page.text)}, follow_redirects=True)
                self.assertIn('アクション入門・次のテーマへ', response.text)
                with self.app.app_context():
                    le = next(le for le in action_lessons.overview() if le['topic'] == topic)
                    self.assertEqual(le['score'], 5)
                    self.assertTrue(le['completed'])
        self.assertIn('全9テーマ', self.c.get('/learn/actions').text)

    def test_wrong_answers_enter_existing_review_and_keep_explanations(self):
        from sensei import action_lessons, practice
        with self.app.app_context():
            items = action_lessons.questions('flop', random.Random(7))
            bid = practice.create_batch('practice', action_lessons.title('flop'), items)
            practice.grade(practice.load_batch(bid), [-1] * 5, [None] * 5)
            self.assertEqual(practice.due_count(), 5)
            due = practice.due_items(5)
            self.assertEqual({it['key'] for it in due}, {it['key'] for it in items})
            for item in due:
                self.assertEqual(item['action_topic'], 'flop')
                self.assertTrue(item['explain'])
                self.assertTrue(item['source'])
        response = self.c.get('/practice/review', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('復習', response.text)

    def test_all_questions_have_sources_and_stable_shuffled_answer(self):
        from sensei import action_lessons, content
        keys = []
        for topic, lesson in action_lessons.data()['lessons'].items():
            keys.extend(it['key'] for it in action_lessons.questions(topic, random.Random(0)))
            self.assertIn(lesson['tag'], content.TAG_JP)
            self.assertTrue(lesson['source_ids'])
            for seed in range(6):
                for raw, item in zip(lesson['questions'], action_lessons.questions(topic, random.Random(seed))):
                    self.assertEqual(len(set(item['choices'])), 4)
                    self.assertEqual(item['choices'][item['answer']], raw['choices'][raw['answer']])
                    self.assertIn(item['label'], ['RULE', 'THEORY'])
                    self.assertTrue(item['source'])
                    self.assertTrue(all(s['url'].startswith('https://') for s in item['source']))
        self.assertEqual(len(keys), 45)
        self.assertEqual(len(set(keys)), 45)

    def test_completion_uses_latest_four_of_five(self):
        from sensei import action_lessons, practice
        with self.app.app_context():
            for score in [4, 3]:
                items = action_lessons.questions('actions', random.Random(score))
                bid = practice.create_batch('practice', action_lessons.title('actions'), items)
                practice.grade(practice.load_batch(bid),
                               [it['answer'] if i < score else -1 for i, it in enumerate(items)], [None] * 5)
                le = action_lessons.overview()[0]
                self.assertEqual(le['score'], score)
                self.assertEqual(le['completed'], score >= 4)

    def test_unknown_topics_auth_and_csrf(self):
        self.assertEqual(self.c.get('/learn/actions/unknown').status_code, 404)
        self.assertEqual(self.c.post('/learn/actions/flop/practice').status_code, 400)
        anonymous = self.app.test_client()
        self.assertEqual(anonymous.get('/learn/actions').status_code, 302)
