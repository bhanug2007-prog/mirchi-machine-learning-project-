from unittest import TestCase

import numpy as np
import pandas as pd

from scripts.market_signals import MODELS, WEATHER_DELAY, build_market_features, evaluate, predict_at_origin


class MarketSignalsTest(TestCase):
    def setUp(self):
        dates = pd.date_range("2025-01-01", periods=80)
        steps = np.arange(len(dates))
        self.market = pd.DataFrame({"price": 15000 + steps * 4, "arrival": 10 + steps}, index=dates)
        self.weather = pd.DataFrame({"rain": steps % 10, "max_temp": 35 - steps % 5}, index=dates)

    def test_forecasts_do_not_read_future_labels_or_unpublished_signals(self):
        origin = self.market.index[60]
        delay = pd.Timedelta(days=7)

        def forecast(market, weather):
            features = build_market_features(market, weather).dropna()
            targets = pd.Series(market["price"].reindex(features.index + delay).to_numpy(), index=features.index)
            return predict_at_origin(features, targets, origin, delay, MODELS)

        expected = forecast(self.market, self.weather)
        changed_market = self.market.copy()
        changed_weather = self.weather.copy()
        changed_market.loc[changed_market.index > origin, "price"] = 50000
        changed_market.loc[origin:, "arrival"] = 9000
        changed_weather.loc[changed_weather.index > origin - pd.Timedelta(days=WEATHER_DELAY)] = [500, 5]
        self.assertIsNotNone(expected)
        self.assertEqual(expected, forecast(changed_market, changed_weather))

    def test_missing_weather_keeps_market_only_comparison(self):
        _, rows = evaluate(self.market)
        self.assertEqual(len(rows), 7)
        self.assertTrue(all(row["scored"] for row in rows))
        self.assertEqual(set(rows[0]["metrics"]), {"persistence", "price", "arrivals"})
