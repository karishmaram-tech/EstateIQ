"""
app/routes/health.py
====================
Health check and API information routes.

Routes:
    GET /health       — Liveness check for monitoring
    GET /api/v1/info  — API documentation and limits
    GET /api/v1/metrics — Runtime metrics
"""

import logging
import os
from datetime import datetime
from flask import Blueprint, jsonify
from app.services.predictor import ModelLoader
import config

logger     = logging.getLogger("estateiq")
health_bp  = Blueprint("health", __name__)

# Track when the app started for uptime calculation
_app_start_time      = datetime.now()
_prediction_count    = 0
_error_count         = 0


def increment_predictions():
    global _prediction_count
    _prediction_count += 1


def increment_errors():
    global _error_count
    _error_count += 1


@health_bp.route("/health")
def health():
    """
    Liveness check endpoint.
    Returns 200 if the application is running.
    Used by Hugging Face, Docker, and monitoring tools.
    """
    logger.debug("Health check called")
    return jsonify({
        "status":       "ok",
        "app":          config.APP_NAME,
        "version":      config.APP_VERSION,
        "environment":  config.ENVIRONMENT,
        "model_loaded": ModelLoader.is_real_model(),
        "uptime_s":     int((datetime.now() - _app_start_time).total_seconds())
    })


@health_bp.route("/api/v1/info")
def api_info():
    """
    API documentation endpoint.
    Describes all available endpoints and rate limits.
    """
    return jsonify({
        "api":         config.APP_NAME,
        "version":     config.APP_VERSION,
        "environment": config.ENVIRONMENT,
        "rate_limits": {
            "predict": f"{config.RATE_LIMIT_PER_MINUTE} requests/minute/IP",
            "global":  (
                f"{config.RATE_LIMIT_PER_DAY}/day, "
                f"{config.RATE_LIMIT_PER_HOUR}/hour per IP"
            )
        },
        "endpoints": {
            "GET  /":               "Main application UI",
            "GET  /health":         "Application health check",
            "GET  /api/v1/info":    "This endpoint — API documentation",
            "GET  /api/v1/metrics": "Runtime metrics",
            "POST /api/v1/predict": "House price prediction",
            "GET  /api/v1/explain": "SHAP feature importance",
        },
        "model_loaded": ModelLoader.is_real_model(),
    })


@health_bp.route("/api/v1/metrics")
def metrics():
    """
    Runtime metrics endpoint.
    Shows operational stats — the beginning of observability.
    In production this would feed into Prometheus/Grafana.
    """
    uptime = (datetime.now() - _app_start_time).total_seconds()
    return jsonify({
        "uptime_seconds":    round(uptime),
        "predictions_total": _prediction_count,
        "errors_total":      _error_count,
        "model_loaded":      ModelLoader.is_real_model(),
        "version":           config.APP_VERSION,
        "environment":       config.ENVIRONMENT,
    })