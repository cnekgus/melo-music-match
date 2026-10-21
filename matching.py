"""Set-theoretic music matching. Pure functions for reproducible experiments."""

def jaccard(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a | b else 0.0


def feature_sets(selected, songs):
    lookup = {s['id']: s for s in songs}
    chosen = [lookup[sid] for sid in selected if sid in lookup]
    return {
        'songs': set(selected),
        'genres': {s['genre'] for s in chosen if s.get('genre')},
        'moods': {s['mood'] for s in chosen if s.get('mood')},
        'tempos': {s['tempo'] for s in chosen if s.get('tempo')},
    }


def compare(a, b, weights=None):
    weights = weights or {'songs': .35, 'genres': .25, 'moods': .25, 'tempos': .15}
    parts = {k: jaccard(a.get(k, []), b.get(k, [])) for k in weights}
    score = sum(parts[k] * weights[k] for k in weights)
    return {'score': score, 'parts': parts, 'common': {k: sorted(set(a.get(k, [])) & set(b.get(k, []))) for k in weights}, 'is_match': score >= .40}
