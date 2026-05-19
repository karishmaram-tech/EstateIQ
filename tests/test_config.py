"""
test_config.py — Tests for Configuration Management
=====================================================
Tests that verify config.py correctly reads environment
variables, applies defaults, converts types, and validates.
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config


class TestConfigDefaults:
    """Test that config values have sensible defaults."""

    def test_app_name_has_default(self):
        """APP_NAME should never be empty."""
        assert config.APP_NAME is not None
        assert len(config.APP_NAME) > 0

    def test_app_version_has_default(self):
        """APP_VERSION should follow semantic versioning."""
        assert config.APP_VERSION is not None
        parts = config.APP_VERSION.split(".")
        assert len(parts) >= 2, "Version should have at least major.minor format"

    def test_port_is_integer(self):
        """PORT must be an integer, not a string."""
        assert isinstance(config.PORT, int), \
            f"PORT should be int, got {type(config.PORT)}"

    def test_port_is_valid_range(self):
        """PORT must be in the valid range for network ports."""
        assert 1024 <= config.PORT <= 65535, \
            f"PORT {config.PORT} is outside valid range 1024-65535"

    def test_debug_is_boolean(self):
        """DEBUG must be a boolean, not the string 'False'."""
        assert isinstance(config.DEBUG, bool), \
            f"DEBUG should be bool, got {type(config.DEBUG)}"

    def test_rate_limits_are_integers(self):
        """Rate limit values must be integers for Flask-Limiter."""
        assert isinstance(config.RATE_LIMIT_PER_MINUTE, int)
        assert isinstance(config.RATE_LIMIT_PER_HOUR, int)
        assert isinstance(config.RATE_LIMIT_PER_DAY, int)

    def test_rate_limits_are_positive(self):
        """Rate limits of zero or negative make no sense."""
        assert config.RATE_LIMIT_PER_MINUTE > 0
        assert config.RATE_LIMIT_PER_HOUR > 0
        assert config.RATE_LIMIT_PER_DAY > 0

    def test_rate_limit_hierarchy(self):
        """
        Per-day limit should be greater than per-hour.
        Per-hour should be greater than per-minute.
        """
        assert config.RATE_LIMIT_PER_DAY >= config.RATE_LIMIT_PER_HOUR, \
            "Daily limit should be >= hourly limit"
        assert config.RATE_LIMIT_PER_HOUR >= config.RATE_LIMIT_PER_MINUTE, \
            "Hourly limit should be >= per-minute limit"

    def test_rate_limit_strings_are_formatted_correctly(self):
        """Flask-Limiter expects strings like '30 per minute'."""
        assert "per minute" in config.RATE_LIMIT_PREDICT
        assert "per day" in config.RATE_LIMIT_DEFAULT[0]
        assert "per hour" in config.RATE_LIMIT_DEFAULT[1]

    def test_log_level_is_valid(self):
        """LOG_LEVEL must be a valid Python logging level integer."""
        import logging
        valid_levels = [
            logging.DEBUG, logging.INFO, logging.WARNING,
            logging.ERROR, logging.CRITICAL
        ]
        assert config.LOG_LEVEL in valid_levels, \
            f"LOG_LEVEL {config.LOG_LEVEL} is not a valid logging level"

    def test_model_path_is_string(self):
        """MODEL_PATH must be a non-empty string."""
        assert isinstance(config.MODEL_PATH, str)
        assert len(config.MODEL_PATH) > 0

    def test_model_path_ends_with_pkl(self):
        """MODEL_PATH should point to a pickle file."""
        assert config.MODEL_PATH.endswith(".pkl"), \
            f"MODEL_PATH should end with .pkl, got: {config.MODEL_PATH}"

    def test_secret_key_is_string(self):
        """SECRET_KEY must be a non-empty string."""
        assert isinstance(config.SECRET_KEY, str)
        assert len(config.SECRET_KEY) > 0


class TestGetEnvFunction:
    """Test the get_env helper function in config.py."""

    def test_get_env_returns_default_when_missing(self):
        """When a variable is not set, return the default."""
        result = config.get_env(
            "NONEXISTENT_VARIABLE_XYZ_12345",
            default="my_default"
        )
        assert result == "my_default"

    def test_get_env_reads_set_variable(self):
        """When a variable IS set, return its value."""
        os.environ["TEST_VAR_FOR_ESTATEIQ"] = "hello"
        result = config.get_env("TEST_VAR_FOR_ESTATEIQ", default="ignored")
        assert result == "hello"
        del os.environ["TEST_VAR_FOR_ESTATEIQ"]

    def test_get_env_casts_to_int(self):
        """cast=int should convert string '42' to integer 42."""
        os.environ["TEST_INT_VAR"] = "42"
        result = config.get_env("TEST_INT_VAR", cast=int)
        assert result == 42
        assert isinstance(result, int)
        del os.environ["TEST_INT_VAR"]

    def test_get_env_casts_true_string_to_bool(self):
        """The string 'true' should become Python True."""
        os.environ["TEST_BOOL_VAR"] = "true"
        result = config.get_env("TEST_BOOL_VAR", cast=bool)
        assert result is True
        del os.environ["TEST_BOOL_VAR"]

    def test_get_env_casts_false_string_to_bool(self):
        """
        The string 'False' should become Python False.
        Critical — bool('False') == True in plain Python
        because non-empty strings are truthy.
        get_env must handle this correctly.
        """
        os.environ["TEST_BOOL_VAR"] = "False"
        result = config.get_env("TEST_BOOL_VAR", cast=bool)
        assert result is False
        del os.environ["TEST_BOOL_VAR"]

    def test_get_env_raises_when_required_and_missing(self):
        """required=True should raise EnvironmentError if missing."""
        with pytest.raises(EnvironmentError):
            config.get_env(
                "DEFINITELY_NOT_SET_VAR_XYZ",
                required=True
            )

    def test_get_env_raises_on_invalid_cast(self):
        """Trying to cast 'hello' to int should raise ValueError."""
        os.environ["TEST_BAD_INT"] = "hello"
        with pytest.raises(ValueError):
            config.get_env("TEST_BAD_INT", cast=int)
        del os.environ["TEST_BAD_INT"]


class TestValidateConfig:
    """Test that validate_config catches real misconfigurations."""

    def test_validate_config_returns_list(self):
        """validate_config should always return a list."""
        result = config.validate_config()
        assert isinstance(result, list)

    def test_validate_config_warns_on_default_secret_key(self):
        """
        If SECRET_KEY is the insecure default,
        validate_config should include a warning.
        """
        original = config.SECRET_KEY
        config.SECRET_KEY = "dev-insecure-key-do-not-use-in-production"

        warnings = config.validate_config()
        warning_text = " ".join(warnings).lower()
        assert "secret" in warning_text or "key" in warning_text

        config.SECRET_KEY = original