"""
conftest.py — Shared Test Configuration and Fixtures
=====================================================
pytest automatically loads this file before running any tests.
Fixtures defined here are available to all test files.

WHAT IS A FIXTURE?
A fixture is a function that sets up something a test needs,
runs the test, and then cleans up afterwards.
"""

import pytest
import os
import sys

# Add the parent directory to Python's path so tests can import app and config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set test environment variables BEFORE importing app
# This prevents the app from looking for real files during testing
os.environ.setdefault("ENVIRONMENT", "testing")
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("MODEL_PATH", "model/house_price_model.pkl")
os.environ.setdefault("DEBUG", "False")
os.environ.setdefault("LOG_LEVEL", "WARNING")
os.environ.setdefault("RATE_LIMIT_PER_MINUTE", "1000")
os.environ.setdefault("RATE_LIMIT_PER_HOUR", "10000")
os.environ.setdefault("RATE_LIMIT_PER_DAY", "100000")

from app import app as flask_app


@pytest.fixture(scope="session")
def app():
    """
    Create a Flask application configured for testing.
    scope="session" means this fixture is created ONCE
    for the entire test session and shared across all tests.
    """
    flask_app.config.update({
        "TESTING": True,
        "DEBUG": False,
        "WTF_CSRF_ENABLED": False,
    })

    yield flask_app


@pytest.fixture(scope="session")
def client(app):
    """
    Create a Flask test client.
    Lets you make HTTP requests to your app
    without running a real server.
    """
    return app.test_client()


@pytest.fixture
def sample_payload():
    """A valid prediction payload for use in multiple tests."""
    return {
        "area":           2100,
        "bedrooms":       4,
        "bathrooms":      3,
        "floors":         2,
        "year_built":     2005,
        "garage":         1,
        "pool":           0,
        "garden":         1,
        "location_score": 7,
        "condition":      8
    }


@pytest.fixture
def small_property_payload():
    """A small, low-value property payload for boundary testing."""
    return {
        "area":           500,
        "bedrooms":       1,
        "bathrooms":      1,
        "floors":         1,
        "year_built":     1960,
        "garage":         0,
        "pool":           0,
        "garden":         0,
        "location_score": 2,
        "condition":      3
    }


@pytest.fixture
def luxury_payload():
    """A large luxury property payload for upper-bound testing."""
    return {
        "area":           8000,
        "bedrooms":       7,
        "bathrooms":      6,
        "floors":         3,
        "year_built":     2022,
        "garage":         1,
        "pool":           1,
        "garden":         1,
        "location_score": 10,
        "condition":      10
    }