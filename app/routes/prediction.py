"""
app/routes/prediction.py
========================
Prediction API routes.

Routes:
    POST /api/v1/predict  — House price prediction
    POST /api/v1/explain  — SHAP feature importance
"""

import logging
import time
from datetime import datetime
from flask import Blueprint, request, jsonify
from app.extensions import limiter
from app.services.validator import validate_prediction_request
from app.services.predictor import (
    PredictionInput,
    predict,
    get_shap_data,
    ModelLoader
)
import config

logger = logging.getLogger("estateiq")

prediction_bp = Blueprint("prediction", __name__, url_prefix="/api/v1")


@prediction_bp.route("/predict", methods=["POST"])
@limiter.limit(config.RATE_LIMIT_PREDICT)
def predict_price():
    """
    House price prediction endpoint.

    Request Body (JSON):
        area           (float)  Total area in sq ft
        bedrooms       (int)    Number of bedrooms (1-20)
        bathrooms      (int)    Number of bathrooms (1-15)
        floors         (int)    Number of floors (1-4)
        year_built     (int)    Year built (1800-2025)
        garage         (int)    Has garage: 0 or 1
        pool           (int)    Has pool: 0 or 1
        garden         (int)    Has garden: 0 or 1
        location_score (int)    Location quality (1-10)
        condition      (int)    Property condition (1-10)

    Returns:
        200: Prediction result with price and market position
        400: Validation errors
        500: Server error
    """
    request_start = time.time()
    request_id    = datetime.now().strftime("%Y%m%d%H%M%S%f")

    logger.info(f"PREDICT [{request_id}] | Request received")

    # ── Parse request ─────────────────────────────────────
    raw_data = request.get_json(silent=True, force=False)

    # ── Validate ──────────────────────────────────────────
    validation = validate_prediction_request(raw_data)
    if not validation.is_valid:
        logger.warning(
            f"PREDICT [{request_id}] | Validation failed | "
            f"Errors: {validation.errors}"
        )
        return jsonify({
            "success":    False,
            "errors":     validation.errors,
            "request_id": request_id
        }), 400

    # ── Predict ───────────────────────────────────────────
    try:
        prediction_input = PredictionInput(**validation.data)
        result           = predict(prediction_input)
        response_ms      = round((time.time() - request_start) * 1000, 2)

        logger.info(
            f"PREDICT [{request_id}] | SUCCESS | "
            f"Price: ${result.price:,.0f} | "
            f"Market: {result.market} | "
            f"Model: {result.model_type} | "
            f"Time: {response_ms}ms"
        )

        return jsonify({
            "success":          True,
            "price":            result.price,
            "price_low":        result.price_low,
            "price_high":       result.price_high,
            "price_psf":        result.price_psf,
            "market_position":  result.market,
            "market_color":     result.market_color,
            "model_type":       result.model_type,
            "request_id":       request_id,
            "response_time_ms": response_ms
        })

    except Exception as e:
        response_ms = round((time.time() - request_start) * 1000, 2)
        import traceback
        print("FULL ERROR:", traceback.format_exc())
        logger.error(
            f"PREDICT [{request_id}] | ERROR | {str(e)}",
            exc_info=True
        )
        return jsonify({
            "success":    False,
            "errors":     ["Prediction failed. Please try again."],
            "request_id": request_id
        }), 500


@prediction_bp.route("/explain", methods=["POST", "GET"])
def explain():
    """
    SHAP explainability endpoint.
    Returns global feature importance from the trained model.
    """
    request_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
    shap_data  = get_shap_data()

    if shap_data is None:
        return jsonify({
            "success":    False,
            "errors":     [
                "SHAP data not available. "
                "Run: python scripts/train_model.py"
            ],
            "request_id": request_id
        }), 503

    return jsonify({
        "success":            True,
        "feature_importance": shap_data.get("feature_importance", []),
        "base_value":         shap_data.get("base_value", 0),
        "request_id":         request_id,
        "explanation":        (
            "Each value shows the average dollar impact of "
            "that feature across all predictions"
        )
    })