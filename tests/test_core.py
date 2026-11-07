import unittest, datetime as dt
from core import run, predict

class Tests(unittest.TestCase):

    def test_seasonal(self):
        self.assertEqual(predict(list(range(14)), 8, 'seasonal_naive'), [7, 8, 9, 10, 11, 12, 13, 7])

    def test_forecast(self):
        r = run({})
        self.assertEqual(len(r['forecast']), 7)
        self.assertIn(r['selected_model'], r['backtest'])
        self.assertLess(r['backtest']['trend_weekday']['mae'], 1)

    def test_no_leakage_dates(self):
        for m in run({})['backtest'].values():
            for f in m['folds']:
                self.assertLess(f['train_end'], f['test_start'])

    def test_bad_horizon(self):
        with self.assertRaises(ValueError):
            run({'horizon': 99})

    def test_bad_dates(self):
        with self.assertRaises(ValueError):
            run({'series': [{'date': '2026-01-01', 'value': 1}] * 42})
