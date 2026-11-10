"""Source-backed situations; rules and arithmetic are not solver frequencies."""
import copy
import json
from functools import lru_cache

from .config import CONTENT_DIR


@lru_cache(maxsize=1)
def data():
    result = json.loads((CONTENT_DIR / 'decision-spots.json').read_text())
    source_path = CONTENT_DIR / 'source-decisions.json'
    if source_path.exists():
        result['spots'].extend(json.loads(source_path.read_text())['spots'])
    return result


def question(cfg, rng):
    from .arena import POSITIONS, seats
    available = [s for s in data()['spots'] if cfg['format'] in s['formats']
                 and ('players' not in s or s['players'] == cfg['players'])]
    spot = copy.deepcopy(rng.choice(available))
    n = cfg['players']
    button = 'BTN/SB' if n == 2 else 'BTN'
    def rename(text):
        return text.replace('BTN', button) if n == 2 else text
    hero = rename(spot['hero'])
    investments = {rename(k): v for k, v in spot['investments'].items() if k != 'SB' or n != 2}
    active = [rename(p) for p in spot.get('active', ['BTN', 'BB'])]
    folded = [p for p in POSITIONS[n] if p not in active]
    if n == 2 and spot['street'] == 'プリフロップ' and 'SB' in spot['investments']:
        spot['pot'] -= spot['investments']['SB']
    for field in ('prompt', 'explain', 'hint', 'condition'):
        spot[field] = rename(spot[field])
    spot['history'] = [rename(x) for x in spot['history']]
    if n == 2:
        spot['condition'] = spot['condition'].replace('他はフォールド。', '両者が残っています。').replace('SBの0.5bbはデッドマネー。', '')
        spot['history'] = [x.replace('SB 0.5bb／BB 1bb', 'BTN/SB 0.5bb／BB 1bb') for x in spot['history'] if x != 'SB フォールド']
    spot['choices'] = [rename(x) for x in spot['choices']]
    spot.update(mode='decisions', format=cfg['format'], players=n, hero=hero, investments=investments,
                seats=seats(n, hero, spot['stack'] or 0, investments, folded),
                frequencies=None)
    if spot['stack'] is None:
        for seat in spot['seats']:
            seat['stack'] = None
    return spot
