"""出典付きアクション入門。ソルバーの最適アクション採点ではない。"""
import json
import random
from functools import lru_cache

from . import drills, practice
from .config import CONTENT_DIR
from .db import q


@lru_cache(maxsize=1)
def data():
    return json.loads((CONTENT_DIR / 'action-lessons.json').read_text(encoding='utf-8'))


def title(topic):
    return 'アクション入門5問: ' + data()['lessons'][topic]['short']


def overview():
    lessons = []
    for topic, lesson in data()['lessons'].items():
        row = q('SELECT result FROM batches WHERE title=? AND graded=1 ORDER BY id DESC LIMIT 1',
                (title(topic),), one=True)
        result = json.loads(row['result']) if row else None
        lessons.append(dict(lesson, topic=topic, score=result['score'] if result else None,
                            completed=bool(result and result['score'] >= 4)))
    return lessons


def questions(topic, rng=None):
    rng = rng or random.Random()
    lesson = data()['lessons'][topic]
    out = []
    for question in lesson['questions']:
        item = drills.finish(
            'actions-' + topic, 2, lesson['tag'], question['prompt'], question['choices'],
            question['choices'][question['answer']], question['explain'], lesson['goal'],
            question.get('label', 'THEORY'),
            [data()['sources'][key] for key in question['source_ids']],
            'アクション入門 / ' + lesson['short'], rng, action_topic=topic)
        out.append(practice.shuffled(item, rng))
    return out
