"""
app/services/validator.py
=========================
Input validation service for property prediction requests.

WHY SEPARATE VALIDATION?
Mixing validation with routing makes both harder to test and
maintain. Isolating it here means:
- You can test validation without making HTTP requests
- You can reuse the same validation in multiple routes
- When validation rules change, there is exactly one place to edit
- The route function stays clean and readable
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ValidationResult:
    """
    Result of validating a prediction request.

    Using a dataclass instead of a plain dict gives you:
    - Type hints so your editor catches mistakes
    - Attribute access instead of string key access
    - Clear documentation of what validation returns
    """
    is_valid:  bool
    errors:    list
    data:      Optional[dict] = None


# ─────────────────────────────────────────────────────────
#  VALIDATION CONSTANTS
#  Defined as constants so they appear in one place.
#  If the business rules change, you update here only.
# ─────────────────────────────────────────────────────────

AREA_MIN           = 100
AREA_MAX           = 20000
BEDROOMS_MIN       = 1
BEDROOMS_MAX       = 20
BATHROOMS_MIN      = 1
BATHROOMS_MAX      = 15
YEAR_BUILT_MIN     = 1800
YEAR_BUILT_MAX     = 2025
LOCATION_MIN       = 1
LOCATION_MAX       = 10
CONDITION_MIN      = 1
CONDITION_MAX      = 10
FLOORS_MIN         = 1
FLOORS_MAX         = 4


def validate_prediction_request(data: dict) -> ValidationResult:
    """
    Validate a prediction request payload.

    Args:
        data: Raw JSON dict from the request

    Returns:
        ValidationResult with is_valid, errors list, and cleaned data

    Usage:
        result = validate_prediction_request(request.get_json())
        if not result.is_valid:
            return jsonify({"errors": result.errors}), 400
        # Use result.data for clean validated values
    """
    if not data:
        return ValidationResult(
            is_valid=False,
            errors=["Request body is empty. Send a JSON object with property details."]
        )

    errors = []

    # ── Area ─────────────────────────────────────────────
    try:
        area = float(data.get("area", 0))
        if area < AREA_MIN or area > AREA_MAX:
            errors.append(
                f"Area must be between {AREA_MIN:,} and {AREA_MAX:,} sq ft. "
                f"Got: {area:,.0f}"
            )
    except (ValueError, TypeError):
        area = 0
        errors.append("Area must be a valid number.")

    # ── Bedrooms ─────────────────────────────────────────
    try:
        bedrooms = int(data.get("bedrooms", 0))
        if bedrooms < BEDROOMS_MIN or bedrooms > BEDROOMS_MAX:
            errors.append(
                f"Bedrooms must be between {BEDROOMS_MIN} and {BEDROOMS_MAX}. "
                f"Got: {bedrooms}"
            )
    except (ValueError, TypeError):
        bedrooms = 0
        errors.append("Bedrooms must be a valid integer.")

    # ── Bathrooms ────────────────────────────────────────
    try:
        bathrooms = int(data.get("bathrooms", 0))
        if bathrooms < BATHROOMS_MIN or bathrooms > BATHROOMS_MAX:
            errors.append(
                f"Bathrooms must be between {BATHROOMS_MIN} and {BATHROOMS_MAX}. "
                f"Got: {bathrooms}"
            )
    except (ValueError, TypeError):
        bathrooms = 0
        errors.append("Bathrooms must be a valid integer.")

    # ── Floors ───────────────────────────────────────────
    try:
        floors = int(data.get("floors", 1))
        if floors < FLOORS_MIN or floors > FLOORS_MAX:
            errors.append(
                f"Floors must be between {FLOORS_MIN} and {FLOORS_MAX}. "
                f"Got: {floors}"
            )
    except (ValueError, TypeError):
        floors = 1
        errors.append("Floors must be a valid integer.")

    # ── Year Built ───────────────────────────────────────
    try:
        year_built = int(data.get("year_built", 2000))
        if year_built < YEAR_BUILT_MIN or year_built > YEAR_BUILT_MAX:
            errors.append(
                f"Year built must be between {YEAR_BUILT_MIN} and {YEAR_BUILT_MAX}. "
                f"Got: {year_built}"
            )
    except (ValueError, TypeError):
        year_built = 2000
        errors.append("Year built must be a valid integer.")

    # ── Location Score ───────────────────────────────────
    try:
        location_score = int(data.get("location_score", 5))
        if location_score < LOCATION_MIN or location_score > LOCATION_MAX:
            errors.append(
                f"Location score must be between {LOCATION_MIN} and {LOCATION_MAX}. "
                f"Got: {location_score}"
            )
    except (ValueError, TypeError):
        location_score = 5
        errors.append("Location score must be a valid integer.")

    # ── Condition ────────────────────────────────────────
    try:
        condition = int(data.get("condition", 5))
        if condition < CONDITION_MIN or condition > CONDITION_MAX:
            errors.append(
                f"Condition must be between {CONDITION_MIN} and {CONDITION_MAX}. "
                f"Got: {condition}"
            )
    except (ValueError, TypeError):
        condition = 5
        errors.append("Condition must be a valid integer.")

    # ── Binary Fields (0 or 1) ───────────────────────────
    binary_fields = {}
    for field in ["garage", "pool", "garden"]:
        try:
            value = int(data.get(field, 0))
            if value not in (0, 1):
                errors.append(f"{field.capitalize()} must be 0 or 1. Got: {value}")
                value = 0
            binary_fields[field] = value
        except (ValueError, TypeError):
            binary_fields[field] = 0
            errors.append(f"{field.capitalize()} must be 0 or 1.")

    # ── Return Result ────────────────────────────────────
    if errors:
        return ValidationResult(is_valid=False, errors=errors)

    cleaned_data = {
    "area":           area,
    "bedrooms":       bedrooms,
    "bathrooms":      bathrooms,
    "floors":         floors,
    "year_built":     year_built,
    "location_score": location_score,
    "condition":      condition,
    "garage":         binary_fields["garage"],
    "pool":           binary_fields["pool"],
    "garden":         binary_fields["garden"],
}

    return ValidationResult(is_valid=True, errors=[], data=cleaned_data)