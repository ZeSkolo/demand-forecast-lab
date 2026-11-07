import math, datetime as dt

def solve(a, b):
    n = len(b)
    m = [list(r) + [v] for r, v in zip(a, b)]
    for i in range(n):
        pivot = max(range(i, n), key=lambda j: abs(m[j][i]))
        m[i], m[pivot] = (m[pivot], m[i])
        if abs(m[i][i]) < 1e-12:
            raise ValueError('Singular regression')
        v = m[i][i]
        m[i] = [x / v for x in m[i]]
        for j in range(n):
            if j != i:
                v = m[j][i]
                m[j] = [x - v * y for x, y in zip(m[j], m[i])]
    return [r[-1] for r in m]

def predict(values, horizon, method):
    n = len(values)
    if method == 'seasonal_naive':
        return [values[n - 7 + i % 7] for i in range(horizon)]

    def features(i):
        return [1, i / 100] + [float(i % 7 == k) for k in range(1, 7)]
    xs = [features(i) for i in range(n)]
    a = [[sum((x[i] * x[j] for x in xs)) + (1e-06 if i == j else 0) for j in range(8)] for i in range(8)]
    b = [sum((x[i] * y for x, y in zip(xs, values))) for i in range(8)]
    w = solve(a, b)
    return [max(0, sum((x * y for x, y in zip(w, features(n + i))))) for i in range(horizon)]

def run(p):
    rows = p.get('series')
    h = p.get('horizon', 7)
    if not isinstance(h, int) or not 1 <= h <= 30:
        raise ValueError('horizon must be 1–30')
    if rows is None:
        rows = [{'date': (dt.date(2026, 1, 1) + dt.timedelta(days=i)).isoformat(), 'value': round(100 + 0.4 * i + 15 * math.sin(2 * math.pi * i / 7), 3)} for i in range(100)]
    if not isinstance(rows, list) or not 42 <= len(rows) <= 2000:
        raise ValueError('42–2000 daily observations required')
    dates = [dt.date.fromisoformat(r['date']) for r in rows]
    v = [r['value'] for r in rows]
    if any((not isinstance(x, (int, float)) or not math.isfinite(x) or x < 0 for x in v)):
        raise ValueError('Demand must be finite and nonnegative')
    if any((b - a != dt.timedelta(days=1) for a, b in zip(dates, dates[1:]))):
        raise ValueError('Dates must be consecutive, daily and ordered')
    reports = {}
    for method in ['seasonal_naive', 'trend_weekday']:
        errors = []
        actual = []
        folds = []
        for end in range(max(28, len(v) - 28), len(v) - 6, 7):
            truth = v[end:end + 7]
            forecast = predict(v[:end], len(truth), method)
            e = [a - b for a, b in zip(truth, forecast)]
            errors += e
            actual += truth
            folds.append({'train_end': dates[end - 1].isoformat(), 'test_start': dates[end].isoformat(), 'mae': sum(map(abs, e)) / len(e)})
        reports[method] = {'mae': sum(map(abs, errors)) / len(errors), 'rmse': (sum((x * x for x in errors)) / len(errors)) ** 0.5, 'wape': sum(map(abs, errors)) / sum(actual) if sum(actual) else None, 'folds': folds}
    selected = min(reports, key=lambda k: reports[k]['mae'])
    forecast = predict(v, h, selected)
    return {'selected_model': selected, 'backtest': reports, 'forecast': [{'date': (dates[-1] + dt.timedelta(days=i + 1)).isoformat(), 'value': round(x, 3)} for i, x in enumerate(forecast)], 'selection_basis': 'rolling_origin_MAE', 'synthetic': p.get('series') is None}
