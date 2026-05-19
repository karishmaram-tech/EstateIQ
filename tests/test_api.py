"""
test_api.py — Tests for Flask API Endpoints
============================================
Integration tests that test the full request cycle:
routing, validation, prediction, and response formatting.
"""

import pytest
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestHealthEndpoint:
    """Tests for GET /health"""

    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_json(self, client):
        response = client.get("/health")
        data = response.get_json()
        assert data is not None

    def test_health_has_status_field(self, client):
        response = client.get("/health")
        data = response.get_json()
        assert "status" in data

    def test_health_status_is_ok(self, client):
        response = client.get("/health")
        data = response.get_json()
        assert data["status"] == "ok"

    def test_health_has_version(self, client):
        response = client.get("/health")
        data = response.get_json()
        assert "version" in data

    def test_health_has_environment(self, client):
        response = client.get("/health")
        data = response.get_json()
        assert "environment" in data


class TestApiInfoEndpoint:
    """Tests for GET /api/info"""

    def test_api_info_returns_200(self, client):
        response = client.get("/api/info")
        assert response.status_code == 200

    def test_api_info_has_rate_limits(self, client):
        response = client.get("/api/info")
        data = response.get_json()
        assert "rate_limits" in data

    def test_api_info_has_endpoints(self, client):
        response = client.get("/api/info")
        data = response.get_json()
        assert "endpoints" in data


class TestHomePage:
    """Tests for GET /"""

    def test_homepage_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_homepage_returns_html(self, client):
        response = client.get("/")
        assert b"html" in response.data.lower()

    def test_homepage_contains_app_name(self, client):
        response = client.get("/")
        assert b"EstateIQ" in response.data


class TestPredictEndpoint:
    """Tests for POST /predict"""

    def test_valid_payload_returns_200(self, client, sample_payload):
        response = client.post(
            "/predict",
            data=json.dumps(sample_payload),
            content_type="application/json"
        )
        assert response.status_code == 200

    def test_valid_payload_returns_success_true(self, client, sample_payload):
        response = client.post(
            "/predict",
            data=json.dumps(sample_payload),
            content_type="application/json"
        )
        data = response.get_json()
        assert data["success"] is True

    def test_response_contains_price(self, client, sample_payload):
        response = client.post(
            "/predict",
            data=json.dumps(sample_payload),
            content_type="application/json"
        )
        data = response.get_json()
        assert "price" in data

    def test_response_price_is_positive(self, client, sample_payload):
        response = client.post(
            "/predict",
            data=json.dumps(sample_payload),
            content_type="application/json"
        )
        data = response.get_json()
        assert data["price"] > 0

    def test_response_contains_price_range(self, client, sample_payload):
        response = client.post(
            "/predict",
            data=json.dumps(sample_payload),
            content_type="application/json"
        )
        data = response.get_json()
        assert "price_low" in data
        assert "price_high" in data

    def test_price_low_is_less_than_price_high(self, client, sample_payload):
        response = client.post(
            "/predict",
            data=json.dumps(sample_payload),
            content_type="application/json"
        )
        data = response.get_json()
        assert data["price_low"] < data["price_high"]

    def test_response_contains_market_position(self, client, sample_payload):
        response = client.post(
            "/predict",
            data=json.dumps(sample_payload),
            content_type="application/json"
        )
        data = response.get_json()
        assert "market_position" in data

    def test_market_position_is_valid_value(self, client, sample_payload):
        response = client.post(
            "/predict",
            data=json.dumps(sample_payload),
            content_type="application/json"
        )
        data = response.get_json()
        valid_positions = ["Below Average", "Average", "Above Average", "Premium"]
        assert data["market_position"] in valid_positions

    def test_response_contains_price_per_sqft(self, client, sample_payload):
        response = client.post(
            "/predict",
            data=json.dumps(sample_payload),
            content_type="application/json"
        )
        data = response.get_json()
        assert "price_psf" in data
        assert data["price_psf"] > 0

    def test_response_contains_request_id(self, client, sample_payload):
        response = client.post(
            "/predict",
            data=json.dumps(sample_payload),
            content_type="application/json"
        )
        data = response.get_json()
        assert "request_id" in data

    def test_response_contains_response_time(self, client, sample_payload):
        response = client.post(
            "/predict",
            data=json.dumps(sample_payload),
            content_type="application/json"
        )
        data = response.get_json()
        assert "response_time_ms" in data

    def test_luxury_property_is_premium(self, client, luxury_payload):
        response = client.post(
            "/predict",
            data=json.dumps(luxury_payload),
            content_type="application/json"
        )
        data = response.get_json()
        assert data["success"] is True
        assert data["market_position"] == "Premium"

    def test_small_property_is_not_premium(self, client, small_property_payload):
        response = client.post(
            "/predict",
            data=json.dumps(small_property_payload),
            content_type="application/json"
        )
        data = response.get_json()
        assert data["success"] is True
        assert data["market_position"] != "Premium"


class TestPredictValidation:
    """Tests for input validation on POST /predict"""

    def _post(self, client, payload):
        return client.post(
            "/predict",
            data=json.dumps(payload),
            content_type="application/json"
        )

    def test_area_zero_returns_400(self, client, sample_payload):
        payload = {**sample_payload, "area": 0}
        response = self._post(client, payload)
        assert response.status_code == 400

    def test_area_negative_returns_400(self, client, sample_payload):
        payload = {**sample_payload, "area": -500}
        response = self._post(client, payload)
        assert response.status_code == 400

    def test_area_too_large_returns_400(self, client, sample_payload):
        payload = {**sample_payload, "area": 99999}
        response = self._post(client, payload)
        assert response.status_code == 400

    def test_too_many_bedrooms_returns_400(self, client, sample_payload):
        payload = {**sample_payload, "bedrooms": 25}
        response = self._post(client, payload)
        assert response.status_code == 400

    def test_too_many_bathrooms_returns_400(self, client, sample_payload):
        payload = {**sample_payload, "bathrooms": 20}
        response = self._post(client, payload)
        assert response.status_code == 400

    def test_future_year_returns_400(self, client, sample_payload):
        payload = {**sample_payload, "year_built": 2099}
        response = self._post(client, payload)
        assert response.status_code == 400

    def test_ancient_year_returns_400(self, client, sample_payload):
        payload = {**sample_payload, "year_built": 1700}
        response = self._post(client, payload)
        assert response.status_code == 400

    def test_error_response_has_errors_field(self, client, sample_payload):
        payload = {**sample_payload, "area": -1}
        response = self._post(client, payload)
        data = response.get_json()
        assert "errors" in data
        assert isinstance(data["errors"], list)
        assert len(data["errors"]) > 0

    def test_error_response_has_success_false(self, client, sample_payload):
        payload = {**sample_payload, "area": -1}
        response = self._post(client, payload)
        data = response.get_json()
        assert data["success"] is False

    def test_empty_json_body_returns_400(self, client):
        response = client.post(
            "/predict",
            data="{}",
            content_type="application/json"
        )
        assert response.status_code == 400

    def test_non_json_body_does_not_return_500(self, client):
        response = client.post(
            "/predict",
            data="this is not json",
            content_type="text/plain"
        )
        assert response.status_code != 500


class TestNotFoundEndpoint:
    """Test behaviour for routes that do not exist."""

    def test_unknown_route_returns_404(self, client):
        response = client.get("/this-route-does-not-exist")
        assert response.status_code == 404