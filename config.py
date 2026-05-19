"""
config.py — EstateIQ Central Configuration Module
"""

import os
import logging
from dotenv import load_dotenv

load_dotenv(override=False)


def get_env(key, default=None, required=False, cast=str):
    value = os.environ.get(key)

    if value is None:
        if required:
            raise EnvironmentError(
                f"Required environment variable '{key}' is not set."
            )
        return default

    if cast == bool:
        return value.lower() in ("true", "1", "yes", "on")

    try:
        return cast(value)
    except (ValueError, TypeError):
        raise ValueError(
            f"Environment variable '{key}' has value '{value}' "
            f"which cannot be converted to {cast.__name__}."
        )


# ── Flask core ────────────────────────────────────────────
SECRET_KEY  = get_env("SECRET_KEY",  default="dev-insecure-key-do-not-use-in-production")
DEBUG       = get_env("DEBUG",       default=False, cast=bool)
PORT        = get_env("PORT",        default=7860,  cast=int)
ENVIRONMENT = get_env("ENVIRONMENT", default="development")

# ── Logging ───────────────────────────────────────────────
LOG_LEVEL_STR = get_env("LOG_LEVEL", default="INFO").upper()
# Convert string like "INFO" to integer like 20
LOG_LEVEL = getattr(logging, LOG_LEVEL_STR, logging.INFO)

# ── Model ─────────────────────────────────────────────────
MODEL_PATH  = get_env("MODEL_PATH",  default="model/house_price_model.pkl")
APP_NAME    = get_env("APP_NAME",    default="EstateIQ")
APP_VERSION = get_env("APP_VERSION", default="1.0.0")

# ── Rate limiting ─────────────────────────────────────────
RATE_LIMIT_PER_MINUTE = get_env("RATE_LIMIT_PER_MINUTE", default=30,  cast=int)
RATE_LIMIT_PER_HOUR   = get_env("RATE_LIMIT_PER_HOUR",   default=50,  cast=int)
RATE_LIMIT_PER_DAY    = get_env("RATE_LIMIT_PER_DAY",    default=200, cast=int)

# These are the formatted strings Flask-Limiter expects
RATE_LIMIT_PREDICT = f"{RATE_LIMIT_PER_MINUTE} per minute"
RATE_LIMIT_DEFAULT = [
    f"{RATE_LIMIT_PER_DAY} per day",
    f"{RATE_LIMIT_PER_HOUR} per hour"
]


def validate_config():
    warnings = []

    if SECRET_KEY == "dev-insecure-key-do-not-use-in-production":
        if ENVIRONMENT == "production":
            raise EnvironmentError(
                "SECRET_KEY must be set to a secure random value in production."
            )
        else:
            warnings.append(
                "SECRET_KEY is using the insecure default. "
                "Change this before going to production."
            )

    if DEBUG and ENVIRONMENT == "production":
        warnings.append("DEBUG is True in production. Set DEBUG=False.")

    if PORT < 1024 or PORT > 65535:
        raise ValueError(f"PORT must be between 1024 and 65535. Got: {PORT}")

    if RATE_LIMIT_PER_MINUTE < 1:
        raise ValueError("RATE_LIMIT_PER_MINUTE must be at least 1.")

    return warnings


def print_config_summary():
    print("\n" + "═" * 50)
    print(f"  {APP_NAME} v{APP_VERSION} — Configuration")
    print("═" * 50)
    print(f"  Environment:  {ENVIRONMENT}")
    print(f"  Debug mode:   {DEBUG}")
    print(f"  Port:         {PORT}")
    print(f"  Log level:    {LOG_LEVEL_STR}")
    print(f"  Model path:   {MODEL_PATH}")
    print(f"  Secret key:   {'[SET]' if SECRET_KEY != 'dev-insecure-key-do-not-use-in-production' else '[DEFAULT - insecure]'}")
    print(f"  Rate limits:  {RATE_LIMIT_PER_MINUTE}/min | {RATE_LIMIT_PER_HOUR}/hr | {RATE_LIMIT_PER_DAY}/day")
    print("═" * 50 + "\n")