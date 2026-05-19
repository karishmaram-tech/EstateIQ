"""
app.py — EstateIQ Flask Application
"""

from flask import Flask, request, jsonify, render_template
import numpy as np
import joblib
import os
import logging
import time
from datetime import datetime
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import config


# ── Logger ────────────────────────────────────────────────

def setup_logger():
    logger = logging.getLogger("estateiq")
    logger.setLevel(config.LOG_LEVEL)

    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(config.LOG_LEVEL)
    console_handler.setFormatter(formatter)

    log_path = "/tmp/app.log" if os.name != "nt" else "app.log"
    file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger()


# ── Flask app ─────────────────────────────────────────────

app = Flask(__name__)
app.config["SECRET_KEY"] = config.SECRET_KEY

try:
    config_warnings = config.validate_config()
    for warning in config_warnings:
        logger.warning(f"CONFIG WARNING: {warning}")
except EnvironmentError as e:
    logger.critical(f"FATAL CONFIG ERROR: {e}")
    raise SystemExit(1)

config.print_config_summary()

logger.info(f"Starting {config.APP_NAME} v{config.APP_VERSION}")
logger.info(f"Environment: {config.ENVIRONMENT}")


# ── Model loading ─────────────────────────────────────────

MODEL_PATH = config.MODEL_PATH


def load_model():
    if os.path.exists(MODEL_PATH):
        logger.info(f"Loading trained model from: {MODEL_PATH}")
        return joblib.load(MODEL_PATH)
    logger.warning(f"Model not found at {MODEL_PATH}. Using mock predictions.")
    return None


model = load_model()


# ── Rate limiter ──────────────────────────────────────────

def get_real_ip():
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return get_remote_address()


limiter = Limiter(
    app=app,
    key_func=get_real_ip,
    default_limits=config.RATE_LIMIT_DEFAULT,
    storage_uri="memory://"
)


# ── Error handlers ────────────────────────────────────────

@app.errorhandler(429)
def rate_limit_exceeded(e):
    logger.warning(f"RATE LIMIT BLOCKED | IP: {request.remote_addr}")
    return jsonify({
        "success":             False,
        "errors":              [f"Too many requests. Limit: {config.RATE_LIMIT_PER_MINUTE}/minute."],
        "error_type":          "rate_limit_exceeded",
        "retry_after_seconds": 60
    }), 429


# ── Prediction logic ──────────────────────────────────────

def mock_predict(features):
    """
    Demo prediction formula.
    Features order:
        0: area
        1: bedrooms
        2: bathrooms
        3: floors
        4: year_built
        5: garage
        6: pool
        7: garden
        8: location_score
        9: condition
    """
    area, bedrooms, bathrooms, floors, year_built, \
    garage, pool, garden, location, condition = features

    base  = 50000
    price = (
        base
        + area       * 120
        + bedrooms   * 8000
        + bathrooms  * 6000
        + floors     * 12000
        + (2025 - year_built) * -300
        + garage     * 15000
        + pool       * 25000
        + garden     * 10000
        + location   * 5000
        + condition  * 8000
    )

    noise = price * np.random.uniform(-0.02, 0.02)
    return max(50000, price + noise)


# ── Routes ────────────────────────────────────────────────

@app.route("/")
def index():
    metrics = {
        "accuracy":   94.2,
        "train_size": 50000,
        "features":   10,
        "r2_score":   0.942,
        "mae":        12400,
        "rmse":       18200
    }
    return render_template("index.html", metrics=metrics)


@app.route("/predict", methods=["POST"])
@limiter.limit(config.RATE_LIMIT_PREDICT)
def predict():
    request_start_time = time.time()
    request_id = datetime.now().strftime("%Y%m%d%H%M%S%f")

    logger.info(f"REQUEST [{request_id}] | New prediction request received")

    try:
        data = request.get_json(silent=True, force=False)

        if not data:
            logger.warning(f"REQUEST [{request_id}] | Empty JSON received")
            return jsonify({
                "success": False,
                "errors":  ["No data received."],
                "request_id": request_id
            }), 400

        logger.debug(f"REQUEST [{request_id}] | Raw input: {data}")

        # ── Extract inputs ────────────────────────────────
        area          = float(data.get("area",           0))
        bedrooms      = int(data.get("bedrooms",         0))
        bathrooms     = int(data.get("bathrooms",        0))
        floors        = int(data.get("floors",           1))
        year_built    = int(data.get("year_built",    2000))
        garage        = int(data.get("garage",           0))
        pool          = int(data.get("pool",             0))
        garden        = int(data.get("garden",           0))
        location      = int(data.get("location_score",   5))
        condition     = int(data.get("condition",        5))

        # ── Validate inputs ───────────────────────────────
        errors = []

        if area <= 0 or area > 20000:
            errors.append("Area must be between 1 and 20,000 sq ft")
        if bedrooms < 1 or bedrooms > 20:
            errors.append("Bedrooms must be between 1 and 20")
        if bathrooms < 1 or bathrooms > 15:
            errors.append("Bathrooms must be between 1 and 15")
        if year_built < 1800 or year_built > 2025:
            errors.append("Year built must be between 1800 and 2025")

        if errors:
            logger.warning(f"REQUEST [{request_id}] | Validation failed | {errors}")
            return jsonify({
                "success":    False,
                "errors":     errors,
                "request_id": request_id
            }), 400

        # ── Predict ───────────────────────────────────────
        features = [
            area, bedrooms, bathrooms, floors, year_built,
            garage, pool, garden, location, condition
        ]

        if model:
            price      = float(model.predict([features])[0])
            model_type = "trained_model"
        else:
            price      = mock_predict(features)
            model_type = "demo_formula"

        # ── Build response ────────────────────────────────
        low       = price * 0.92
        high      = price * 1.08
        price_psf = price / area if area > 0 else 0

        if price < 150000:
            market       = "Below Average"
            market_color = "blue"
        elif price < 300000:
            market       = "Average"
            market_color = "green"
        elif price < 600000:
            market       = "Above Average"
            market_color = "amber"
        else:
            market       = "Premium"
            market_color = "red"

        response_time_ms = round((time.time() - request_start_time) * 1000, 2)

        logger.info(
            f"REQUEST [{request_id}] | SUCCESS | "
            f"Price: ${price:,.0f} | Market: {market} | "
            f"Model: {model_type} | Time: {response_time_ms}ms"
        )

        return jsonify({
            "success":          True,
            "price":            round(price, 2),
            "price_low":        round(low, 2),
            "price_high":       round(high, 2),
            "price_psf":        round(price_psf, 2),
            "market_position":  market,
            "market_color":     market_color,
            "features_used":    features,
            "request_id":       request_id,
            "response_time_ms": response_time_ms
        })

    except (ValueError, TypeError) as e:
        response_time_ms = round((time.time() - request_start_time) * 1000, 2)
        logger.error(f"REQUEST [{request_id}] | INPUT ERROR | {str(e)}")
        return jsonify({
            "success":    False,
            "errors":     [f"Invalid input: {str(e)}"],
            "request_id": request_id
        }), 400

    except Exception as e:
        response_time_ms = round((time.time() - request_start_time) * 1000, 2)
        logger.error(f"REQUEST [{request_id}] | SERVER ERROR | {str(e)}", exc_info=True)
        return jsonify({
            "success":    False,
            "errors":     ["Server error. Please try again."],
            "request_id": request_id
        }), 500


@app.route("/health")
def health():
    logger.debug("Health check called")
    return jsonify({
        "status":       "ok",
        "app":          config.APP_NAME,
        "version":      config.APP_VERSION,
        "environment":  config.ENVIRONMENT,
        "model_loaded": os.path.exists(config.MODEL_PATH),
        "debug_mode":   config.DEBUG
    })


@app.route("/api/info")
def api_info():
    return jsonify({
        "api":     config.APP_NAME,
        "version": config.APP_VERSION,
        "rate_limits": {
            "predict": f"{config.RATE_LIMIT_PER_MINUTE} requests per minute per IP",
            "global":  f"{config.RATE_LIMIT_PER_DAY} per day, {config.RATE_LIMIT_PER_HOUR} per hour"
        },
        "endpoints": {
            "GET /":         "Main application UI",
            "POST /predict": "Submit property details, receive price prediction",
            "GET /health":   "Server health check",
            "GET /api/info": "API information and rate limits"
        },
        "model_loaded": os.path.exists(config.MODEL_PATH)
    })


# ── Start server ──────────────────────────────────────────

if __name__ == "__main__":
    logger.info(f"Starting server on port {config.PORT}")
    app.run(
        host="0.0.0.0",
        port=config.PORT,
        debug=config.DEBUG
    )