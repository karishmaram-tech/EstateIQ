"""
app/__init__.py
===============
Application factory for EstateIQ.
"""

import logging
import os
from flask import Flask, jsonify

import config
from app.extensions import limiter


def create_app(config_override: dict = None) -> Flask:
    """
    Create and configure the Flask application.

    Args:
        config_override: Optional dict to override config values.
                        Used in testing to pass test-specific settings.

    Returns:
        Configured Flask application instance.
    """
    app = Flask(
        __name__,
        template_folder=os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "templates"
        ),
        static_folder=os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "static"
        ),
    )

    # ── Core Flask Config ─────────────────────────────────
    app.config["SECRET_KEY"]     = config.SECRET_KEY
    app.config["DEBUG"]          = config.DEBUG
    app.config["TESTING"]        = False
    app.config["JSON_SORT_KEYS"] = False

    # ── Apply test overrides ──────────────────────────────
    if config_override:
        app.config.update(config_override)

    # ── Validate config ───────────────────────────────────
    _validate_startup_config(app)

    # ── Initialize Extensions ─────────────────────────────
    _init_extensions(app)

    # ── Register Blueprints ───────────────────────────────
    _register_blueprints(app)

    # ── Register Error Handlers ───────────────────────────
    _register_error_handlers(app)

    # ── Log startup ───────────────────────────────────────
    logger = logging.getLogger("estateiq")
    logger.info(f"App created: {config.APP_NAME} v{config.APP_VERSION}")
    logger.info(f"Environment: {config.ENVIRONMENT}")

    return app


def _validate_startup_config(app: Flask):
    try:
        warnings = config.validate_config()
        logger = logging.getLogger("estateiq")
        for warning in warnings:
            logger.warning(f"CONFIG: {warning}")
    except EnvironmentError as e:
        raise SystemExit(f"FATAL CONFIG ERROR: {e}")


def _init_extensions(app: Flask):
    limiter.init_app(app)
    app.config["RATELIMIT_DEFAULT"]         = config.RATE_LIMIT_DEFAULT
    app.config["RATELIMIT_HEADERS_ENABLED"] = True


def _register_blueprints(app: Flask):
    from app.routes.main       import main_bp
    from app.routes.prediction import prediction_bp
    from app.routes.health     import health_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(health_bp)


def _register_error_handlers(app: Flask):

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({
            "success":    False,
            "errors":     ["Bad request: " + str(e)],
            "error_type": "bad_request"
        }), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            "success":    False,
            "errors":     [f"Endpoint not found: {str(e)}"],
            "error_type": "not_found"
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({
            "success":    False,
            "errors":     ["Method not allowed on this endpoint"],
            "error_type": "method_not_allowed"
        }), 405

    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        logger = logging.getLogger("estateiq")
        logger.warning(f"RATE LIMIT | {str(e)}")
        return jsonify({
            "success":             False,
            "errors":              [
                f"Too many requests. "
                f"Limit: {config.RATE_LIMIT_PER_MINUTE}/minute. "
                f"Please wait and try again."
            ],
            "error_type":          "rate_limit_exceeded",
            "retry_after_seconds": 60
        }), 429

    @app.errorhandler(500)
    def server_error(e):
        logger = logging.getLogger("estateiq")
        logger.error(f"SERVER ERROR: {str(e)}", exc_info=True)
        return jsonify({
            "success":    False,
            "errors":     ["Internal server error. Please try again."],
            "error_type": "server_error"
        }), 500