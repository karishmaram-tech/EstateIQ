"""
test_prediction.py — Tests for Prediction Logic
================================================
These tests check the core ML prediction functions
directly, without making HTTP requests.

This is called unit testing — testing the smallest
possible unit of code in isolation.
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import mock_predict


class TestMockPredict:
    """
    Test the mock_predict function that runs when
    no trained model file is available.
    """

    def _make_features(
        self,
        area=2100, bedrooms=4, bathrooms=3, floors=2,
        year_built=2005, garage=1, pool=0, garden=1,
        location=7, condition=8
    ):
        """Helper to build a features list without repeating code."""
        return [area, bedrooms, bathrooms, floors, year_built,
                garage, pool, garden, location, condition]

    def test_returns_positive_price(self):
        """Predicted price must always be positive."""
        features = self._make_features()
        price = mock_predict(features)
        assert price > 0, f"Price should be positive, got {price}"

    def test_returns_float(self):
        """Price must be a number, not a string or None."""
        features = self._make_features()
        price = mock_predict(features)
        assert isinstance(price, (int, float)), \
            f"Price should be numeric, got {type(price)}"

    def test_minimum_price_floor(self):
        """
        The mock formula has a minimum floor of $50,000.
        Even the worst possible property should return at least this.
        """
        worst_features = self._make_features(
            area=100, bedrooms=1, bathrooms=1, floors=1,
            year_built=1900, garage=0, pool=0, garden=0,
            location=1, condition=1
        )
        price = mock_predict(worst_features)
        assert price >= 50000, \
            f"Price should never go below $50,000, got ${price:,.0f}"

    def test_larger_area_gives_higher_price(self):
        """All else equal, a larger property should cost more."""
        small = mock_predict(self._make_features(area=1000))
        large = mock_predict(self._make_features(area=3000))
        assert large > small, \
            f"Larger area should cost more. Small: ${small:,.0f}, Large: ${large:,.0f}"

    def test_more_bedrooms_gives_higher_price(self):
        """More bedrooms should increase the predicted price."""
        two_bed  = mock_predict(self._make_features(bedrooms=2))
        five_bed = mock_predict(self._make_features(bedrooms=5))
        assert five_bed > two_bed

    def test_better_location_gives_higher_price(self):
        """Higher location score should increase price."""
        rural = mock_predict(self._make_features(location=1))
        prime = mock_predict(self._make_features(location=10))
        assert prime > rural

    def test_pool_adds_value(self):
        """A pool should add value to a property."""
        without_pool = mock_predict(self._make_features(pool=0))
        with_pool    = mock_predict(self._make_features(pool=1))
        assert with_pool > without_pool

    def test_garage_adds_value(self):
        """A garage should add value to a property."""
        without_garage = mock_predict(self._make_features(garage=0))
        with_garage    = mock_predict(self._make_features(garage=1))
        assert with_garage > without_garage

    def test_newer_property_costs_more(self):
        """Newer properties should cost more than older ones."""
        old_property = mock_predict(self._make_features(year_built=1950))
        new_property = mock_predict(self._make_features(year_built=2020))
        assert new_property > old_property

    def test_price_scales_reasonably_with_area(self):
        """
        Doubling the area should not produce a wildly
        disproportionate price change.
        """
        base   = mock_predict(self._make_features(area=1000))
        double = mock_predict(self._make_features(area=2000))
        ratio  = double / base
        assert 1.0 < ratio < 3.5, \
            f"Doubling area gave a suspicious price ratio of {ratio:.2f}"

    def test_luxury_property_is_expensive(self):
        """
        A luxury property with all features at maximum
        should produce a high price estimate.
        """
        luxury = mock_predict(self._make_features(
            area=8000, bedrooms=7, bathrooms=6, floors=3,
            year_built=2022, garage=1, pool=1, garden=1,
            location=10, condition=10
        ))
        assert luxury > 500000, \
            f"Luxury property should exceed $500K, got ${luxury:,.0f}"

    def test_multiple_calls_stay_in_range(self):
        """
        Because mock_predict has random noise, calling it
        multiple times should stay within a reasonable range.
        """
        features = self._make_features()
        prices   = [mock_predict(features) for _ in range(20)]
        min_price = min(prices)
        max_price = max(prices)
        spread    = (max_price - min_price) / min_price
        assert spread < 0.10, \
            f"Price spread across 20 calls is {spread:.1%}, exceeds 10%"